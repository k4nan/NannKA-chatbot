import smtplib
from email.mime.text import MIMEText

# ==========================================
# ISI DATA INI DENGAN TELITI
# ==========================================

# 1. Ini Email YANG MENGIRIM OTP (Email Bot)
# Harus email yang sama tempat Anda membuat App Password tadi!
EMAIL_PENGIRIM = "lillnann92@gmail.com"  

# 2. Ini App Password 16 Digit milik email di atas
# Hapus spasi jika ada. Contoh: "abcdefghijklmnop"
PASSWORD_APP = "phxyomhiwnyxwczk" 

# 3. Ini Email penerima (Boleh email Anda sendiri untuk ngetes)
EMAIL_TUJUAN = "syech.hannan@gmail.com"

# ==========================================

print("Sedang mencoba login ke Google...")

try:
    # Koneksi ke Server Google
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    
    # Mencoba Login
    server.login(EMAIL_PENGIRIM, PASSWORD_APP)
    print("✅ LOGIN BERHASIL! Password benar.")
    
    # Mencoba Kirim
    msg = MIMEText("Halo, ini tes koneksi sukses!")
    msg['Subject'] = 'Tes Python'
    msg['From'] = EMAIL_PENGIRIM
    msg['To'] = EMAIL_TUJUAN
    
    server.sendmail(EMAIL_PENGIRIM, EMAIL_TUJUAN, msg.as_string())
    server.quit()
    print("✅ EMAIL TERKIRIM! Cek inbox penerima.")

except Exception as e:
    print("\n❌ GAGAL LOGIN!")
    print("Penyebab:", e)
    print("\nSOLUSI:")
    print("1. Cek apakah EMAIL_PENGIRIM sudah benar (jangan typo).")
    print("2. Cek apakah PASSWORD_APP sudah benar 16 digit.")
    print("3. Pastikan App Password itu dibuat DARI DALAM akun email pengirim tersebut.")