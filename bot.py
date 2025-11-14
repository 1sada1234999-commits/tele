
import os
import io
import json
from ftplib import FTP_TLS

import telebot
from telebot import types

from config import (
    BOT_TOKEN,
    OWNER_ID,
    CHANNEL_USERNAME,
    FTP_HOST,
    FTP_USER,
    FTP_PASS,
    FTP_DIR,
    SITE_DOMAIN,
)

# تأكد أن BOT_TOKEN موجود
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود. شغّل init_env.py أو ضع التوكن في متغير البيئة BOT_TOKEN.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# حالات للمحادثة
STATE_WAIT_APP_NAME = "WAIT_APP_NAME"
STATE_WAIT_APP_DESC = "WAIT_APP_DESC"
STATE_WAIT_APP_IMAGE = "WAIT_APP_IMAGE"
STATE_WAIT_APP_FILE = "WAIT_APP_FILE"
STATE_WAIT_BROADCAST_TEXT = "WAIT_BROADCAST_TEXT"

user_states = {}
new_post_data = {}

SUBSCRIBERS_FILE = "data/subscribers.json"
os.makedirs("data", exist_ok=True)


def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data)
    except Exception:
        return set()


def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(subs), f)


subscribers = load_subscribers()


# ======= إدارة الحالة =======

def set_state(chat_id, state):
    if state is None:
        user_states.pop(chat_id, None)
    else:
        user_states[chat_id] = state


def get_state(chat_id):
    return user_states.get(chat_id)


def init_new_post(chat_id):
    new_post_data[chat_id] = {
        "name": None,
        "desc": None,
        "image_file_id": None,
        "app_file_id": None,
        "download_url": None,
        "hashtags": None,
    }


def get_new_post(chat_id):
    return new_post_data.get(chat_id)


def upload_to_infinityfree(file_bytes: bytes, remote_filename: str) -> str:
    """
    رفع ملف APK إلى InfinityFree عن طريق FTP (اختياري).
    لو إعدادات FTP غير مضبوطة، ترجع "".
    """
    if not FTP_HOST or not FTP_USER or not FTP_PASS:
        return ""

    ftps = FTP_TLS(FTP_HOST)
    ftps.login(FTP_USER, FTP_PASS)
    ftps.prot_p()  # تشفير الاتصال
    if FTP_DIR:
        ftps.cwd(FTP_DIR)

    bio = io.BytesIO(file_bytes)
    ftps.storbinary(f"STOR {remote_filename}", bio)
    ftps.quit()

    # عدّل المسار حسب مجلد الرفع
    # هنا افترضنا /downloads تحت الـ htdocs
    return f"https://{SITE_DOMAIN}/downloads/{remote_filename}"


def simple_hashtag_generator(app_name: str, description: str) -> str:
    """
    مولّد هاشتاغات بسيط بدون API.
    لو حابب لاحقاً تربطه مع API ذكاء اصطناعي، عدّل هذه الدالة.
    """
    text = f"{app_name} {description}"
    words = text.replace("\\n", " ").split(" ")
    clean = []
    for w in words:
        w = w.strip().lower()
        if not w:
            continue
        if len(w) < 3:
            continue
        for ch in [",", ".", "!", "?", ":", ";", "،", "؛", "«", "»", "“", "”", "\"", "'", "(", ")", "[", "]"]:
            w = w.replace(ch, "")
        if not w:
            continue
        if w not in clean:
            clean.append(w)

    base_tags = ["اندرويد", "apk", "xdownmod", "تطبيقات_مهكرة", "تطبيقات_معدلة"]
    tags = clean[:7] + base_tags
    hashtags = []
    for t in tags:
        t = t.replace(" ", "_")
        if not t.startswith("#"):
            t = "#" + t
        if t not in hashtags:
            hashtags.append(t)

    return " ".join(hashtags[:15])


def is_owner(message_or_call):
    # دعم Message و CallbackQuery
    user = None
    if hasattr(message_or_call, "from_user"):
        user = message_or_call.from_user
    elif hasattr(message_or_call, "message") and hasattr(message_or_call.message, "from_user"):
        user = message_or_call.message.from_user
    return bool(user and user.id == OWNER_ID)


# ======= أوامر عامة =======

