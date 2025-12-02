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
                    f"🤖 <b>Is Bot:</b> {is_bot}\n"
                    f"🌟 <b>Premium:</b> {is_premium}"
                )

            # JSON DUMP
            elif text == "/json":
                target_msg = msg.get("reply_to_message", msg)
                json_str = json.dumps(target_msg, indent=2)
                if len(json_str) > 4000: json_str = json_str[:4000] + "..."
                response_text = f"<pre>{json_str}</pre>"

        # --- ২. ফরোয়ার্ডেড মেসেজ ডিটেকশন ---
        if not response_text and "forward_date" in msg:
            if "forward_from_chat" in msg:
                f_chat = msg["forward_from_chat"]
                c_title = f_chat.get("title", "No Title")
                c_username = f"@{f_chat['username']}" if "username" in f_chat else "Private"
                c_id = f_chat["id"]
                
                response_text = (
                    f"📢 <b>CHANNEL SOURCE</b>\n\n"
                    f"📛 <b>Title:</b> {c_title}\n"
                    f"🆔 <b>ID:</b> <code>{c_id}</code>\n"
                    f"🔗 <b>Username:</b> {c_username}"
                )
            
            elif "forward_from" in msg:
                f_user = msg["forward_from"]
                u_name = f_user.get("first_name", "")
                u_id = f_user["id"]
                u_user = f"@{f_user['username']}" if "username" in f_user else "None"
                
                response_text = (
                    f"👤 <b>USER SOURCE</b>\n\n"
                    f"📛 <b>Name:</b> {u_name}\n"
                    f"🆔 <b>ID:</b> <code>{u_id}</code>\n"
                    f"🔗 <b>Username:</b> {u_user}"
                )
            
            elif "forward_sender_name" in msg:
                response_text = (
                    f"🔒 <b>HIDDEN USER</b>\n\n"
                    f"📛 <b>Name:</b> {msg['forward_sender_name']}\n"
                    "⚠️ <i>ID পাওয়া সম্ভব নয়।</i>"
                )

        # --- ৩. মিডিয়া ইনফো ---
        if not response_text:
            media_type = "Unknown"
            file_id = "N/A"
            file_size = 0
            
            if "photo" in msg:
                media_type = "Photo"
                photo = msg["photo"][-1]
                file_id = photo["file_id"]
                file_size = photo.get("file_size", 0)
            elif "video" in msg:
                media_type = "Video"
                video = msg["video"]
                file_id = video["file_id"]
                file_size = video.get("file_size", 0)
            elif "document" in msg:
                media_type = "Document"
                doc = msg["document"]
                file_id = doc["file_id"]
                file_size = doc.get("file_size", 0)
            elif "sticker" in msg:
                media_type = "Sticker"
                sticker = msg["sticker"]
                file_id = sticker["file_id"]
                file_size = sticker.get("file_size", 0)

            if media_type != "Unknown":
                readable_size = get_readable_size(file_size)
                response_text = (
                    f"💾 <b>MEDIA INFO</b>\n\n"
                    f"🏷 <b>Type:</b> {media_type}\n"
                    f"📦 <b>Size:</b> {readable_size}\n"
                    f"🧩 <b>File ID:</b> <code>{file_id}</code>"
                )

        # মেসেজ না থাকলে (যেমন শুধু টেক্সট পাঠিয়েছে কিন্তু /start না) ডিফল্ট ইনফো
        if not response_text and "text" in msg:
             # এখানে চাইলে সাধারণ মেসেজের রিপ্লাই দিতে পারেন, 
             # অথবা কিছুই না দিলে ইউজার কিছু পাবে না।
             pass 

        if response_text:
            send_message(chat_id, response_text, message_id)

        return "ok", 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error", 200
                
