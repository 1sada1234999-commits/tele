
import os

TEMPLATE = """BOT_TOKEN={token}
OWNER_ID={owner_id}

FTP_HOST={ftp_host}
FTP_USER={ftp_user}
FTP_PASS={ftp_pass}
FTP_DIR={ftp_dir}

SITE_DOMAIN={site_domain}
"""

def main():
    print("إعداد ملف .env للبوت xdownmod")
    token = input("أدخل توكن البوت من BotFather: ").strip()
    if not token:
        print("لا يمكن ترك التوكن فارغاً.")
        return

    owner_id = input("أدخل آيدي المالك (اتركه فارغاً لاستخدام الافتراضي 6355443493): ").strip()
    if not owner_id:
        owner_id = "6355443493"

    ftp_host = input("FTP_HOST (يمكن تركه فارغاً لو لن تستخدم الرفع التلقائي): ").strip()
    ftp_user = input("FTP_USER: ").strip()
    ftp_pass = input("FTP_PASS: ").strip()
    ftp_dir  = input("FTP_DIR (افتراضي: /htdocs/downloads): ").strip() or "/htdocs/downloads"

    site_domain = input("SITE_DOMAIN (افتراضي: xdownmod.com): ").strip() or "xdownmod.com"

    content = TEMPLATE.format(
        token=token,
        owner_id=owner_id,
        ftp_host=ftp_host,
        ftp_user=ftp_user,
        ftp_pass=ftp_pass,
        ftp_dir=ftp_dir,
        site_domain=site_domain,
    )

    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ تم إنشاء ملف .env بنجاح. الآن يمكنك تشغيل البوت باستخدام:")
    print("python bot.py")

if __name__ == "__main__":
    main()
