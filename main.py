import flet as ft
import google.generativeai as genai
import os

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def main(page: ft.Page):
    page.title = "ScamGuard AI Pro - By Amine"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 35

    def check_scam(e):
        if not input_box.value:
            return
        
        pb.visible = True
        res_card.visible = False
        page.update()

        prompt = f"حلل هذا النص واكتشف إذا كان احتيالاً: {input_box.value}"
        
        try:
            response = model.generate_content(prompt)
            res_txt.value = response.text
        except Exception as err:
            # 🔥 هذا هو السطر الذي سيكشف لنا المشكلة الحقيقية 🔥
            res_txt.value = f"الخطأ التقني هو: {str(err)}"
        
        res_card.visible = True
        pb.visible = False
        page.update()

    logo = ft.Text("🛡️", size=90)
    title = ft.Text("ScamGuard AI Pro", size=36, weight="bold", color="blue400")
    
    input_box = ft.TextField(
        label="الصق نص الرسالة هنا للفحص",
        multiline=True,
        min_lines=4,
        border_radius=15,
        border_color="blue"
    )

    btn = ft.ElevatedButton(
        "بدء الفحص الذكي",
        on_click=check_scam,
        height=50,
        width=250
    )

    pb = ft.ProgressBar(visible=False, color="cyan")
    res_txt = ft.Text(size=16)
    res_card = ft.Card(
        visible=False,
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("📊 تقرير الأمان:", size=20, weight="bold", color="cyan"),
                res_txt,
            ])
        )
    )

    page.add(logo, title, input_box, btn, pb, res_card)
    page.add(ft.Text("تم التحليل بواسطة خوارزميات Amine", size=12, italic=True, color="grey500"))

ft.app(target=main, view=None, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
