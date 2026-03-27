import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading

# 🔑 المفاتيح السرية من إعدادات Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = "6178338980"

# إعداد المكتبة
genai.configure(api_key=GEMINI_KEY)

# 🤖 محرك البحث التلقائي عن موديل شغال (The Fallback Engine)
model = None
working_model_name = "None"

def find_working_model():
    global model, working_model_name
    # قائمة الموديلات التي سنحاول تجربتها بالترتيب من الأحدث للأقدم
    candidates = [
        "gemini-1.5-flash", 
        "models/gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-pro", 
        "models/gemini-pro"
    ]
    
    for name in candidates:
        try:
            # محاولة بناء الموديل
            temp_model = genai.GenerativeModel(name)
            # تجربة إرسال طلب "نبض" (Ping) بسيط جداً للتأكد من أنه ليس 404
            temp_model.generate_content("test", generation_config={"max_output_tokens": 1})
            
            # إذا وصلنا هنا، يعني الموديل شغال 100%
            model = temp_model
            working_model_name = name
            print(f"✅ تم العثور على موديل شغال: {name}")
            return
        except Exception as e:
            print(f"❌ الموديل {name} فشل: {str(e)}")
            continue

    print("🚨 لم ينجح أي موديل! تأكد من صلاحية مفتاح API.")

# تشغيل البحث فور بدء السيرفر
find_working_model()

def send_spy_report(ip, ua, platform):
    try:
        if not ip or ip in ["127.0.0.1", "0.0.0.0"]: return
        with urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5) as response:
            data = json.loads(response.read().decode())
        
        report = (
            f"🕵️‍♂️ **Visitor Alert**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🌍 {data.get('country')} - {data.get('city')}\n"
            f"📱 Device: {ua[:50]}...\n"
            f"🤖 AI Model: `{working_model_name}`\n"
            f"🌐 IP: `{ip}`"
        )
        
        safe_msg = urllib.parse.quote(report)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={safe_msg}&parse_mode=Markdown"
        urllib.request.urlopen(url, timeout=5)
    except: pass

def main(page: ft.Page):
    # إرسال تقرير الزائر
    threading.Thread(target=send_spy_report, args=(page.client_ip, page.client_user_agent, page.platform), daemon=True).start()

    page.title = "ScamGuard AI Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 30

    def check_scam(e):
        if not input_box.value.strip(): return
        if not model:
            res_txt.value = "❌ لا يوجد موديل ذكاء اصطناعي متاح حالياً. يرجى مراجعة إعدادات السيرفر."; page.update(); return
            
        btn.disabled = True; loading.visible = True; res_card.visible = False; page.update()
        
        try:
            # استخدام الموديل الذي نجح في الاختبار
            response = model.generate_content(f"Analyze this for fraud: {input_box.value}")
            res_txt.value = response.text
        except Exception as err:
            res_txt.value = f"❌ خطأ في التحليل: {str(err)}\n(الموديل المحاول: {working_model_name})"
        
        loading.visible = False; btn.disabled = False; res_card.visible = True; page.update()

    # الواجهة (🛡️ النسخة المستقرة)
    logo = ft.Text("🛡️", size=70)
    title = ft.Text("ScamGuard AI Pro", size=30, weight="bold", color="blue400")
    input_box = ft.TextField(label="📩 الصق النص هنا للفحص", multiline=True, width=450)
    btn = ft.ElevatedButton("🚀 بدء الفحص الذكي", on_click=check_scam, height=50, width=250)
    loading = ft.Row([ft.ProgressRing(width=20), ft.Text("جاري البحث عن موديل والتحليل...")], visible=False, alignment="center")
    res_txt = ft.Text(size=16, selectable=True)
    res_card = ft.Card(visible=False, content=ft.Container(padding=20, content=res_txt), width=500)
    
    page.add(logo, title, input_box, btn, loading, res_card)

if __name__ == "__main__":
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
    
