# 🤖 All-in-One Telegram Utility Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)

A powerful, serverless Telegram bot hosted on **Vercel**. This bot provides a wide range of utility tools including Temporary Mail, PDF conversion, QR Code generation, Media processing, and advanced User/Channel Information retrieval.

## 🔥 Features

### 🆔 Advanced Info (Auto Detect)
- **User Info:** Forward any message to get User ID, Name, Username, and Profile Link.
- **Channel/Group Info:** Forward messages from channels/groups to get hidden IDs.
- **File Info:** Send any file (Photo, Video, Audio, Doc) to get detailed metadata (Size, Resolution, Duration, MIME Type).

### 📧 Temporary Mail System
- Generate unlimited temporary emails using `Mail.tm` API.
- Check inbox and read emails directly within the bot.
- Auto-refresh inbox support.

### 🛠 Generator Tools
- **QR Code:** Convert text/link to QR Code image.
- **Password Generator:** Create strong random passwords.
- **Link Shortener:** Shorten long URLs using TinyURL.

### 📂 PDF Tools
- **Image to PDF:** Convert JPG/PNG images to PDF.
- **Text to PDF:** Convert text messages to PDF documents.

### 🖼 & 🗣 Media Tools
- **Text to Speech (TTS):** Convert text to voice (English).
- **Image Resizer:** Resize images by 50%.
- **Grayscale:** Convert colorful images to black & white.

### 📝 Text Tools
- **Base64:** Encode and Decode text.
- **MD5 Hash:** Generate hash from text.
- **Case Converter:** Convert text to UPPERCASE.

---

## 🚀 Deployment Guide (Vercel)

You can deploy this bot for **FREE** on Vercel without any coding knowledge.

### Prerequisites
1. A [Telegram Bot Token](https://t.me/BotFather).
2. A [GitHub Account](https://github.com).
3. A [Vercel Account](https://vercel.com).

### Step 1: Deploy to Vercel
Click the button below to fork this repo and deploy it to Vercel automatically:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FYOUR_GITHUB_USERNAME%2FYOUR_REPO_NAME)

*(Note: Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME` in the link above if you want the button to work directly, or just manually import from Vercel dashboard).*

### Step 2: Configure Environment Variables
During deployment on Vercel, add the following **Environment Variable**:

| Key | Value |
| :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token (Get it from @BotFather) |

### Step 3: Set Webhook
After deployment, Vercel will give you a domain (e.g., `https://my-bot.vercel.app`). You need to connect it to Telegram.

Open your browser and visit:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_VERCEL_URL>/webhook
```

*Replace `<YOUR_BOT_TOKEN>` with your token and `<YOUR_VERCEL_URL>` with your Vercel domain.*

If you see `Webhook was set`, your bot is live! 🎉

---

## 📂 Project Structure
```
.
├── api/
│   └── main.py         # Main bot logic
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel configuration
└── README.md           # Documentation

```
---

## 🛠 Built With

- **Python** - Core language.
- **Flask** - Web framework for webhook handling.
- **Requests** - For making API calls (Telegram, Mail.tm).
- **Pillow (PIL)** - Image processing.
- **gTTS** - Text to Speech.
- **FPDF** - PDF generation.
- **Mail.tm API** - For temporary emails.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
**Developed with ❤️ by [Masud Rana]**
