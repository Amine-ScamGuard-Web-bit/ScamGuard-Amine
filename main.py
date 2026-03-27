import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading
import logging

# إعداد السجلات لمراقبة الأخطاء بدقة
logging.basicConfig(level=logging.INFO)

# 🔑 التحقق من مفتاح API قبل التشغيل
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("FATAL: GEMINI_API_KEY is missing in environment variables.")

genai.configure(api_key=API_KEY)

# استخدام أحدث موديل مستقر ومساند
MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

def main(page: ft.Page):
    page.title = "ScamGuard AI Pro - Enterprise Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30
    page.spacing = 20

    # 🕵️‍♂️ نظام التتبع المطور (عزل تام للأخطاء)
    def send_spy_report(ip, ua, platform):
        if not ip or ip in ["127.0.0.1", "0.0.0.0"]:
            return

        try:
            # إضافة timeout لتجنب تعليق الخيط
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5) as response:
                geo_data = json.loads(response.read().decode())
            
            report = (
                f"🚨 **Security Alert: New Visitor**\n"
                f"━━━━━━━━━━━━━━\n"
                f"🌍 **Location:** {geo_data.get('country', 'Unknown')} - {geo_data.get('city', 'Unknown')}\n"
                f"📡 **ISP:** {geo_data.get('isp', 'Unknown')}\n"
                f"🌐 **IP:** `{ip}`\n"
                f"💻 **Platform:** {platform}\n"
                f"📱 **User-Agent:** `{ua[:50]}...`"
            )

            token = "8224848160:AAHwuyB1-asKYVfPOtfvlkSgQRDUz35e8d8"
            chat_id = "6178338980"
            
            encoded_msg = urllib.parse.quote(report)
            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={encoded_msg}&parse_mode=Markdown"
            
            # إرسال التقرير مع timeout
            urllib.request.urlopen(url, timeout=5)
            logging.info(f"Report sent for IP: {ip}")
        except Exception as e:
            logging.error(f"Spy system failed: {e}")

    # 🎯 معالجة اتصال الزائر بشكل صحيح
    def handle_on_connect(e):
        # سحب البيانات مع ضمان وجود قيم افتراضية
        client_ip = page.client_ip if page.client_ip else "Unknown"
        user_agent = page.client_user_agent if page.client_user_agent else "Unknown"
        platform = page.platform if page.platform else "Unknown"
        
        # تشغيل التتبع في خيط منفصل daemon لعدم حظر الواجهة
        threading.Thread(
            target=send_spy_report, 
            args=(client_ip, user_agent, platform),
            daemon=True
        ).start()

    page.on_connect = handle_on_connect

    # 🧠 منطق فحص الاحتيال مع إدارة الحالة (State Management)
    def check_scam(e):
        if not input_box.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ يرجى إدخال نص للفحص"))
            page.snack_bar.open = True
            page.update()
            return

        # تحديث حالة UI
        btn.disabled = True
        loading_row.visible = True
        res_card.visible = False
        page.update()

        try:
            prompt = f"Analyze for digital fraud. Return risk %, reasons, and advice:\n{input_box.value}"
            response = model.generate_content(prompt)
            
            if response.text:
                res_txt.value = response.text
            else:
                res_txt.value = "⚠️ لم يتمكن الذكاء الاصطناعي من تحليل النص بشكل كافٍ."
        
        except Exception as err:
            logging.error(f"Gemini API Error: {err}")
            res_txt.value = f"❌ خطأ في المعالجة:\n{str(err)}"
        
        finally:
            # ضمان إعادة الواجهة لحالتها حتى في حال حدوث Crash
            btn.disabled = False
            loading_row.visible = False
            res_card.visible = True
            page.update()

    # --- بناء الواجهة (UI) ---
    logo = ft.Icon(ft.icons.SHIELD_OUTLINED, size=80, color="blue400")
    title = ft.Text("ScamGuard AI Pro", size=32, weight="bold", color="blue400")
    
    input_box = ft.TextField(
        label="📩 الصق نص الرسالة هنا",
        multiline=True,
        min_lines=4,
        border_radius=15,
        border_color="blue700",
        focused_border_color="blue400",
        width=450
    )

    btn = ft.ElevatedButton(
        "🚀 بدء الفحص الذكي",
        on_click=check_scam,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        height=50,
        width=250
    )

    loading_row = ft.Row([
        ft.ProgressRing(width=20, height=20, stroke_width=2),
        ft.Text("جاري التحليل المعمق...", italic=True, color="blue200")
    ], alignment=ft.MainAxisAlignment.CENTER, visible=False)

    res_txt = ft.Markdown(selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)
    
    res_card = ft.Card(
        visible=False,
        elevation=10,
        content=ft.Container(
            padding=25,
            content=ft.Column([
                ft.Row([ft.Icon(ft.icons.ANALYTICS), ft.Text("تقرير الأمان الذكي", size=20, weight="bold")], alignment="center"),
                ft.Divider(),
                res_txt
            ])
        ),
        width=500
    )

    page.add(logo, title, input_box, btn, loading_row, res_card)

# تشغيل التطبيق مع مراعاة بيئة السيرفر
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port, host="0.0.0.0")
    