@bot.message_handler(commands=["start"])
def cmd_start(message):
    chat_id = message.chat.id

    # حفظ المستخدم كـ "مشترك في البوت" لرسائل البرودكاست
    subscribers.add(chat_id)
    save_subscribers(subscribers)

    if is_owner(message):
        text = (
            "مرحباً 👑\\n"
            "بوت إدارة قناة <b>xdownApk</b> جاهز.\\n"
            "اختر من الأزرار التالية:"
        )
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("📢 منشور جديد", callback_data="new_post"),
        )
        keyboard.add(
            types.InlineKeyboardButton("📨 رسالة جماعية", callback_data="broadcast"),
        )
        keyboard.add(
            types.InlineKeyboardButton("📊 إحصائيات", callback_data="stats"),
        )
        keyboard.add(
            types.InlineKeyboardButton("🌐 معلومات الموقع", callback_data="site_panel"),
        )
        keyboard.add(
            types.InlineKeyboardButton("❓ مساعدة", callback_data="help"),
        )
        bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        text = (
            "أهلاً بك في بوت قناة <b>xdownApk</b> 📱📥\\n\\n"
            "حمّل أحدث التطبيقات والألعاب المعدّلة.\\n\\n"
            "انضم للقناة:\\n"
            f"{CHANNEL_USERNAME}"
        )
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "📲 فتح القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
            )
        )
        bot.send_message(chat_id, text, reply_markup=keyboard)


@bot.message_handler(commands=["help"])
def cmd_help(message):
    text = (
        "📌 أوامر البوت:\\n"
        "/start - القائمة الرئيسية\\n"
        "/help - هذه الرسالة\\n\\n"
        "لوحة التحكم الكاملة موجودة في الأزرار (Inline) للمالك."
    )
    bot.send_message(message.chat.id, text)


# ======= التعامل مع الأزرار (CallbackQuery) =======

@bot.callback_query_handler(func=lambda c: True)
def process_callback(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    data = call.data

    if not is_owner(call):
        bot.answer_callback_query(call.id, "هذه الخيارات خاصة بصاحب البوت.")
        return

    if data == "new_post":
        init_new_post(chat_id)
        set_state(chat_id, STATE_WAIT_APP_NAME)
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📝 أرسل <b>اسم التطبيق</b>:")
    elif data == "broadcast":
        set_state(chat_id, STATE_WAIT_BROADCAST_TEXT)
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "✉️ أرسل النص الذي تريد إرساله لكل من استخدم /start:")
    elif data == "stats":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"👥 عدد المستخدمين المسجّلين: <b>{len(subscribers)}</b>")
    elif data == "site_panel":
        bot.answer_callback_query(call.id)
        text = (
            "🌐 معلومات الموقع:\\n"
            f"دومين: <b>{SITE_DOMAIN}</b>\\n\\n"
            "حالياً الموقع منفصل، لاحقاً ممكن نربط البوت مع لوحة إدارة للموقع."
        )
        bot.send_message(chat_id, text)
    elif data == "help":
        bot.answer_callback_query(call.id)
        cmd_help(call.message)


# ======= خطوات منشور جديد =======

@bot.message_handler(func=lambda m: get_state(m.chat.id) == STATE_WAIT_APP_NAME, content_types=["text"])
def handle_app_name(message):
    chat_id = message.chat.id
    post = get_new_post(chat_id)
    if not post:
        init_new_post(chat_id)
        post = get_new_post(chat_id)

    post["name"] = message.text.strip()
    set_state(chat_id, STATE_WAIT_APP_DESC)
    bot.send_message(chat_id, "🧾 أرسل <b>وصف التطبيق</b> (يمكن عربي + إنجليزي):")


@bot.message_handler(func=lambda m: get_state(m.chat.id) == STATE_WAIT_APP_DESC, content_types=["text"])
def handle_app_desc(message):
    chat_id = message.chat.id
    post = get_new_post(chat_id)
    if not post:
        bot.send_message(chat_id, "حدث خطأ، أعد من جديد بـ /start.")
        set_state(chat_id, None)
        return

    post["desc"] = message.text.strip()
    set_state(chat_id, STATE_WAIT_APP_IMAGE)
    bot.send_message(chat_id, "🖼 أرسل <b>صورة الغلاف / لوجو التطبيق</b>:")


