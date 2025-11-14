
import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env لو موجود
load_dotenv()

# توكن البوت (لا تكتبه هنا مباشرة، خليه في متغير بيئة أو ملف .env)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# آيدي المالك (يمكن تغييره من .env)
OWNER_ID = int(os.getenv("OWNER_ID", "6355443493"))

# يوزر القناة
CHANNEL_USERNAME = "@xdownApk"

# إعدادات استضافة InfinityFree / FTP – عدّلها لو حابب تستخدم الرفع التلقائي
FTP_HOST = os.getenv("FTP_HOST", "")      # مثلاً: ftpupload.net
FTP_USER = os.getenv("FTP_USER", "")      # epiz_XXXXXXX
FTP_PASS = os.getenv("FTP_PASS", "")      # كلمة مرور FTP
FTP_DIR  = os.getenv("FTP_DIR", "/htdocs/downloads")  # مجلد الرفع داخل الاستضافة

# دومين الموقع
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "xdownmod.com")
