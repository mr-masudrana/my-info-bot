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
    return "Advanced Info Bot is Live & Stable! 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        # মেসেজ ছাড়া অন্য আপডেট ইগনোর করা হবে (যেমন edited_message)
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
            
            # START COMMAND
            if text == "/start":
                first_name = user.get("first_name", "User")
                response_text = (
                    f"👋 স্বাগতম <b>{first_name}</b>!\n\n"
                    "আমি এখন <b>Advanced Mode</b>-এ আছি। 🛡️\n"
                    "আমার ফিচারসমূহ:\n"
                    "🔹 <b>Forward Info:</b> মেসেজ ফরোয়ার্ড করে সোর্স জানুন।\n"
                    "🔹 <b>Media Info:</b> ফাইলের সাইজ ও ডিটেইলস জানুন।\n"
                    "🔹 <b>JSON Data:</b> <code>/json</code> লিখে রিপ্লাই দিলে Raw ডাটা পাবেন।\n\n"
                    "<i>যেকোনো কিছু ফরোয়ার্ড বা সেন্ড করে টেস্ট করুন!</i>"
                )

            # JSON DUMP (For Developers)
            elif text == "/json":
                # মেসেজটি যদি রিপ্লাই হয়, তবে অরিজিনাল মেসেজের জেসন দেখাবে
                target_msg = msg.get("reply_to_message", msg)
                json_str = json.dumps(target_msg, indent=2)
                # মেসেজ বেশি বড় হলে কেটে ছোট করা হবে
                if len(json_str) > 4000: json_str = json_str[:4000] + "..."
                response_text = f"<pre>{json_str}</pre>"

        # --- ২. ফরোয়ার্ডেড মেসেজ ডিটেকশন ---
        if not response_text and "forward_date" in msg:
            # ক) চ্যানেল বা গ্রুপ থেকে
            if "forward_from_chat" in msg:
                f_chat = msg["forward_from_chat"]
                c_title = f_chat.get("title", "No Title")
                c_username = f"@{f_chat['username']}" if "username" in f_chat else "Private/None"
                c_id = f_chat["id"]
                c_type = f_chat["type"].upper()
                
                response_text = (
                    f"📢 <b>FORWARDED SOURCE</b>\n\n"
                    f"📛 <b>Title:</b> {c_title}\n"
                    f"🆔 <b>ID:</b> <code>{c_id}</code>\n"
                    f"🔗 <b>Username:</b> {c_username}\n"
                    f"📂 <b>Type:</b> {c_type}"
                )
            
            # খ) ইউজার থেকে
            elif "forward_from" in msg:
                f_user = msg["forward_from"]
                u_name = f_user.get("first_name", "")
                u_id = f_user["id"]
                u_user = f"@{f_user['username']}" if "username" in f_user else "None"
                u_bot = "🤖 Yes" if f_user.get("is_bot") else "👤 No"
                u_prem = "🌟 Yes" if f_user.get("is_premium") else "❌ No"
                
                response_text = (
                    f"👤 <b>USER PROFILE (Source)</b>\n\n"
                    f"📛 <b>Name:</b> {u_name}\n"
                    f"🆔 <b>ID:</b> <code>{u_id}</code>\n"
                    f"🔗 <b>Username:</b> {u_user}\n"
                    f"🤖 <b>Bot:</b> {u_bot} | {u_prem}"
                )
            
            # গ) হিডেন ইউজার
            elif "forward_sender_name" in msg:
                response_text = (
                    f"🔒 <b>HIDDEN USER</b>\n\n"
                    f"📛 <b>Name:</b> {msg['forward_sender_name']}\n"
                    "⚠️ <i>ইউজার প্রাইভেসি সেটিংসের কারণে আইডি পাওয়া যায়নি।</i>"
                )

        # --- ৩. মিডিয়া বা ফাইল ইনফো (Advanced) ---
        if not response_text:
            media_type = "Unknown"
            file_id = "N/A"
            file_size = 0
            extra_info = ""

            if "photo" in msg:
                media_type = "🖼 Photo"
                # সবচেয়ে বড় সাইজের ছবিটা নেওয়া হয়
                photo = msg["photo"][-1]
                file_id = photo["file_id"]
                file_size = photo.get("file_size", 0)
                extra_info = f"📏 <b>Res:</b> {photo['width']}x{photo['height']}"

            elif "video" in msg:
                media_type = "📹 Video"
                video = msg["video"]
                file_id = video["file_id"]
                file_size = video.get("file_size", 0)
                duration = video.get("duration", 0)
                extra_info = f"⏱ <b>Duration:</b> {duration}s"

            elif "document" in msg:
                media_type = "📁 Document"
                doc = msg["document"]
                file_id = doc["file_id"]
                file_size = doc.get("file_size", 0)
                mime = doc.get("mime_type", "unknown")
                extra_info = f"📑 <b>Type:</b> {mime}"

            elif "sticker" in msg:
                media_type = "🎭 Sticker"
                sticker = msg["sticker"]
                file_id = sticker["file_id"]
                file_size = sticker.get("file_size", 0)
                emoji = sticker.get("emoji", "N/A")
                is_anim = "Yes" if sticker.get("is_animated") else "No"
                extra_info = f"😀 <b>Emoji:</b> {emoji} | <b>Anim:</b> {is_anim}"

            # যদি কোনো মিডিয়া পাওয়া যায়
            if media_type != "Unknown":
                readable_size = get_readable_size(file_size)
                response_text = (
                    f"💾 <b>MEDIA INFO</b>\n\n"
                    f"🏷 <b>Type:</b> {media_type}\n"
                    f"📦 <b>Size:</b> {readable_size}\n"
                    f"{extra_info}\n"
                    f"🧩 <b>File ID:</b> <code>{file_id}</code>"
                )

        # --- ৪. ডিফল্ট ইউজার ইনফো (যদি উপরের কিছু না হয়) ---
        if not response_text:
            u_id = user.get("id")
            u_name = user.get("first_name", "")
            u_lang = user.get("language_code", "N/A").upper()
            u_prem = "🌟 Yes" if user.get("is_premium") else "❌ No"
            
            response_text = (
                f"ℹ️ <b>YOUR INFO</b>\n\n"
                f"📛 <b>Name:</b> {u_name}\n"
                f"🆔 <b>ID:</b> <code>{u_id}</code>\n"
                f"🌐 <b>Lang:</b> {u_lang}\n"
                f"💎 <b>Premium:</b> {u_prem}\n"
                f"📍 <b>Chat Type:</b> {msg['chat']['type'].title()}"
            )

        # ফাইনাল মেসেজ সেন্ডিং
        if response_text:
            send_message(chat_id, response_text, message_id)

        return "ok", 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error", 200
                