@bot.message_handler(func=lambda m: get_state(m.chat.id) == STATE_WAIT_APP_IMAGE, content_types=["photo"])
def handle_app_image(message):
    chat_id = message.chat.id
    post = get_new_post(chat_id)
    if not post:
        bot.send_message(chat_id, "حدث خطأ، أعد /start.")
        set_state(chat_id, None)
        return

    photo = message.photo[-1]
    post["image_file_id"] = photo.file_id

    set_state(chat_id, STATE_WAIT_APP_FILE)
    bot.send_message(chat_id, "📦 الآن أرسل <b>ملف التطبيق APK</b> كـ Document (ملف).")


@bot.message_handler(func=lambda m: get_state(m.chat.id) == STATE_WAIT_APP_FILE,
                     content_types=["document"])
def handle_app_file(message):
    chat_id = message.chat.id
    if not is_owner(message):
        bot.send_message(chat_id, "هذه الميزة خاصة بصاحب البوت.")
        set_state(chat_id, None)
        return

    post = get_new_post(chat_id)
    if not post:
        bot.send_message(chat_id, "حدث خطأ، أعد /start.")
        set_state(chat_id, None)
        return

    doc = message.document
    post["app_file_id"] = doc.file_id

    # تحميل الملف من تيليجرام
    file_info = bot.get_file(doc.file_id)
    downloaded = bot.download_file(file_info.file_path)

    remote_filename = doc.file_name or f"app_{doc.file_id}.apk"

    bot.send_message(chat_id, "⏫ محاولة رفع الملف إلى الاستضافة (لو إعدادات FTP مضبوطة)...")

    download_url = ""
    try:
        download_url = upload_to_infinityfree(downloaded, remote_filename)
    except Exception as e:
        print("FTP error:", e)
        bot.send_message(chat_id, "⚠️ تعذّر الرفع إلى الاستضافة، سيتم استخدام رابط مباشر من تيليجرام.")

    if not download_url:
        # fallback: رابط من تيليجرام (مش دائماً دائم، لكن حل مؤقت)
        file_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        download_url = file_link

    post["download_url"] = download_url

    # هاشتاغات
    hashtags = simple_hashtag_generator(post["name"], post["desc"])
    post["hashtags"] = hashtags

    caption = (
        f"📱 <b>{post['name']}</b>\\n\\n"
        f"{post['desc']}\\n\\n"
        f"⬇️ تحميل مباشر:\\n{post['download_url']}\\n\\n"
        f"{post['hashtags']}\\n\\n"
        f"🔰 قناة التطبيقات:\\n{CHANNEL_USERNAME}"
    )

    bot.send_message(chat_id, "✅ تم تجهيز المنشور، سيتم نشره الآن في القناة...")

    try:
        bot.send_photo(
            CHANNEL_USERNAME,
            photo=post["image_file_id"],
            caption=caption,
        )
        bot.send_message(chat_id, "🎉 تم نشر المنشور بنجاح في القناة!")
    except Exception as e:
        print("Publish error:", e)
        bot.send_message(chat_id, "⚠️ خطأ أثناء النشر، تأكد أن البوت مشرف في القناة.")

    set_state(chat_id, None)
    new_post_data.pop(chat_id, None)


# ======= رسالة جماعية (Broadcast) =======

@bot.message_handler(func=lambda m: get_state(m.chat.id) == STATE_WAIT_BROADCAST_TEXT, content_types=["text"])
def handle_broadcast_text(message):
    chat_id = message.chat.id
    if not is_owner(message):
        bot.send_message(chat_id, "هذه الميزة خاصة بالمالك فقط.")
        set_state(chat_id, None)
        return

    text = message.text
    set_state(chat_id, None)

    bot.send_message(chat_id, f"🚀 جاري إرسال الرسالة إلى {len(subscribers)} مستخدم تقريباً...")

    sent = 0
    for uid in list(subscribers):
        try:
            bot.send_message(uid, text)
            sent += 1
        except Exception:
            continue

    bot.send_message(chat_id, f"✅ تم الإرسال إلى {sent} مستخدم.")


print("Bot is running...")
bot.infinity_polling()
