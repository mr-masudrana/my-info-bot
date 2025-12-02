from flask import Flask, request
import telegram
import os
import asyncio
import json

# এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন
BOT_TOKEN = os.environ.get('BOT_TOKEN')

app = Flask(__name__)
bot = telegram.Bot(token=BOT_TOKEN)

# --- হেল্পার ফাংশন: তথ্য সুন্দর করে সাজানোর জন্য ---
def get_user_profile_link(user_id):
    return f'<a href="tg://user?id={user_id}">{user_id}</a>'

def format_info(data_dict, title="INFO"):
    """যেকোনো ডেটাকে সুন্দর লিস্ট আকারে দেখাবে"""
    text = f"<b>ℹ️ {title}</b>\n\n"
    for key, value in data_dict.items():
        if value:  # যদি ভ্যালু থাকে তবেই দেখাবে
            text += f"<b>🔹 {key}:</b> {value}\n"
    return text

@app.route('/')
def home():
    return "Advanced Info Bot is Running! 🛡️"

@app.route('/webhook', methods=['POST'])
def webhook():
    # আপডেট রিসিভ করা
    try:
        data = request.get_json(force=True)
        update = telegram.Update.de_json(data, bot)
    except Exception as e:
        return "Error parsing update", 400

    # শুধুমাত্র মেসেজ হ্যান্ডেল করব (এডিট বা অন্য কিছু নয়)
    if update.message:
        msg = update.message
        chat_id = msg.chat.id
        
        # রেসপন্স পাঠানোর ফাংশন
        async def send_response(text, reply_to=None):
            try:
                await bot.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    parse_mode='HTML', 
                    reply_to_message_id=reply_to,
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"Error sending message: {e}")

        final_response = ""

        # ১. যদি /start কমান্ড দেয়
        if msg.text and msg.text == "/start":
            user = msg.from_user
            info = {
                "Name": user.full_name,
                "ID": f"<code>{user.id}</code>",
                "Username": f"@{user.username}" if user.username else "N/A",
                "Language": user.language_code,
                "Is Bot": "Yes" if user.is_bot else "No"
            }
            final_response = (
                f"👋 হ্যালো <b>{user.first_name}</b>!\n\n"
                "আমি একটি <b>অ্যাডভান্সড ইনফো বট</b>।\n"
                "আমার কাজ হলো যেকোনো চ্যাট, ইউজার বা চ্যানেলের গোপন তথ্য বের করা।\n\n"
                "🔍 <b>কিভাবে ব্যবহার করবেন?</b>\n"
                "১. যেকোনো মেসেজ আমার কাছে <b>Forward</b> করুন।\n"
                "২. আমি ওই মেসেজের সোর্স, চ্যানেল আইডি বা ইউজার আইডি বলে দেব।\n\n"
                f"{format_info(info, 'YOUR PROFILE')}"
            )

        # ২. যদি কোনো মেসেজ FORWARD করা হয় (সবচেয়ে গুরুত্বপূর্ণ অংশ)
        elif msg.forward_date:
            # ক) চ্যানেল থেকে ফরোয়ার্ড হলে
            if msg.forward_from_chat:
                chat = msg.forward_from_chat
                info = {
                    "Type": chat.type.upper(),  # Channel or Supergroup
                    "Title": chat.title,
                    "ID": f"<code>{chat.id}</code>", # কপি করার জন্য মোনোস্পেস
                    "Username": f"@{chat.username}" if chat.username else "Private/No Username",
                    "Link": f"{chat.invite_link}" if chat.invite_link else None
                }
                final_response = format_info(info, "📢 CHANNEL/GROUP INFO")

            # খ) কোনো ইউজার থেকে ফরোয়ার্ড হলে
            elif msg.forward_from:
                user = msg.forward_from
                info = {
                    "Name": user.full_name,
                    "ID": f"<code>{user.id}</code>",
                    "Username": f"@{user.username}" if user.username else "N/A",
                    "Bot": "Yes" if user.is_bot else "No"
                }
                final_response = format_info(info, "👤 FORWARDED USER INFO")

            # গ) যদি ইউজার প্রাইভেসি দিয়ে রাখে (Hidden Sender)
            elif msg.forward_sender_name:
                final_response = (
                    "<b>🔒 HIDDEN USER DETECTED</b>\n\n"
                    f"<b>🔹 Name:</b> {msg.forward_sender_name}\n"
                    "<i>ব্যবহারকারী তার প্রোফাইল হাইড করে রেখেছেন, তাই ID পাওয়া সম্ভব নয়।</i>"
                )

        # ৩. যদি সাধারণ মেসেজ দেয় (ফরোয়ার্ড না)
        else:
            # এখানে আমরা ইউজারের নিজের তথ্য আবার দেখাবো অথবা মিডিয়া ইনফো দেব
            content_type = "Text"
            if msg.sticker: content_type = "Sticker"
            elif msg.photo: content_type = "Photo"
            elif msg.document: content_type = "Document"
            elif msg.video: content_type = "Video"

            info = {
                "Content Type": content_type,
                "Message ID": msg.message_id,
                "Your ID": f"<code>{msg.from_user.id}</code>",
                "Chat Type": msg.chat.type.capitalize()
            }
            
            # স্টিকার হলে ফাইল আইডি সহ দেখাবো
            if msg.sticker:
                info["Emoji"] = msg.sticker.emoji
                info["File ID"] = f"<code>{msg.sticker.file_id}</code>"

            final_response = format_info(info, "📝 MESSAGE INFO")

        # মেসেজ পাঠানো
        if final_response:
            asyncio.run(send_response(final_response, msg.message_id))

    return "ok"
            
