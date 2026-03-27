import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading

# 🔒 جلب المفاتيح من "الخزنة السرية" (Environment Variables) في سيرفر Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = "6178338980" # الـ ID الخاص بك (ثابت وآمن)

# إعداد الذكاء الاصطناعي
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 🕵️‍♂️ نظام التتبع المطور (إرسال التقارير لتليجرام)
def send_spy_report(ip, ua, platform):
    try:
        # تجنب إرسال تقارير عن السيرفر نفسه
        if not ip or ip in ["127.0.0.1", "0.0.0.0"]: return
        
        # جلب بيانات الموقع الجغرافي
        with urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5) as response:
            data = json.loads(response.read().decode())
        
        # تنسيق التقرير
        report = (
            f"🚨 **Security Alert: New Visit**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🌍 **Location:** {data.get('country')} - {data.get('city')}\n"
            f"📡 **ISP:** {data.get('isp')}\n"
            f"🌐 **IP:** `{ip}`\n"
            f"💻 **System:** {platform}\n"
            f"📱 **Device:** `{ua[:60]}...`"
        )
        
        safe_msg = urllib.parse.quote(report)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={safe_msg}&parse_mode=Markdown"
        
        # إرسال الرسالة لتليجرام
        urllib.request.urlopen(url, timeout=5)
    except:
        pass # لضمان استمرار الموقع حتى لو فشل التتبع

def main(page: ft.Page):
    # 🎯 تشغيل التتبع فور دخول الزائر
    client_ip = page.client_ip
    client_ua = page.client_user_agent if page.client_user_agent else "Unknown"
    client_plat = page.platform if page.platform else "Unknown"
    
    threading.Thread(target=send_spy_report, args=(client_ip, client_ua, client_plat), daemon=True).start()

    # إعدادات واجهة الموقع
    page.title = "ScamGuard AI Pro - By Amine"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    # دالة فحص الاحتيال
    def check_scam(e):
        if not input_box.value.strip(): return
        
        btn.disabled = True
        loading.visible = True
        res_card.visible = False
        page.update()

        try:
            prompt = f"حلل هذا النص كخبير احتيال رقمي ووضح نسبة الخطورة والأسباب:\n{input_box.value}"
            response = model.generate_content(prompt)
            res_txt.value = response.text if response.text else "⚠️ فشل التحليل"
        except Exception as err:
            res_txt.value = f"❌ خطأ تقني: {str(err)}"
        
        loading.visible = False
        btn.disabled = False
        res_card.visible = True
        page.update()

    # تصميم الواجهة (🛡️ النسخة المستقرة)
    logo = ft.Text("🛡️", size=70)
    title = ft.Text("ScamGuard AI Pro", size=30, weight="bold", color="blue400")
    input_box = ft.TextField(label="📩 الصق نص الرسالة للفحص", multiline=True, min_lines=4, border_radius=15, width=400)
    btn = ft.ElevatedButton("🚀 بدء الفحص الذكي", on_click=check_scam, height=50, width=220)
    loading = ft.Row([ft.ProgressRing(width=20), ft.Text("جاري التحليل...")], visible=False, alignment="center")
    res_txt = ft.Text(size=16, selectable=True)
    res_card = ft.Card(visible=False, content=ft.Container(padding=20, content=res_txt), width=450)
    
    page.add(logo, title, input_box, btn, loading, res_card)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port, host="0.0.0.0")
    
