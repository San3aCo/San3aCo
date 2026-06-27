import json, os, logging
from datetime import date
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8808947405:AAGw224qZAaZwHp1zuePKtc4hDZ0jHeq6bQ"  # ← حط التوكن اللي جبته من BotFather
SECRET = "san3a2024"
SUBS_FILE = "subscribers.json"

def load_subs():
    if not os.path.exists(SUBS_FILE):
        return {}
    with open(SUBS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_subs(data):
    with open(SUBS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_daily_code():
    d = date.today()
    s = f"{d.year}-{d.month:02d}-{d.day:02d}{SECRET}"
    h = 0
    for c in s:
        h = ((h << 5) - h) + ord(c)
        h &= h
    return format(abs(h), 'x')[:8].upper()

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً بك في بوت صنعة!\n\n"
        "إذا كنت مشتركاً، أرسل كلمة الاشتراك التي أرسلها لك الأدمن.\n"
        "سأرسل لك كود اليوم لفتح الكورسات."
    )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()
    subs = load_subs()
    user_id = str(update.message.from_user.id)

    # Search for the word in subscribers
    found_user = None
    for uid, data in subs.items():
        if data.get("word", "").lower() == word.lower():
            found_user = uid
            break

    if found_user is None:
        await update.message.reply_text("❌ كلمة الاشتراك غير صحيحة. تأكد من الكلمة أو تواصل مع الأدمن.")
        return

    # Update user ID if changed
    if found_user != user_id:
        subs[user_id] = subs.pop(found_user)
        save_subs(subs)

    code = get_daily_code()
    await update.message.reply_text(
        f"✅ تم التحقق! مرحباً {subs[user_id].get('name', '')}\n\n"
        f"🔐 كود اليوم: <code>{code}</code>\n\n"
        "أدخل هذا الكود في الموقع لفتح الكورسات لمدة 24 ساعة.\n"
        "الكود يتجدد يومياً في منتصف الليل.",
        parse_mode="HTML"
    )

async def add_word(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("استخدم: /add [كلمة_الاشتراك] [اسم_المشترك]")
        return
    word = ctx.args[0]
    name = " ".join(ctx.args[1:])
    subs = load_subs()
    subs[word] = {"word": word, "name": name, "added": str(date.today())}
    save_subs(subs)
    await update.message.reply_text(f"✅ تم إضافة المشترك: {name}\nكلمة الاشتراك: {word}")

async def list_words(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    subs = load_subs()
    if not subs:
        await update.message.reply_text("لا يوجد مشتركين بعد.")
        return
    msg = "📋 قائمة المشتركين:\n\n"
    for uid, data in subs.items():
        msg += f"• {data.get('name', '?')} — كلمة: {data.get('word', '?')}\n"
    await update.message.reply_text(msg)

async def remove_word(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("استخدم: /remove [كلمة_الاشتراك]")
        return
    word = ctx.args[0]
    subs = load_subs()
    to_del = None
    for uid, data in subs.items():
        if data.get("word", "").lower() == word.lower():
            to_del = uid
            break
    if to_del:
        del subs[to_del]
        save_subs(subs)
        await update.message.reply_text(f"✅ تم حذف المشترك بكلمة: {word}")
    else:
        await update.message.reply_text("❌ الكلمة غير موجودة.")

async def today_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    code = get_daily_code()
    await update.message.reply_text(f"🔐 كود اليوم: <code>{code}</code>", parse_mode="HTML")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_word))
    app.add_handler(CommandHandler("list", list_words))
    app.add_handler(CommandHandler("remove", remove_word))
    app.add_handler(CommandHandler("code", today_code))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("[OK] Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
