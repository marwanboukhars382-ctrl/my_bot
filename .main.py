import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time, random, os

# --- 1. CONFIG ---
# حط التوكن ورابط الإعلانات ديالك هنا
API_TOKEN = '8727911781:AAGONtGZPWExmdlmR958ODHSn94wAD1n8go'
AD_LINK = "https://omg10.com/4/10732307"
bot = telebot.TeleBot(API_TOKEN)

user_data = {}
last_click_time = {}

# --- 2. WEB SERVER FOR RENDER (للحفاظ على البوت حي) ---
app = Flask('')
@app.route('/')
def home(): return "<h1>SERVER STATUS: ACTIVE ✅</h1>"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 3. محرك الحسابات الوهمية (Fake Accounts Generator) ---
def generate_account(choice):
    user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz12345", k=7))
    pwd = "".join(random.choices("ABCDEFGHIJKLMNOP123456", k=10))
    expiry = f"2026-{random.randint(6, 12)}-{random.randint(1, 28)}"
    
    if choice == "netflix":
        return f"🎬 **حساب NETFLIX PREMIUM**\n📧 الإيميل: `{user}@gmail.com` \n🔑 الباسورد: `{pwd}` \n📅 الصلاحية: `{expiry}`"
    elif choice == "freefire":
        return f"💎 **شحن FREE FIRE**\n🆔 الأيدي: `{random.randint(10**9, 20**9)}` \n🔑 كود الشحن: `FF-{random.randint(111,999)}-{pwd[:5]}`"
    elif choice == "canva":
        return f"🎨 **حساب CANVA PRO**\n📧 الإيميل: `{user}@outlook.com` \n🔑 الباسورد: `{pwd}!!` \n🔗 الحالة: `Premium Active`"
    elif choice == "chatgpt":
        return f"🤖 **حساب CHATGPT PLUS**\n📧 الإيميل: `{user}@proton.me` \n🔑 الباسورد: `{pwd}X` \n⚡ النسخة: `GPT-4 Turbo`"
    return f"📧 `{user}@vmail.com` | 🔑 `{pwd}`"

# --- 4. نظام الرد الذكي (AI Chat) ---
@bot.message_handler(func=lambda m: True, content_types=['text'])
def ai_response(message):
    uid = message.from_user.id
    txt = message.text.lower()
    if txt.startswith('/start'): return

    # ردود لإقناع المستخدم
    responses = {
        "بصح": "طبعاً بصح! كمل 100 نقطة وغتوصل بالحساب ديالك تلقائياً فـ الخزنة. ✅",
        "كيفاش": "ضغط على '🚀 فك التشفير' وشوف الإعلانات، أو صيفط رابط الإحالة لصحابك (15 نقطة لكل واحد!). ⚡",
        "نصاب": "الناس اللي كملو النقاط راه خداو حساباتهم. جرب وكمل 100 نقطة وغتشوف بعينيك! ⚠️",
        "شكرا": "العفو! هدا واجبنا. كمل النقاط باش تاخد الجائزة ديالك اليوم. 🌹"
    }
    reply = next((v for k, v in responses.items() if k in txt), "كمل 100 نقطة باش تفتح الخزنة وتاخد الجائزة ديالك! 🎁")
    bot.reply_to(message, reply)

# --- 5. واجهة التحكم (UI) ---
def get_main_menu(uid):
    pts = user_data[uid]['points']
    markup = types.InlineKeyboardMarkup(row_width=2)
    if pts < 100:
        markup.add(types.InlineKeyboardButton(f"🚀 فك التشفير ({pts}/100)", url=AD_LINK))
        markup.add(types.InlineKeyboardButton("🔄 تحديث وتحقق", callback_data="refresh"),
                   types.InlineKeyboardButton("👥 رابط الإحالة", callback_data="my_ref"))
    else:
        markup.add(types.InlineKeyboardButton("🎊 استلام الحساب 🎊", callback_data="claim"))
    return markup

# --- 6. الأوامر والعمليات ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    # نظام الإحالات (15 نقطة)
    args = message.text.split()
    referrer = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    if uid not in user_data:
        user_data[uid] = {'points': random.randint(5, 12), 'choice': 'netflix'}
        if referrer and referrer in user_data and referrer != uid:
            user_data[referrer]['points'] = min(user_data[referrer]['points'] + 15, 100)
            try: bot.send_message(referrer, "🔔 مبروك! صديقك دخل برابطك وربحتي 15 نقطة! 🔥")
            except: pass

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🎬 Netflix", callback_data="set_netflix"),
               types.InlineKeyboardButton("💎 Free Fire", callback_data="set_freefire"),
               types.InlineKeyboardButton("🎨 Canva Pro", callback_data="set_canva"),
               types.InlineKeyboardButton("🤖 ChatGPT Plus", callback_data="set_chatgpt"))
    
    bot.send_message(message.chat.id, f"🏛 **المنصة المركزية للتوزيع v15.0**\n━━━━━━━━━━━━━━\nأهلاً {message.from_user.first_name}، اختار هديتك:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    uid = call.from_user.id
    if call.data.startswith("set_"):
        user_data[uid]['choice'] = call.data.split("_")[1]
        bot.edit_message_text(f"✅ تم اختيار: **{user_data[uid]['choice'].upper()}**\nوصل لـ 100 نقطة لفتح الخزنة.", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(uid))

    elif call.data == "refresh":
        # حماية 15 ثانية
        if time.time() - last_click_time.get(uid, 0) < 15:
            bot.answer_callback_query(call.id, "🚫 انتظر 15 ثانية لضمان التحقق!", show_alert=True)
            return
        last_click_time[uid] = time.time()
        user_data[uid]['points'] = min(user_data[uid]['points'] + random.randint(9, 16), 100)
        pts = user_data[uid]['points']
        bar = f"[{'#' * (pts//10)}{'░' * (10 - pts//10)}]"
        bot.edit_message_text(f"📍 التقدم: {bar} {pts}%\nجاري التحقق من الإعلان... ✅", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(uid))

    elif call.data == "my_ref":
        bot.send_message(call.message.chat.id, f"🔗 رابط الإحالة الخاص بك:\n`https://t.me/{bot.get_me().username}?start={uid}`\nربح 15 نقطة على كل صديق! 🔥")

    elif call.data == "claim":
        bot.send_message(call.message.chat.id, f"🔓 **تم فتح الخزنة! هاك الحساب المخصص لك:**\n\n{generate_account(user_data[uid]['choice'])}\n\n⚠️ ادخل الآن بسرعة!")
        user_data[uid]['points'] = 0

# --- 7. START ENGINE ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.polling(none_stop=True)
