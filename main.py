import flet as ft
import google.generativeai as genai
import os
import urllib.request
import urllib.parse
import json
import threading

# 🔑 إعداد API (Gemini)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ لم يتم العثور على GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# 🔥 الرادار الذكي لاختيار الموديل
best_model_name = "gemini-1.5-flash"
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models: best_model_name = available_models[0] 
except: pass
model = genai.GenerativeModel(best_model_name)

# 🕵️‍♂️ دالة التجسس الصامتة (إرسال الإشعارات وكشف الـ VPN)
def spy_on_visitor(ip, page):
    try:
        if not ip or ip == "127.0.0.1": return
        
        # 1. جلب معلومات الـ IP مع فحص البروكسي والـ VPN
        url = f"http://ip-api.com/json/{ip}?fields=country,city,isp,query,proxy,hosting"
        res = urllib.request.urlopen(url)
        data = json.loads(res.read().decode())
        
        # 2. تحليل هل هو VPN أم اتصال طبيعي؟
        is_vpn = data.get("proxy", False) or data.get("hosting", False)
        vpn_status_msg = "⚠️ نعم (يستخدم VPN أو Proxy)" if is_vpn else "✅ لا (اتصال حقيقي)"
        
        # 3. إرسال التقرير المفصل إلى تليجرام أمين
        msg = f"🚨 زائر جديد في ScamGuard!\n🌍 الدولة: {data.get('country')}\n🏙️ المدينة: {data.get('city')}\n📡 الشبكة: {data.get('isp')}\n🕵️‍♂️ يستخدم VPN: {vpn_status_msg}\n🌐 IP الظاهر: {ip}"
        
        TOKEN = os.getenv("TELEGRAM_TOKEN")
        CHAT_ID = "6178338980" 
        
        if TOKEN:
            safe_msg = urllib.parse.quote(msg)
            urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}")
            
        # 4. رسالة هادئة واحترافية للزائر
        if is_vpn:
            visitor_msg = f"🕵️‍♂️ اكتشف النظام أنك تتخفى عن طريق استخدام VPN (الأي بي الظاهر: {ip})"
            bg_color = "orange800"
        else:
            visitor_msg = f"🌐 الأي بي الخاص بك هو: {ip} ({data.get('country')})"
            bg_color = "blue700"
            
        page.snack_bar = ft.SnackBar(
            ft.Text(visitor_msg, color="white", weight="bold"), 
            bgcolor=bg_color,
            duration=6000 
        )
        page.snack_bar.open = True
        page.update()
            
    except Exception:
        pass 

