
import flet as ft
import google.generativeai as genai
import os

# ==========================================
# 🛡️ توثيق الموقع: Amine - 2026
# ==========================================
DEVELOPER_NAME = "Amine"
# المفتاح سيُقرأ من إعدادات السيرفر للأمان
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCR9r30pcEn7JJBavxjJFxGD1XUf6AcCvE")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def main(page: ft.Page):
    page.title = f"ScamGuard AI Pro - By {DEVELOPER_NAME}"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 35

    # واجهة الموقع
    logo = ft.Text("🛡️", size=90)
    title = ft.Text("ScamGuard AI Pro", size=36, weight="bold", color="blue400")
    credit = ft.Text(f"نظام كشف الاحتيال الذكي | تطوير: {DEVELOPER_NAME}", size=14, color="grey500")

    input_box = ft.TextField(
        label="الصق نص الرسالة هنا للفحص",
        multiline=True,
        min_lines=4,
        border_radius=15,
        border_color="blue",
        focused_border_color="cyan"
    )

    pb = ft.ProgressBar(visible=False, color="cyan")
    res_txt = ft.Text(size=18, weight="w500")
    res_card = ft.Card(
        visible=False,
        elevation=10,
        content=ft.Container(padding=25, content=ft.Column([
            ft.Text("📊 تقرير الأمان:", size=20, weight="bold", color="cyan"),
            res_txt,
            ft.Divider(height=20),
            ft.Text(f"تم التحليل بواسطة خوارزميات {DEVELOPER_NAME}", size=11, italic=True)
        ]))
    )

    def analyze(e):
        if not input_box.value: return
        pb.visible = True
        res_card.visible = False
        page.update()

        try:
            prompt = f"حلل هذه الرسالة أمنياً في سطرين وأعط نسبة الاحتيال: {input_box.value}"
            response = model.generate_content(prompt)
            res_txt.value = response.text
        except:
            res_txt.value = "⚠️ عذراً، المحرك مشغول حالياً. حاول ثانية."

        pb.visible = False
        res_card.visible = True
        page.update()

    page.add(
        ft.Container(height=30),
        logo, title, credit,
        ft.Divider(height=40, color="transparent"),
        input_box,
        ft.Container(
            content=ft.ElevatedButton("بدء الفحص الذكي", on_click=analyze, height=55, width=250),
            padding=15
        ),
        pb,
        res_card,
        ft.Container(height=80),
        ft.Text(f"© 2026 Developed by {DEVELOPER_NAME} - Algeria", size=11, color="grey700")
    )

if __name__ == "__main__":
    # تشغيل متوافق مع الاستضافات العالمية (مثل Render)
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=os.getenv("PORT", "8080"), host="0.0.0.0")
