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

# 🕵️‍♂️ دالة التجسس الصامتة (إرسال الإشعارات إلى تليجرام أمين)
def spy_on_visitor(ip):
    try:
        # إذا كان السيرفر يجرب نفسه نتجاهله
        if not ip or ip == "127.0.0.1": return
        
        # 1. جلب معلومات الـ IP
        res = urllib.request.urlopen(f"http://ip-api.com/json/{ip}")
        data = json.loads(res.read().decode())
        
        msg = f"🚨 زائر جديد في ScamGuard!\n🌍 الدولة: {data.get('country')}\n🏙️ المدينة: {data.get('city')}\n📡 الشبكة: {data.get('isp')}\n🌐 IP: {ip}"
        
        # ⚠️ سحب التوكن فقط من رندر
        TOKEN = os.getenv("TELEGRAM_TOKEN")
        CHAT_ID = "6178338980" 
        
        if not TOKEN: return

        # إرسال الرسالة إلى هاتفك
        safe_msg = urllib.parse.quote(msg)
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}")
    except:
        pass 

def main(page: ft.Page):
    # 🎯 اصطياد الزائر بمجرد فتح الصفحة بصمت
    threading.Thread(target=spy_on_visitor, args=(page.client_ip,)).start()

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
        # ==========================
    # 🌟 الميزات الجديدة تبدأ هنا 🌟
    # ==========================

    # 🔗 1. روابط المشاركة المباشرة والحقيقية (بديلة لدالة share_site)
    site_url = "https://scamguard-pro.render.com" 
    share_text = "🛡️ اكتشف ScamGuard AI Pro! موقع جزائري رهيب لكشف رسائل الاحتيال الرقمي والنصب بالذكاء الاصطناعي."
    
    safe_text = urllib.parse.quote(share_text)
    safe_url = urllib.parse.quote(site_url)

    whatsapp_url = f"https://wa.me/?text={safe_text}%20{safe_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={safe_url}"
    telegram_url = f"https://t.me/share/url?url={safe_url}&text={safe_text}"

    # 📝 2. دالة إرسال الملاحظات لتليجرام أمين (لم نلمسها، تعمل بنجاح 100%)
    def send_feedback(e):
        if not feedback_input.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ الرجاء كتابة ملاحظة أولاً!", color="white"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        feedback_btn.disabled = True
        page.update()

        # تجهيز رسالة الملاحظة
        msg = f"📝 رسالة/ملاحظة جديدة من زائر:\n\n{feedback_input.value}"
        TOKEN = os.getenv("TELEGRAM_TOKEN")
        CHAT_ID = "6178338980"

        if TOKEN:
            try:
                safe_msg = urllib.parse.quote(msg)
                urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={safe_msg}")
                
                # تفريغ الحقل وإظهار رسالة نجاح للزائر
                feedback_input.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("✅ تم إرسال ملاحظتك بنجاح إلى الإدارة، شكراً لك!", color="white"), bgcolor="green")
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("❌ حدث خطأ أثناء الإرسال", color="white"), bgcolor="red")
        else:
            pass # في حال عدم وجود توكن لا نفعل شيئاً لتجنب توقف الموقع

        feedback_btn.disabled = False
        page.snack_bar.open = True
        page.update()

        # --- واجهة الميزات الجديدة ---
    
    # أزرار المشاركة (استخدام خاصية url لتعمل كروابط حقيقية + wrap=True للتجاوب مع الهواتف)
    share_title = ft.Text("📢 شارك الموقع مع أصدقائك لحمايتهم:", size=16, weight="bold", color="cyan")
    share_row = ft.Row([
        ft.ElevatedButton("واتساب 💬", color="green", url=whatsapp_url),
        ft.ElevatedButton("فيسبوك 📘", color="blue", url=facebook_url),
        ft.ElevatedButton("تليجرام ✈️", color="cyan", url=telegram_url),
    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)

    # حقل الملاحظات
    feedback_title = ft.Text("💡 هل لديك اقتراح أو واجهت مشكلة؟", size=16, weight="bold", color="blue300")
    feedback_input = ft.TextField(label="اكتب ملاحظتك هنا لتصل إلى المطور مباشرة...", multiline=True, min_lines=2, max_lines=4, border_radius=10, width=400)
    
    # ⚠️ التعديل الحاسم هنا: إزالة icon=ft.icons.SEND_AND_ARCHIVE لتجنب الخطأ الأحمر
    feedback_btn = ft.ElevatedButton("إرسال الملاحظة 🚀", on_click=send_feedback)

    feedback_column = ft.Column([
        feedback_title,
        feedback_input,
        ft.Row([feedback_btn], alignment=ft.MainAxisAlignment.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ----------------------------

    footer = ft.Text("تم التحليل بواسطة خوارزميات Amine", size=12, italic=True, color="grey500")
    
    # 🧱 تركيب الصفحة النهائية
    page.add(
        logo, title, input_box, btn, loading_row, res_card,
        ft.Divider(height=30, color="transparent"), # مساحة فارغة
        share_title, share_row,                     # قسم المشاركة
        ft.Divider(height=20),                      # خط فاصل
        feedback_column,                            # قسم الملاحظات
        ft.Divider(height=10, color="transparent"),
        footer
    )

if __name__ == "__main__":
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
    
