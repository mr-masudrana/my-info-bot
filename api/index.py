from flask import Flask, request
import telegram
from telegram.constants import ParseMode
import os
import asyncio

# এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন
BOT_TOKEN = os.environ.get('BOT_TOKEN')

app = Flask(__name__)
bot = telegram.Bot(token=BOT_TOKEN)

# ফাস্ট রেসপন্সের জন্য একটি হেল্পার ফাংশন
async def send_reply(chat_id, text, message_id=None):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML, # টেক্সট বোল্ড/ইটালিক করার জন্য
            reply_to_message_id=message_id
        )
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/')
def home():
    return "Advanced Info Bot is Running! 🕵️‍♂️"

@app.route('/webhook', methods=['POST'])
def webhook():
    # আপডেট রিসিভ করা
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
    except Exception:
        return "error"

    # শুধু মেসেজ হ্যান্ডেল করব
    if update.message:
        asyncio.run(handle_message(update))
        
    return "ok"

async def handle_message(update):
    msg = update.message
    text = msg.text
    chat_id = msg.chat.id
    
    if not text:
        return

    # ১. ইউজার ইনফো (/myinfo অথবা রিপ্লাই দিয়ে /info)
    if text == "/myinfo" or (text == "/info" and msg.reply_to_message):
        
        # যদি রিপ্লাই দেওয়া হয়, তাহলে যার মেসেজে রিপ্লাই দেওয়া হয়েছে তার তথ্য, 
        # নাহলে যে কমান্ড দিয়েছে তার তথ্য।
        target_user = msg.reply_to_message.from_user if msg.reply_to_message else msg.from_user
        
        user_info = (
            f"👤 <b>User Information</b>\n\n"
            f"🆔 <b>ID:</b> <code>{target_user.id}</code>\n"
            f"📛 <b>First Name:</b> {target_user.first_name}\n"
            f"📛 <b>Last Name:</b> {target_user.last_name if target_user.last_name else 'N/A'}\n"
            f"👤 <b>Username:</b> @{target_user.username if target_user.username else 'None'}\n"
            f"🌐 <b>Language:</b> {target_user.language_code}\n"
            f"🤖 <b>Is Bot:</b> {'Yes' if target_user.is_bot else 'No'}\n"
            f"🌟 <b>Premium:</b> {'Yes' if target_user.is_premium else 'No'}"
        )
        await send_reply(chat_id, user_info, msg.message_id)

    # ২. চ্যাট/গ্রুপ/চ্যানেল ইনফো (/chatinfo)
    elif text == "/chatinfo":
        chat = msg.chat
        chat_info = (
            f"📢 <b>Chat Information</b>\n\n"
            f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"
            f"📌 <b>Title:</b> {chat.title if chat.title else 'Private Chat'}\n"
            f"🏷 <b>Type:</b> {chat.type.upper()}\n"
            f"🔗 <b>Username:</b> @{chat.username if chat.username else 'Private/None'}"
        )
        await send_reply(chat_id, chat_info, msg.message_id)

    # ৩. বট ইনফো (/botinfo)
    elif text == "/botinfo":
        me = await bot.get_me()
        bot_details = (
            f"🤖 <b>Bot Information</b>\n\n"
            f"🆔 <b>ID:</b> <code>{me.id}</code>\n"
            f"📛 <b>Name:</b> {me.first_name}\n"
            f"🔗 <b>Username:</b> @{me.username}\n"
            f"💻 <b>Hosted on:</b> Vercel (Webhook Mode)"
        )
        await send_reply(chat_id, bot_details, msg.message_id)

    # ৪. স্টার্ট মেসেজ
    elif text == "/start":
        welcome_text = (
            "👋 <b>স্বাগতম! আমি একটি অ্যাডভান্সড ইনফো বট।</b>\n\n"
            "নিচের কমান্ডগুলো ব্যবহার করুন:\n"
            "🔹 /myinfo - আপনার নিজের তথ্য দেখুন\n"
            "🔹 /chatinfo - বর্তমান গ্রুপ বা চ্যানেলের তথ্য দেখুন\n"
            "🔹 /botinfo - আমার সম্পর্কে জানুন\n\n"
            "💡 <b>টিপস:</b> কারো তথ্যের জন্য তার মেসেজে রিপ্লাই দিয়ে <code>/info</code> লিখুন।"
        )
        await send_reply(chat_id, welcome_text, msg.message_id)

if __name__ == "__main__":
    app.run(debug=True)
        
