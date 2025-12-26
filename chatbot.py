import streamlit as st
import google.generativeai as genai
import sqlite3
import smtplib
import random
import re
import requests
import datetime
import uuid
import os
import time
from email.mime.text import MIMEText
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. KONFIGURASI
# ==========================================
MY_API_KEY = "API_anda_sendiri_berisikan_16_karakter"
EMAIL_SENDER = "email_anda_sendiri" 
EMAIL_PASSWORD = "email_password_anda_sendiri" 

# [REVISI HTML TITLE] Menambahkan nama Hanan Eka di Tab Browser
st.set_page_config(
    page_title="NannKA Chatbot by Hanan Eka", 
    page_icon="NK", 
    layout="wide"
)

try:
    genai.configure(api_key=MY_API_KEY)
except:
    st.error("API Key Error.")

if not os.path.exists("temp_files"):
    os.makedirs("temp_files")

# ==========================================
# 2. CSS & UI
# ==========================================
custom_css = """
<style>
    .stDeployButton, .stStatusWidget {display:none !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tombol Telur Asin */
    .stButton > button {
        background-color: #A0D6B4; 
        color: #0d3b28;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #8FC9A3;
        color: black;
    }

    /* Widget Cuaca Detail */
    .weather-widget {
        background: linear-gradient(135deg, #6CA6CD 0%, #A0D6B4 100%);
        padding: 15px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .weather-grid {
        display: flex;
        justify-content: space-around;
        margin-top: 10px;
        font-size: 0.8rem;
    }
    
    /* Footer Hanan Eka */
    .hanan-footer {
        text-align: center;
        color: grey;
        font-size: 0.8rem;
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #e0e0e0;
    }
    
    .justify-text { text-align: justify; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. DATABASE
# ==========================================
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, password TEXT, tier TEXT, 
                  credits INTEGER, last_reset TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT, chat_id TEXT, role TEXT, content TEXT, 
                  file_name TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# --- UTILS ---
def clean_email(email):
    if email: return email.lower().strip()
    return ""

def get_user(email):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    u = conn.cursor().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return u

def create_user(email, password):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    today = datetime.date.today().isoformat()
    try:
        conn.cursor().execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (email, password, 'Free', 20, today))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def update_password(email, new_pass):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    conn.cursor().execute("UPDATE users SET password = ? WHERE email = ?", (new_pass, email))
    conn.commit()
    conn.close()

def update_tier(email, new_tier):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    limit = 40 if new_tier == 'SD' else 80 if new_tier == 'SMP' else 999999 if new_tier == 'SMA' else 20
    conn.cursor().execute("UPDATE users SET tier = ?, credits = ? WHERE email = ?", (new_tier, limit, email))
    conn.commit()
    conn.close()

def check_credits(email):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if user:
        last_reset, tier = user[4], user[2]
        today = datetime.date.today().isoformat()
        if last_reset != today:
            limit = 40 if tier == 'SD' else 80 if tier == 'SMP' else 999999 if tier == 'SMA' else 20
            c.execute("UPDATE users SET credits = ?, last_reset = ? WHERE email = ?", (limit, today, email))
            conn.commit()
            return limit, tier
        conn.close()
        return user[3], tier
    conn.close()
    return 0, 'Guest'

def reduce_credit(email):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits - 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

# --- DB CHAT ---
def save_chat_to_db(email, chat_id, role, content, file_name=None):
    if not email: return
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    ts = datetime.datetime.now()
    conn.cursor().execute("INSERT INTO chats (email, chat_id, role, content, file_name, timestamp) VALUES (?, ?, ?, ?, ?, ?)", 
                          (email, chat_id, role, content, file_name, ts))
    conn.commit()
    conn.close()

def load_chats_from_db(email):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    rows = conn.cursor().execute("SELECT chat_id, role, content, file_name FROM chats WHERE email=? ORDER BY timestamp ASC", (email,)).fetchall()
    conn.close()
    sessions = {}
    titles = {}
    for row in rows:
        cid, role, content, fname = row
        if cid not in sessions:
            sessions[cid] = []
            titles[cid] = "Riwayat"
        msg = {"role": role, "content": content}
        if fname: msg["file_name"] = fname
        sessions[cid].append(msg)
        if role == 'user' and len(sessions[cid]) == 1:
            titles[cid] = " ".join(content.split()[:3]) + "..."
    return sessions, titles

def clear_user_history_db(email):
    email = clean_email(email)
    conn = sqlite3.connect('users.db')
    conn.cursor().execute("DELETE FROM chats WHERE email=?", (email,))
    conn.commit()
    conn.close()

# --- EMAIL ---
def send_otp(target, code):
    target = clean_email(target)
    pengirim = EMAIL_SENDER.strip()
    sandi = EMAIL_PASSWORD.strip()
    msg = MIMEText(f"Kode OTP NannKA: {code}")
    msg['Subject'] = 'Verifikasi'
    msg['From'] = pengirim
    msg['To'] = target
    try:
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(pengirim, sandi)
        s.sendmail(pengirim, target, msg.as_string())
        s.quit()
        return True, "OK"
    except Exception as e: return False, str(e)

# ==========================================
# 4. INISIALISASI & PERSISTENCE
# ==========================================
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "session_titles" not in st.session_state: st.session_state.session_titles = {}
if "current_chat_id" not in st.session_state:
    nid = str(uuid.uuid4())
    st.session_state.current_chat_id = nid
    st.session_state.session_titles[nid] = "Obrolan Baru"
    st.session_state.chat_sessions[nid] = []

def new_chat():
    nid = str(uuid.uuid4())
    st.session_state.chat_sessions[nid] = []
    st.session_state.session_titles[nid] = "Obrolan Baru"
    st.session_state.current_chat_id = nid

def del_chat(cid):
    if cid in st.session_state.chat_sessions:
        del st.session_state.chat_sessions[cid]
        del st.session_state.session_titles[cid]
    if st.session_state.current_chat_id == cid: new_chat()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"
if "guest_credits" not in st.session_state: 
    st.session_state.guest_credits = 3
    st.session_state.guest_date = datetime.date.today().isoformat()

# Anti-Logout Logic
params = st.query_params
if "user" in params and not st.session_state.logged_in:
    saved_email = params["user"]
    if get_user(saved_email):
        st.session_state.logged_in = True
        st.session_state.user_email = saved_email
        db_sessions, db_titles = load_chats_from_db(saved_email)
        if db_sessions:
            st.session_state.chat_sessions = db_sessions
            st.session_state.session_titles = db_titles
            st.session_state.current_chat_id = list(db_sessions.keys())[-1]
        else:
            new_chat()

# ==========================================
# 5. UI SIDEBAR (WEATHER, MENU, BRANDING)
# ==========================================
with st.sidebar:
    # CUACA CIREBON
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-6.7063&longitude=108.5570&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto"
        w = requests.get(url).json()['current']
        temp = w['temperature_2m']
        hum = w['relative_humidity_2m']
        rain = w['precipitation']
        wind = w['wind_speed_10m']
        city = "Cirebon"
    except:
        city, temp, hum, rain, wind = "Cirebon (Offline)", 30, 70, 0, 5

    st.markdown(f"""
    <div class="weather-widget">
        <h2 style='margin:0'>{temp}°C</h2>
        <p style='margin:0; font-weight:bold;'>{city}</p>
        <div class="weather-grid">
            <div>💧 {hum}%</div>
            <div>💨 {wind} km/h</div>
            <div>🌧️ {rain} mm</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Info Akun
    if st.session_state.logged_in:
        c, t = check_credits(st.session_state.user_email)
        st.success(f"Akun: {st.session_state.user_email}")
        st.caption(f"Paket: {t} | Sisa: {'Unlimited' if t=='SMA' else c}")
    else:
        st.info("Status: Tamu (Guest)")
        st.caption(f"Sisa Kredit: {st.session_state.guest_credits}/3")

    st.divider()
    
    # Riwayat
    st.subheader("🗂️ Riwayat")
    if st.button("➕ Chat Baru", use_container_width=True):
        new_chat()
        st.rerun()
    
    for cid in reversed(list(st.session_state.chat_sessions.keys())):
        c1, c2 = st.columns([0.8, 0.2])
        tit = st.session_state.session_titles.get(cid, "Obrolan")
        sty = "primary" if cid == st.session_state.current_chat_id else "secondary"
        if c1.button(tit, key=f"b_{cid}", type=sty, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()
        if c2.button("🗑️", key=f"d_{cid}"):
            del_chat(cid)
            st.rerun()
    
    st.divider()
    with st.expander("⚙️ Pengaturan"):
        peran = st.selectbox("Peran:", ["Guru BK", "Guru Mapel (Umum)", "Teman Santai"])
        if st.button("Hapus Semua History"):
            if st.session_state.logged_in:
                clear_user_history_db(st.session_state.user_email)
            st.session_state.chat_sessions = {}
            st.session_state.session_titles = {}
            new_chat()
            st.rerun()
        
        # LOGOUT
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_email = None
                st.session_state.chat_sessions = {}
                st.session_state.session_titles = {}
                new_chat()
                st.query_params.clear() 
                st.rerun()

    if st.button("💎 Langganan / Price List", use_container_width=True):
        st.session_state.show_pricelist = True

    # [REVISI SIDEBAR BRANDING]
    st.markdown("---")
    st.markdown("""
    <div class="hanan-footer">
        Created with ❤️ by <b>Hanan Eka</b>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. AUTH & PRICELIST
# ==========================================

if "show_pricelist" in st.session_state and st.session_state.show_pricelist:
    st.title("💎 Paket Langganan")
    col1, col2, col3 = st.columns(3)
    sel_plan = None
    with col1:
        st.info("SD (10rb)\n40 Chat")
        if st.button("Beli SD", use_container_width=True): sel_plan = "SD"
    with col2:
        st.warning("SMP (20rb)\n80 Chat")
        if st.button("Beli SMP", use_container_width=True): sel_plan = "SMP"
    with col3:
        st.success("SMA (30rb)\nUNLIMITED")
        if st.button("Beli SMA", use_container_width=True): sel_plan = "SMA"

    if sel_plan:
        if st.session_state.logged_in:
            update_tier(st.session_state.user_email, sel_plan)
            st.success(f"Upgrade Berhasil: {sel_plan}")
            time.sleep(1)
            st.session_state.show_pricelist = False
            st.rerun()
        else: st.error("Login dulu!")

    st.divider()
    cb, ct = st.columns([0.7, 0.3])
    with cb:
        if st.button("❌ Batalkan Langganan"):
            if st.session_state.logged_in:
                update_tier(st.session_state.user_email, 'Free')
                st.info("Kembali ke Free.")
                time.sleep(1)
                st.session_state.show_pricelist = False
                st.rerun()
    with ct:
        if st.button("Tutup"):
            st.session_state.show_pricelist = False
            st.rerun()
    st.stop()

if not st.session_state.logged_in:
    if st.session_state.auth_mode == "login":
        st.subheader("Login Akun")
        le = st.text_input("Email", key="le")
        lp = st.text_input("Password", type="password", key="lp")
        
        if st.button("Lupa Kata Sandi?", type="secondary"):
            st.session_state.auth_mode = "forgot"
            st.rerun()

        if st.button("Masuk", type="primary"):
            u = get_user(le)
            if u and u[1] == lp:
                st.session_state.logged_in = True
                st.session_state.user_email = clean_email(le)
                st.query_params["user"] = clean_email(le)
                
                db_sessions, db_titles = load_chats_from_db(st.session_state.user_email)
                if db_sessions:
                    st.session_state.chat_sessions = db_sessions
                    st.session_state.session_titles = db_titles
                    st.session_state.current_chat_id = list(db_sessions.keys())[-1]
                else: new_chat()
                st.rerun()
            else: st.error("Gagal Login")
        
        if st.button("Daftar Akun Baru"):
            st.session_state.auth_mode = "register"
            st.rerun()

    elif st.session_state.auth_mode == "register":
        st.subheader("Daftar Baru")
        re_mail = st.text_input("Email", key="re")
        rp = st.text_input("Password", type="password", key="rp")
        
        if "otp_val" not in st.session_state: st.session_state.otp_val = None
        if st.button("Kirim OTP"):
            clean_re = clean_email(re_mail)
            if not get_user(clean_re):
                otp = str(random.randint(111111,999999))
                res, msg = send_otp(clean_re, otp)
                if res:
                    st.session_state.otp_val = otp
                    st.session_state.temp_reg = (clean_re, rp)
                    st.success("OTP Terkirim")
                else: st.error(f"Gagal: {msg}")
            else: st.error("Email sudah ada")
        
        rotp = st.text_input("Kode OTP")
        if st.button("Verifikasi & Daftar"):
            if st.session_state.otp_val and rotp == st.session_state.otp_val:
                create_user(st.session_state.temp_reg[0], st.session_state.temp_reg[1])
                st.success("Berhasil")
                st.session_state.auth_mode = "login"
                st.rerun()
            else: st.error("OTP Salah")
        
        if st.button("Kembali"):
            st.session_state.auth_mode = "login"
            st.rerun()

    elif st.session_state.auth_mode == "forgot":
        st.subheader("Reset Kata Sandi")
        fe = st.text_input("Email Terdaftar", key="fe")
        
        if "otp_reset" not in st.session_state: st.session_state.otp_reset = None
        if st.button("Kirim OTP Reset"):
            clean_fe = clean_email(fe)
            if get_user(clean_fe):
                otp = str(random.randint(111111,999999))
                res, msg = send_otp(clean_fe, otp)
                if res:
                    st.session_state.otp_reset = otp
                    st.session_state.temp_email = clean_fe
                    st.success("OTP Reset Terkirim")
                else: st.error(f"Gagal: {msg}")
            else: st.error("Email tidak ditemukan")
        
        fotp = st.text_input("Kode OTP")
        npass = st.text_input("Password Baru", type="password")
        if st.button("Simpan Password Baru"):
            if st.session_state.otp_reset and fotp == st.session_state.otp_reset:
                update_password(st.session_state.temp_email, npass)
                st.success("Password Diubah. Silakan Login.")
                st.session_state.auth_mode = "login"
                st.rerun()
            else: st.error("OTP Salah")
        
        if st.button("Batal"):
            st.session_state.auth_mode = "login"
            st.rerun()
    st.divider()

# ==========================================
# 7. MAIN AREA
# ==========================================
cid = st.session_state.current_chat_id
msgs = st.session_state.chat_sessions[cid]
title = st.session_state.session_titles[cid]

st.title(f"💬 {title}")

role_desc = ""
if peran == "Guru Mapel (Umum)":
    role_desc = "Saya Guru untuk semua mata pelajaran (Matematika, IPA, IPS, Sejarah, dll)."
elif peran == "Guru BK":
    role_desc = "kamu adalah seorang Guru BK yang berbicara dengan siswa SMA, yang dimana kamu memiliki sifat humoris, ramah, tidak menakutkan agar saya tidak takut untuk curhat dan nyaman. gunakan bahasa yang santai menggunakan aku kamu"
else:
    role_desc = "Teman ngobrol santai."
st.caption(f"{role_desc}")

for m in msgs:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.write(m["content"])
            with st.expander("Salin"): st.code(m["content"], language=None)
        else:
            if "file_name" in m: st.info(f"📎 {m['file_name']}")
            st.write(m["content"])

with st.container():
    c1, c2, c3 = st.columns([0.15, 0.25, 0.6])
    with c1:
        st.write("Mic:")
        audio_in = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mic', format="webm")
    with c2:
        st.write("File:")
        file_in = st.file_uploader("Up", type=["png","jpg","pdf"], label_visibility="collapsed")

prompt_text = st.chat_input("Ketik pesan...")

final_prompt = None
upload_data = None
file_disp = None

if audio_in:
    webm_path = os.path.join("temp_files", f"rec_{uuid.uuid4()}.webm")
    with open(webm_path, "wb") as f: f.write(audio_in['bytes'])
    try:
        with st.spinner("Mentranskrip suara..."):
            gf = genai.upload_file(webm_path)
            while gf.state.name == "PROCESSING":
                time.sleep(1)
                gf = genai.get_file(gf.name)
            model_flash = genai.GenerativeModel("models/gemini-2.5-flash")
            res = model_flash.generate_content(["Transkrip audio:", gf])
            final_prompt = res.text
        os.remove(webm_path)
    except Exception as e: st.error(f"Gagal Transkrip: {e}")

if prompt_text: final_prompt = prompt_text
if file_in:
    pth = os.path.join("temp_files", file_in.name)
    with open(pth,"wb") as f: f.write(file_in.getbuffer())
    upload_data = genai.upload_file(pth)
    file_disp = file_in.name

if final_prompt or upload_data:
    allow = False
    if st.session_state.logged_in:
        cr, _ = check_credits(st.session_state.user_email)
        if cr > 0 or cr > 900000: allow = True
    else:
        if st.session_state.guest_credits > 0: allow = True

    if allow:
        msg_content = final_prompt if final_prompt else "Analisis File..."
        st.session_state.chat_sessions[cid].append({"role": "user", "content": msg_content, "file_name": file_disp})
        if st.session_state.logged_in:
            save_chat_to_db(st.session_state.user_email, cid, "user", msg_content, file_disp)
        
        if st.session_state.logged_in:
            if cr < 900000: reduce_credit(st.session_state.user_email)
        else: st.session_state.guest_credits -= 1

        sys_inst = ""
        if peran == "Guru BK": sys_inst = "Guru BK hangat."
        elif peran == "Guru Mapel (Umum)": sys_inst = "Guru Sekolah serba tahu mata pelajaran."
        else: sys_inst = "Teman gaul."

        h_ctx = [{"role": "user" if x["role"]=="user" else "model", "parts": [x["content"]]} for x in msgs if "file_name" not in x]
        
        try:
            with st.spinner("Sedang berpikir..."):
                mod = genai.GenerativeModel("models/gemini-2.5-flash", system_instruction=sys_inst)
                con = []
                if final_prompt: con.append(final_prompt)
                if upload_data: con.append(upload_data)
                
                chat = mod.start_chat(history=h_ctx)
                resp = chat.send_message(con)
                reply = resp.text
            
            st.session_state.chat_sessions[cid].append({"role": "assistant", "content": reply})
            if st.session_state.logged_in:
                save_chat_to_db(st.session_state.user_email, cid, "assistant", reply)
            
            if len(st.session_state.chat_sessions[cid]) <= 2:
                st.session_state.session_titles[cid] = " ".join(msg_content.split()[:3]) + "..."
            
            st.rerun()
        except Exception as e: st.error(f"Error AI: {e}")
    else: st.error("Kredit Habis!")