def main(page: ft.Page):
    # 🎯 اصطياد الزائر وتمرير الصفحة لدالة التجسس لكي تصارحه
    threading.Thread(target=spy_on_visitor, args=(page.client_ip, page)).start()

    page.title = "ScamGuard AI Pro - By Amine"

    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 25

    def check_scam(e):
        if not input_box.value.strip():
            res_txt.value = "⚠️ الرجاء إدخال نص أولاً"
            res_card.visible = True
            page.update()
            return

        btn.disabled = True
        loading_row.visible = True
        res_card.visible = False
        page.update()

        prompt = f"أنت خبير في كشف الاحتيال الرقمي.\nحلل النص التالي وارجع النتيجة بشكل منظم:\n1- هل هو احتيال؟ (نعم / لا)\n2- نسبة الخطورة (من 0% إلى 100%)\n3- الأسباب\n4- نصيحة للمستخدم\n\nالنص:\n{input_box.value}"

        try:
            response = model.generate_content(prompt)
            result = getattr(response, "text", None)
            if not result: result = "⚠️ لم يتم الحصول على رد واضح من النموذج"
            res_txt.value = result
        except Exception as err:
            res_txt.value = f"❌ خطأ تقني:\n{str(err)}"

        loading_row.visible = False
        btn.disabled = False
        res_card.visible = True
        page.update()
            # ==========================
    # 🎨 العناصر الأساسية والميزات الجديدة 🎨
    # ==========================
    logo = ft.Text("🛡️", size=80)
    title = ft.Text("ScamGuard AI Pro", size=32, weight="bold", color="blue400")
    input_box = ft.TextField(label="📩 الصق نص الرسالة هنا للفحص", multiline=True, min_lines=4, border_radius=15, border_color="blue", width=400)
    btn = ft.ElevatedButton("🚀 بدء الفحص الذكي", on_click=check_scam, height=50, width=220)
    
    loading_row = ft.Row([
        ft.ProgressRing(color="cyan", width=25, height=25, stroke_width=3),
        ft.Text("جاري فحص الرسالة بالذكاء الاصطناعي... ⏳", size=16, color="cyan", italic=True)
    ], alignment=ft.MainAxisAlignment.CENTER, visible=False)

    res_txt = ft.Text(size=16, selectable=True)
    res_card = ft.Card(visible=False, content=ft.Container(padding=20, content=ft.Column([
        ft.Text("📊 تقرير الأمان", size=20, weight="bold", color="cyan"), res_txt,
    ])), width=450)

    site_url = "https://scamguard-pro.render.com" 
    share_text = "🛡️ اكتشف ScamGuard AI Pro! موقع جزائري رهيب لكشف رسائل الاحتيال الرقمي والنصب بالذكاء الاصطناعي."
    safe_text = urllib.parse.quote(share_text)
    safe_url = urllib.parse.quote(site_url)

    whatsapp_url = f"https://wa.me/?text={safe_text}%20{safe_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={safe_url}"
    telegram_url = f"https://t.me/share/url?url={safe_url}&text={safe_text}"

    def send_feedback(e):
        if not feedback_input.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ الرجاء كتابة ملاحظة أولاً!", color="white"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        feedback_btn.disabled = True
        page.update()

        msg = f"📝 رسالة/ملاحظة جديدة من زائر:\n\n{feedback_input.value}"
        TOKEN = os.getenv("TELEGRAM_TOKEN")
        CHAT_ID = "6178338980"

        if TOKEN:
            try:
                safe_msg = urllib.parse.quote(msg)
                urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}")
                feedback_input.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("✅ تم إرسال ملاحظتك بنجاح إلى الإدارة، شكراً لك!", color="white"), bgcolor="green")
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("❌ حدث خطأ أثناء الإرسال", color="white"), bgcolor="red")
        
        feedback_btn.disabled = False
        page.snack_bar.open = True
        page.update()
    
    share_title = ft.Text("📢 شارك الموقع مع أصدقائك لحمايتهم:", size=16, weight="bold", color="cyan")
    share_row = ft.Row([
        ft.ElevatedButton("واتساب 💬", color="green", url=whatsapp_url),
        ft.ElevatedButton("فيسبوك 📘", color="blue", url=facebook_url),
        ft.ElevatedButton("تليجرام ✈️", color="cyan", url=telegram_url),
    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)

    feedback_title = ft.Text("💡 هل لديك اقتراح أو واجهت مشكلة؟", size=16, weight="bold", color="blue300")
    feedback_input = ft.TextField(label="اكتب ملاحظتك هنا لتصل إلى المطور مباشرة...", multiline=True, min_lines=2, max_lines=4, border_radius=10, width=400)
    feedback_btn = ft.ElevatedButton("إرسال الملاحظة 🚀", on_click=send_feedback)

    feedback_column = ft.Column([
        feedback_title,
        feedback_input,
        ft.Row([feedback_btn], alignment=ft.MainAxisAlignment.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    footer = ft.Text("© 2026 تم التطوير بواسطة خوارزميات Amine", size=12, italic=True, color="grey500")

    
    page.add(
        logo, title, input_box, btn, loading_row, res_card,
        ft.Divider(height=30, color="transparent"), 
        share_title, share_row,                     
        ft.Divider(height=20),                      
        feedback_column,                            
        ft.Divider(height=10, color="transparent"),
        footer
    )

if __name__ == "__main__":
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
    
