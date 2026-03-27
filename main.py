import flet as ft
import google.generativeai as genai
import os

# 🔑 إعداد API
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ لم يتم العثور على GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# 🔥 الرادار الذكي لاختيار الموديل
best_model_name = "gemini-1.5-flash"
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        best_model_name = available_models[0] 
except Exception as e:
    pass

model = genai.GenerativeModel(best_model_name)

def main(page: ft.Page):
    page.title = "ScamGuard AI Pro - By Amine"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 25

    # 🎯 دالة الفحص
    def check_scam(e):
        if not input_box.value.strip():
            res_txt.value = "⚠️ الرجاء إدخال نص أولاً"
            res_card.visible = True
            page.update()
            return

        # 1️⃣ [تحديث الواجهة] إظهار دائرة التحميل وتعطيل الزر مؤقتاً
        btn.disabled = True
        loading_row.visible = True
        res_card.visible = False
        page.update()

        prompt = f"""
أنت خبير في كشف الاحتيال الرقمي.

حلل النص التالي وارجع النتيجة بشكل منظم:
1- هل هو احتيال؟ (نعم / لا)
2- نسبة الخطورة (من 0% إلى 100%)
3- الأسباب
4- نصيحة للمستخدم

النص:
{input_box.value}
"""

        try:
            response = model.generate_content(prompt)
            result = getattr(response, "text", None)

            if not result:
                result = "⚠️ لم يتم الحصول على رد واضح من النموذج"
            res_txt.value = result

        except Exception as err:
            res_txt.value = f"❌ خطأ تقني:\n{str(err)}"

        # 2️⃣ [تحديث الواجهة] إخفاء التحميل وإظهار النتيجة وإعادة تفعيل الزر
        loading_row.visible = False
        btn.disabled = False
        res_card.visible = True
        page.update()

    # 🎨 عناصر واجهة المستخدم
    logo = ft.Text("🛡️", size=80)
    title = ft.Text("ScamGuard AI Pro", size=32, weight="bold", color="blue400")

    input_box = ft.TextField(
        label="📩 الصق نص الرسالة هنا للفحص",
        multiline=True,
        min_lines=4,
        border_radius=15,
        border_color="blue",
        width=400
    )

    btn = ft.ElevatedButton(
        "🚀 بدء الفحص الذكي",
        on_click=check_scam,
        height=50,
        width=220
    )

    # 🔥 [الجديد] تصميم التحميل (دائرة متحركة + نص تفاعلي)
    loading_row = ft.Row(
        [
            ft.ProgressRing(color="cyan", width=25, height=25, stroke_width=3),
            ft.Text("جاري فحص الرسالة بالذكاء الاصطناعي... ⏳", size=16, color="cyan", italic=True)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False  # مخفي في البداية
    )

    res_txt = ft.Text(size=16, selectable=True)
    res_card = ft.Card(
        visible=False,
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("📊 تقرير الأمان", size=20, weight="bold", color="cyan"),
                res_txt,
            ])
        ),
        width=450
    )

    footer = ft.Text("تم التحليل بواسطة خوارزميات Amine", size=12, italic=True, color="grey500")

    # إضافة كل العناصر للصفحة (لاحظ أننا أضفنا loading_row تحت الزر)
    page.add(logo, title, input_box, btn, loading_row, res_card, footer)


# 🚀 تشغيل التطبيق على السيرفر (Render)
if __name__ == "__main__":
    ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
    
