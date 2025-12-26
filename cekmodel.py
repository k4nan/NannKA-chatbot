import google.generativeai as genai

# Ganti TULISAN_INI dengan API Key asli Anda
API_KEY = "AIzaSyDxsfwhQTiy8MRYCtBzan1VZwT3HcGXwMo" 

genai.configure(api_key=API_KEY)

print("Mencari model yang tersedia...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
    
MY_API_KEY = "AIzaSyDxsfwhQTiy8MRYCtBzan1VZwT3HcGXwMo"
EMAIL_SENDER = "lillnann92@gmail.com" # Email Bot (Pengirim)
EMAIL_PASSWORD = "vkufjfoeipiolspr" # App Password Gmail Bot