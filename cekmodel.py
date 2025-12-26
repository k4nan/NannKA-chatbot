import google.generativeai as genai

# Ganti TULISAN_INI dengan API Key asli Anda
API_KEY = "isi_API_anda_dengan_16_karakter" 

genai.configure(api_key=API_KEY)

print("Mencari model yang tersedia...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
    
MY_API_KEY = "isi_API_anda_dengan_16_karakter"
EMAIL_SENDER = "email_anda" # Email Bot (Pengirim)
EMAIL_PASSWORD = "sandi_email_anda" # App Password Gmail Bot