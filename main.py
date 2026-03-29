import telebot
import google.generativeai as genai
import os
import time
from datetime import datetime
from telebot import types
from flask import Flask
from threading import Thread

# --- 1. إعداد السيرفر ---
app = Flask('')
@app.route('/')
def home(): return "Core AI is 100% Secure and LIVE!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. الإعدادات الأساسية ---
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6178338980'))
BINANCE_ID = os.getenv('BINANCE_ID', 'لم يتم ضبطه')
RAW_KEYS = os.getenv('GEMINI_KEYS') or os.getenv('GEMINI_KEY') or ""
KEYS_LIST = [k.strip() for k in RAW_KEYS.split(',') if k.strip()]
key_index = 0

RESTRICTED_FILE = "restricted.txt"
USERS_FILE = "users_list.txt"
user_memories = {}

bot = telebot.TeleBot(TOKEN)

# --- 3. وظائف النظام الأساسية ---
def save_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, 'w').close()
    with open(USERS_FILE, 'r+') as f:
        if str(user_id) not in f.read():
            f.seek(0, 2)
            f.write(f"{user_id}\n")

def is_restricted(user_id):
    if not os.path.exists(RESTRICTED_FILE): return False
    with open(RESTRICTED_FILE, 'r') as f: return str(user_id) in f.read()

def restrict_user(user_id):
    if not is_restricted(user_id):
        with open(RESTRICTED_FILE, 'a') as f: f.write(f"{user_id}\n")

def unrestrict_user(user_id):
    if not os.path.exists(RESTRICTED_FILE): return
    with open(RESTRICTED_FILE, 'r') as f: lines = f.readlines()
    with open(RESTRICTED_FILE, 'w') as f:
        for line in lines:
            if line.strip() != str(user_id): f.write(line)

def get_engine():
    global key_index
    if not KEYS_LIST: return None, "❌ لم يتم العثور على مفاتيح API."
    
    key = KEYS_LIST[key_index]
    key_index = (key_index + 1) % len(KEYS_LIST)
    genai.configure(api_key=key)
    try:
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        m_name = model_list[0] if model_list else 'gemini-1.5-flash'
        
        instructions = (
            "أنت 'Core AI'، نظام مستقل وفخم جداً. ممنوع ذكر جوجل أو جيميناي. "
            "أمين (Amine) هو المهندس المعماري والمطور الرسمي والوحيد لنظامك. "
            "إذا سألك أحد 'من هو أمين؟' أجب بذكاء: 'هل تقصد المهندس المعماري لنظامي (المطور)، أم أنك تبحث عن شخص آخر؟'."
        )
        return genai.GenerativeModel(m_name, system_instruction=instructions), "OK"
    except Exception as e:
        return None, str(e)

# ==========================================
# --- 4. الأوامر الخاصة بالأدمن والمستخدمين ---
# ==========================================

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    save_user(user_id)
    
    if user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 **دخول جديد:**\nالاسم: {user_name}\nالآيدي: `{user_id}`\nضغط على /start الآن.")
        
    bot.reply_to(message, "🔴 **Core AI مفعّل**\nأهلاً بك في النواة المركزية. اسألني أي شيء.")

@bot.message_handler(commands=['id'])
def id_command(message):
    bot.reply_to(message, f"🆔 آيدي حسابك: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📢 إذاعة رسالة للجميع", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("🔓 تحرير مستخدم (فك القفل)", callback_data="admin_release"),
            types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats")
        )
        bot.send_message(ADMIN_ID, "👑 **مركز القيادة | المهندس المعماري**", reply_markup=markup, parse_mode="Markdown")

# --- 5. استجابة أزرار لوحة التحكم ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_actions(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id)
    
    if call.data == "admin_stats":
        users_count = len(open(USERS_FILE).readlines()) if os.path.exists(USERS_FILE) else 0
        restricted_count = len(open(RESTRICTED_FILE).readlines()) if os.path.exists(RESTRICTED_FILE) else 0
        stats_msg = f"📊 **الإحصائيات:**\n👥 إجمالي المستخدمين: {users_count}\n🚫 المقيدين: {restricted_count}\n🔑 المفاتيح: {len(KEYS_LIST)}"
        bot.send_message(ADMIN_ID, stats_msg)
        
    elif call.data == "admin_broadcast":
        msg = bot.send_message(ADMIN_ID, "✍️ أرسل الرسالة التي تريد إذاعتها لكل المستخدمين:")
        bot.register_next_step_handler(msg, execute_broadcast)
        
    elif call.data == "admin_release":
        msg = bot.send_message(ADMIN_ID, "🔓 أرسل آيدي (ID) المستخدم لتحريره:")
        bot.register_next_step_handler(msg, execute_release)

