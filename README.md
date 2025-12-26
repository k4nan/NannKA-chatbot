# 🤖 NannKA Chatbot

**NannKA Chatbot** adalah asisten AI cerdas berbasis Web yang dibangun menggunakan **Python (Streamlit)** dan **Google Gemini AI**. Proyek ini dikembangkan oleh **Hanan Eka**.

Chatbot ini memiliki fitur autentikasi lengkap, tingkatan membership, pengenalan suara, analisis gambar, dan widget cuaca real-time.

[tampilan chatbot](https://drive.google.com/file/d/16MiVu5a5x0KOLO7B-cu_5nOhOkPsXLT3/view?usp=sharing)

## ✨ Fitur Unggulan

* **🧠 Multi-Peran AI:** Bisa berperan sebagai Guru BK (Psikologis), Guru Mapel Umum, atau Teman Santai.
* **🔐 Sistem Autentikasi:** Login, Register, dan Lupa Password menggunakan **OTP Email (Gmail SMTP)**.
* **💎 Sistem Membership:** Tiering akun (Guest, SD, SMP, SMA/Unlimited) dengan batasan kuota chat harian.
* **🎙️ Interaksi Multimedia:** Mendukung input **Suara (Voice-to-Text)** dan **Upload Gambar/Dokumen**.
* **☁️ Widget Cuaca Real-time:** Menampilkan suhu, kelembapan, dan curah hujan khusus kota **Cirebon** (via Open-Meteo API).
* **💾 Database Persisten:** Riwayat chat tersimpan permanen untuk member menggunakan **SQLite**.

## 🛠️ Teknologi yang Digunakan

* **Bahasa:** Python 3.x
* **Framework UI:** Streamlit
* **AI Core:** Google Gemini 1.5 Flash
* **Database:** SQLite3
* **Fitur Lain:** `smtplib` (Email), `mic-recorder` (Audio), `requests` (API Cuaca).

## 🚀 Cara Menjalankan (Instalasi)

1.  **Clone Repository ini**
    ```bash
    git clone [https://github.com/USERNAME_ANDA/nannka-chatbot.git](https://github.com/USERNAME_ANDA/nannka-chatbot.git)
    cd nannka-chatbot
    ```

2.  **Buat Virtual Environment (Opsional tapi Disarankan)**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Install Library**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi API Key**
    Buka file `chatbot.py` dan isi variabel berikut dengan data Anda:
    ```python
    MY_API_KEY = "API_KEY_GEMINI_ANDA"
    EMAIL_SENDER = "email_bot@gmail.com"
    EMAIL_PASSWORD = "app_password_16_digit"
    ```

5.  **Jalankan Aplikasi**
    ```bash
    streamlit run chatbot.py
    ```

## 👨‍💻 Author

**Hanan Eka**
* Project: Magang / Portofolio Python AI

---
*Created with ❤️ by Hanan Eka*