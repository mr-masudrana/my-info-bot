from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

# কনফিগারেশন
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
    return "Bot is running with Custom Format! 🎨"

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

        # --- ১. টেক্সট হ্যান্ডেলিং ---
        if "text" in msg:
            text = msg["text"]
            
            # --- START COMMAND ---
            if text == "/start":
                # নাম সাজানো (First Name + Last Name)
                fname = user.get("first_name", "")
                lname = user.get("last_name", "")
                full_name = f"{fname} {lname}".strip()
                
                u_id = user.get("id", "N/A")
                username = f"@{user.get('username')}" if user.get("username") else "None"

                response_text = (
                    f"👋 হ্যালো <b>{fname}</b>!\n\n"
                    "আমি একটি অ্যাডভান্সড ইনফো বট।\n"
                    "আমার কাজ হলো যেকোনো চ্যাট, ইউজার বা চ্যানেলের গোপন তথ্য বের করা।\n\n"
                    "👤 <b>YOUR PROFILE:</b>\n\n"
                    f"🆔 <b>ID:</b> <code>{u_id}</code>\n"
                    f"📛 <b>Name:</b> {full_name}\n"
                    f"🔗 <b>Username:</b> {username}"
                )

        # --- ২. ফরোয়ার্ডেড মেসেজ ডিটেকশন ---
        if not response_text and "forward_date" in msg:
            
            # ক) চ্যানেল থেকে ফরোয়ার্ড হলে
            if "forward_from_chat" in msg:
                f_chat = msg["forward_from_chat"]
                c_title = f_chat.get("title", "No Title")
                c_username = f"@{f_chat['username']}" if "username" in f_chat else "None"
                c_id = f_chat["id"]
                
                response_text = (
                    "📢 <b>CHANNEL SOURCE</b>\n\n"
                    f"🆔 <b>ID:</b> <code>{c_id}</code>\n"
                    f"📛 <b>Name:</b> {c_title}\n"
                    f"🔗 <b>Username:</b> {c_username}"
                )
            
            # খ) ইউজার বা অন্য বট থেকে ফরোয়ার্ড হলে
            elif "forward_from" in msg:
                f_user = msg["forward_from"]
                
                # নাম সাজানো
                fname = f_user.get("first_name", "")
                lname = f_user.get("last_name", "")
                full_name = f"{fname} {lname}".strip()
                
                u_id = f_user["id"]
                u_user = f"@{f_user['username']}" if "username" in f_user else "None"
                
                # চেক করা এটা বট নাকি মানুষ
                if f_user.get("is_bot"):
                    header = "🤖 <b>BOT SOURCE</b>"
                else:
                    header = "👤 <b>USER SOURCE</b>"
                
                response_text = (
                    f"{header}\n\n"
                    f"🆔 <b>ID:</b> <code>{u_id}</code>\n"
                    f"📛 <b>Name:</b> {full_name}\n"
                    f"🔗 <b>Username:</b> {u_user}"
                )
            
            # গ) হিডেন ইউজার (যাদের প্রোফাইলে ফরওয়ার্ড রেস্ট্রিকশন আছে)
            elif "forward_sender_name" in msg:
                response_text = (
                    "🔒 <b>HIDDEN USER</b>\n\n"
                    f"📛 <b>Name:</b> {msg['forward_sender_name']}\n"
                    "⚠️ <i>ID পাওয়া সম্ভব নয় (Privacy On)।</i>"
                )

        # --- ৩. মিডিয়া ইনফো (ছবি/ভিডিওর সাইজ দেখানোর জন্য - ঐচ্ছিক) ---
        # আপনি যদি শুধু টেক্সট চান তবে এই অংশটুকু বাদ দিতে পারেন, 
        # তবে এটি রাখলে কেউ ছবি দিলেও ইনফো পাবে।
        if not response_text:
            file_type = None
            if "photo" in msg: file_type = "Photo"
            elif "video" in msg: file_type = "Video"
            elif "document" in msg: file_type = "Document"
            
            if file_type:
                 u_id = user.get("id")
                 response_text = (
                    f"📝 <b>MEDIA INFO</b>\n\n"
                    f"📂 <b>Type:</b> {file_type}\n"
                    f"🆔 <b>Your ID:</b> <code>{u_id}</code>"
                 )

        # মেসেজ পাঠানো
        if response_text:
            send_message(chat_id, response_text, message_id)

        return "ok", 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error", 200
        
