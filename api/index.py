from flask import Flask, request
import os
import requests

app = Flask(__name__)

# টোকেন এনভায়রনমেন্ট থেকে নেওয়া
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# টেলিগ্রাম এপিআই বেস URL
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text, reply_to=None):
    """মেসেজ পাঠানোর ফাংশন (Synchronous)"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    
    # সরাসরি রিকোয়েস্ট পাঠানো (কোনো async ঝামেলা নেই)
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/')
def home():
    return "Bot is running perfectly! 🟢"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # টেলিগ্রাম থেকে আসা ডেটা (JSON)
        data = request.get_json(force=True)
        
        # ডিবাগিং: লগ চেক করার জন্য
        # print(data)

        # মেসেজ আছে কিনা চেক করা
        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            message_id = msg["message_id"]
            
            response_text = ""

            # ১. টেক্সট লজিক (/start)
            if "text" in msg:
                text = msg["text"]
                if text == "/start":
                    user_first_name = msg["from"]["first_name"]
                    response_text = (
                        f"👋 হ্যালো <b>{user_first_name}</b>!\n\n"
                        "আমি এখন সম্পূর্ণ স্ট্যাবল (Stable) মোডে চলছি।\n"
                        "কোনো মেসেজ ফরোয়ার্ড করুন, আমি ডিটেইলস দেব।"
                    )
            
            # ২. ফরোয়ার্ড করা মেসেজ হ্যান্ডেলিং
            if "forward_date" in msg:
                # ক) চ্যানেল থেকে
                if "forward_from_chat" in msg:
                    f_chat = msg["forward_from_chat"]
                    title = f_chat.get("title", "No Title")
                    username = f"@{f_chat['username']}" if "username" in f_chat else "Private"
                    c_id = f_chat["id"]
                    
                    response_text = (
                        f"📢 <b>CHANNEL INFO</b>\n\n"
                        f"🔹 <b>Title:</b> {title}\n"
                        f"🔹 <b>ID:</b> <code>{c_id}</code>\n"
                        f"🔹 <b>Username:</b> {username}"
                    )
                
                # খ) ইউজার থেকে
                elif "forward_from" in msg:
                    f_user = msg["forward_from"]
                    name = f_user.get("first_name", "")
                    u_id = f_user["id"]
                    
                    response_text = (
                        f"👤 <b>USER INFO</b>\n\n"
                        f"🔹 <b>Name:</b> {name}\n"
                        f"🔹 <b>ID:</b> <code>{u_id}</code>"
                    )
                
                # গ) গোপন ইউজার (Hidden User)
                elif "forward_sender_name" in msg:
                    sender_name = msg["forward_sender_name"]
                    response_text = (
                        f"🔒 <b>HIDDEN USER</b>\n\n"
                        f"🔹 <b>Name:</b> {sender_name}\n"
                        "<i>ID পাওয়া যায়নি (প্রাইভেসি অন)।</i>"
                    )

            # ৩. সাধারণ মেসেজ (যদি উপরের কোনোটি না হয় এবং রেসপন্স খালি থাকে)
            if not response_text:
                # ইউজারের নিজের আইডি দেখানো
                user_id = msg["from"]["id"]
                chat_type = msg["chat"]["type"].capitalize()
                
                content_type = "Text"
                if "sticker" in msg: content_type = "Sticker"
                elif "photo" in msg: content_type = "Photo"
                elif "video" in msg: content_type = "Video"
                
                response_text = (
                    f"📝 <b>MESSAGE INFO</b>\n\n"
                    f"🔹 <b>Type:</b> {content_type}\n"
                    f"🔹 <b>Your ID:</b> <code>{user_id}</code>\n"
                    f"🔹 <b>Chat Type:</b> {chat_type}"
                )

            # মেসেজ পাঠানো
            if response_text:
                send_message(chat_id, response_text, message_id)

        return "ok", 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error", 200
        
