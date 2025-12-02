from flask import Flask, request
import telegram
import os
import asyncio

# এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন নেওয়া হবে (নিরাপত্তার জন্য)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

app = Flask(__name__)

# বট ইনিশিলাইজ করা
bot = telegram.Bot(token=BOT_TOKEN)

@app.route('/')
def home():
    return "Bot is running on Vercel! 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    # টেলিগ্রাম থেকে আসা ডেটা (JSON) গ্রহণ করা
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    # যদি কোনো টেক্সট মেসেজ আসে
    if update.message and update.message.text:
        chat_id = update.message.chat.id
        text = update.message.text.lower() # ছোট হাতের অক্ষরে রূপান্তর
        
        # মেসেজ পাঠানোর জন্য একটি ছোট্ট async ফাংশন
        async def send_msg(msg):
            await bot.send_message(chat_id=chat_id, text=msg)

        # লজিক (Logic): কোন কমান্ডে কী উত্তর দেবে
        response_text = ""
        
        if text == "/start":
            response_text = (
                "স্বাগতম! 👋 আমি একটি ইনফো বট।\n\n"
                "নিচের কমান্ডগুলো ব্যবহার করুন:\n"
                "🔹 /about - আমাদের সম্পর্কে জানুন\n"
                "🔹 /contact - যোগাযোগ করুন\n"
                "🔹 /services - আমাদের সেবাসমূহ"
            )
        
        elif text == "/about":
            response_text = "আমরা একটি আইটি সল্যুশন কোম্পানি। আমরা গত ৫ বছর ধরে সেবা দিয়ে আসছি।"
            
        elif text == "/contact":
            response_text = "📞 ফোন: +88017XXXXXXXX\n📧 ইমেইল: info@example.com\n📍 ঠিকানা: ঢাকা, বাংলাদেশ।"
            
        elif text == "/services":
            response_text = "আমাদের সেবাসমূহ:\n1. Web Development\n2. Telegram Bot\n3. Graphic Design"
            
        else:
            response_text = "দুঃখিত, আমি এই কমান্ডটি বুঝিনি। /start টাইপ করুন।"

        # মেসেজ পাঠানো (asyncio.run ব্যবহার করে)
        if response_text:
            try:
                asyncio.run(send_msg(response_text))
            except Exception as e:
                print(f"Error: {e}")

    return "ok"

# লোকাল পিসিতে টেস্ট করার জন্য (Vercel এ এটার দরকার নেই)
if __name__ == "__main__":
    app.run(debug=True)
  
