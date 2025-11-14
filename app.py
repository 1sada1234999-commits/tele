import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
ADMIN_ID = os.environ.get("ADMIN_ID")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

SESSIONS = {}

def send(chat, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat, "text": text})

def send_photo(chat, file_id, caption):
    requests.post(f"{API}/sendPhoto", json={"chat_id": chat, "photo": file_id, "caption": caption})

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update or "message" not in update:
        return "ok"

    msg = update["message"]
    chat = msg["chat"]["id"]
    text = msg.get("text")
    photos = msg.get("photo")

    # فقط الإدارة
    if str(chat) != str(ADMIN_ID):
        send(chat, "❌ غير مصرح لك باستخدام هذا البوت.")
        return "ok"

    if chat not in SESSIONS:
        SESSIONS[chat] = {"step": None, "data": {}}

    session = SESSIONS[chat]

    if text == "/start":
        session["step"] = None
        session["data"] = {}
        send(chat, "مرحباً! ارسل /newapp لرفع تطبيق جديد.")
        return "ok"

    if text == "/newapp":
        session["step"] = "name"
        send(chat, "📌 ارسل اسم التطبيق:")
        return "ok"

    step = session["step"]

    if step == "name" and text:
        session["data"]["name"] = text
        session["step"] = "desc"
        send(chat, "📝 ارسل وصف التطبيق:")
        return "ok"

    if step == "desc" and text:
        session["data"]["desc"] = text
        session["step"] = "features"
        send(chat, "✨ ارسل المميزات:")
        return "ok"

    if step == "features" and text:
        session["data"]["features"] = text
        session["step"] = "modded"
        send(chat, "🔧 هل التطبيق معدل؟ نعم / لا")
        return "ok"

    if step == "modded" and text:
        t = text.strip().lower()
        session["data"]["modded"] = "معدل ✅" if "نعم" in t else "غير معدل ❌"
        session["step"] = "photo"
        send(chat, "📸 ارسل صورة التطبيق:")
        return "ok"

    if step == "photo" and photos:
        file_id = photos[-1]["file_id"]
        data = session["data"]

        caption = f"""📱 {data['name']}

🧩 الحالة: {data['modded']}

⭐ المميزات:
{data['features']}

📜 الوصف:
{data['desc']}
"""

        send_photo(CHANNEL_ID, file_id, caption)
        send(chat, "✅ تم نشر التطبيق بنجاح!")
        session["step"] = None
        session["data"] = {}
        return "ok"

    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Xdownmod Telegram Bot Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