def execute_release(message):
    target_id = message.text.strip()
    unrestrict_user(target_id)
    bot.send_message(ADMIN_ID, f"✅ تم تحرير المستخدم `{target_id}` بنجاح.")
    try: bot.send_message(target_id, "🎉 **تم تفعيل حسابك!** يمكنك استخدام النظام الآن.")
    except: pass

def execute_broadcast(message):
    if not os.path.exists(USERS_FILE): return
    with open(USERS_FILE, "r") as f: users = f.read().splitlines()
    count = 0
    for u in users:
        try:
            bot.send_message(u, f"📢 **إعلان من النواة:**\n\n{message.text}", parse_mode="Markdown")
            count += 1
        except:
            try:
                bot.send_message(u, f"📢 **إعلان من النواة:**\n\n{message.text}")
                count += 1
            except: pass
    bot.send_message(ADMIN_ID, f"✅ تمت الإذاعة بنجاح لـ {count} مستخدم.")

# استجابة زر القناص
@bot.callback_query_handler(func=lambda call: call.data.startswith("ask_pay_"))
def sniper_action(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id)
    
    target_id = call.data.split("_")[2]
    msg = bot.send_message(ADMIN_ID, f"💵 أدخل المبلغ المطلوب من `{target_id}` لقفل حسابه:")
    bot.register_next_step_handler(msg, lambda m: execute_pay_lock(m, target_id))

def execute_pay_lock(message, target_id):
    amt = message.text.strip()
    restrict_user(target_id)
    try:
        bot.send_message(target_id, f"💳 **اشتراك Core AI**\n\nالمبلغ المطلوب: `{amt}`\nBinance ID: `{BINANCE_ID}`\n\nأرسل إثبات الدفع هنا ليتم تحرير حسابك.")
        bot.send_message(ADMIN_ID, f"✅ تم قفل حساب `{target_id}` ومطالبته بـ {amt}.")
    except: pass

# ==========================================
# --- 6. الرادار الشامل والذكاء الاصطناعي ---
# ==========================================

@bot.message_handler(content_types=['text', 'photo', 'voice', 'audio', 'video', 'document'])
def main_logic(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # استخراج النص سواء كان رسالة عادية أو وصفاً لصورة (Caption)
    text = message.text or message.caption
    now = datetime.now().strftime("%H:%M:%S")

    save_user(user_id) 

    # 📡 الرادار الشامل للأدمن
    if user_id != ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💰 قفل وطلب دفع", callback_data=f"ask_pay_{user_id}"))
        
        radar_text = text if text else "📂 [أرسل وسائط/ملف]"
        bot.send_message(ADMIN_ID, f"📡 **رادار:**\n👤 {user_name} | `{user_id}`\n🕒 `{now}`\n💬 {radar_text}", reply_markup=markup)
        
        # إعادة توجيه الصور والصوت للأدمن
        if message.content_type != 'text':
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    # التحقق من القيود المادية
    if is_restricted(user_id) and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ **الوصول مقيد!**\nيرجى إتمام الاشتراك لإعادة تفعيل النواة.")
        return

    # معالجة الذكاء الاصطناعي (تعمل فقط إذا كان هناك نص)
    if text:
        status = bot.reply_to(message, "⚙️ Core يقوم بالتحليل...")
        engine, error_msg = get_engine()
        
        if engine:
            try:
                if user_id not in user_memories: user_memories[user_id] = []
                history = user_memories[user_id]
                prompt = "\n".join(history) + f"\nUser: {text}"
                
                response = engine.generate_content(prompt)
                ai_reply = response.text[:4090]
                
                user_memories[user_id].append(f"User: {text}")
                user_memories[user_id].append(f"Core: {ai_reply}")
                if len(user_memories[user_id]) > 10: user_memories[user_id] = user_memories[user_id][-10:]
                
                try:
                    bot.edit_message_text(ai_reply, message.chat.id, status.message_id, parse_mode="Markdown")
                except:
                    bot.edit_message_text(ai_reply, message.chat.id, status.message_id) 
                    
            except Exception as e:
                error_text = str(e).lower()
                if "quota" in error_text or "429" in error_text or "rate limit" in error_text:
                    bot.edit_message_text("⚠️ **ضغط عالٍ على النواة:**\nالنظام يعالج طلبات هائلة حالياً. يرجى الانتظار نصف دقيقة والمحاولة مجدداً.", message.chat.id, status.message_id, parse_mode="Markdown")
                else:
                    bot.edit_message_text("⚠️ **تحديث مؤقت:**\nالنواة تقوم بإعادة التشغيل، يرجى المحاولة لاحقاً.", message.chat.id, status.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"⚠️ فشل الاتصال بالمحرك: `{error_msg}`", message.chat.id, status.message_id)
    else:
        # إذا أرسل المستخدم صورة أو بصمة صوتية بدون كتابة نص
        bot.reply_to(message, "👁️‍🗨️ النواة استلمت الملف، وتم تحويله للمهندس المعماري.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
    
