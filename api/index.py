from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

# কনফিগারেশন
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# --- হেল্পার ফাংশন: ফাইল সাইজ সুন্দর করে দেখানোর জন্য ---
def get_readable_size(size_in_bytes):
    if not size_in_bytes: return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

# --- মেসেজ পাঠানোর ফাংশন ---
def send_message(chat_id, text, reply_to=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/')
def home():
    return "Bot is running with New Design! 🎨"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        if "message" not in data:
            return "ok", 200

        msg = data["message"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]
        user = msg.get("from", {})
        
        response_text = ""

        # --- ১. টেক্সট কমান্ড হ্যান্ডেলিং ---
        if "text" in msg:
            text = msg["text"]
            
            # --- START COMMAND (আপনার চাওয়া ডিজাইন) ---
            if text == "/start":
                # ইউজারের তথ্যগুলো বের করে নেওয়া
                u_id = user.get("id", "N/A")
                first_name = user.get("first_name", "N/A")
                last_name = user.get("last_name", "N/A")
                username = f"@{user.get('username')}" if user.get("username") else "N/A"
                language = user.get("language_code", "N/A").upper()
                is_bot = "Yes" if user.get("is_bot") else "No"
                is_premium = "Yes" if user.get("is_premium") else "No"

                # মেসেজ ফরম্যাট করা
                response_text = (
                    f"👋 হ্যালো <b>{first_name}</b>!\n\n"
                    "আমি একটি অ্যাডভান্সড ইনফো বট।\n"
                    "আমার কাজ হলো যেকোনো চ্যাট, ইউজার বা চ্যানেলের গোপন তথ্য বের করা।\n\n"
                    "👤 <b>YOUR PROFILE:</b>\n\n"
                    f"🆔 <b>ID:</b> <code>{u_id}</code>\n"
                    f"📛 <b>First_Name:</b> {first_name}\n"
                    f"📛 <b>Last_Name:</b> {last_name}\n"
                    f"🔗 <b>Username:</b> {username}\n"
                    f"🌐 <b>Language:</b> {language}\n"
                    f
                
