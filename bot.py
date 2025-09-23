
# bot.py
# بوت تليجرام: عرض معلومات المستخدم عند الضغط على زر "عرض معلومات حسابي"
# كل التعليقات باللغة العربية لسهولة الفهم.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN") or "7715852438:AAEaYXak8zgGHCYCPACmUwOP5vleWD7-T-Y"

# رسالة /start: تعرض زر "عرض معلومات حسابي"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("عرض معلومات حسابي", callback_data="show_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # إذا المحادثة خاصة نرسل ترحيب وزر
    await update.message.reply_text("اضغط الزر لعرض معلومات حسابك:", reply_markup=reply_markup)

# معالجة ضغطة الزر
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # تأكيد استلام الضغط

    user = query.from_user  # بيانات المستخدم الذي ضغط الزر
    user_id = user.id

    # نحاول جلب معلومات الشات (قد يتضمن bio للمستخدم إن كان متاحاً)
    try:
        chat = await context.bot.get_chat(user_id)
    except Exception as e:
        chat = None

    # جلب صورة الملف الشخصي (أول صورة إن وجدت)
    photos = await context.bot.get_user_profile_photos(user_id, limit=1)
    photo_file_id = None
    if photos.total_count and photos.photos:
        # photos.photos is list of lists (sizes). نأخذ آخر حجم (أكبر) من المجموعة الأولى
        sizes = photos.photos[0]
        photo_file_id = sizes[-1].file_id

    # تجهيز نص المعلومات (حريصين على التعامل مع القيم الفارغة)
    full_name = (user.first_name or "") + ((" " + user.last_name) if user.last_name else "")
    username = ("@" + user.username) if user.username else "لا يوجد"
    user_id_str = str(user_id)
    language = user.language_code or "غير محدد"
    is_bot = "نعم" if user.is_bot else "لا"

    # بايو (السيرة) متاح أحيانًا عبر get_chat -> chat.bio
    bio = getattr(chat, "bio", None) if chat else None
    bio_text = bio if bio else "لا يوجد بايو مرئي"

    # ملاحظات على معلومات غير متاحة: (انشئنا قائمة لتوضيح القيود للمستخدم)
    notes = [
        "- ملاحظة: واجهة بوت تليجرام لا تسمح للبوت بمعرفة تاريخ إنشاء الحساب.",
        "- ملاحظة: لا يمكن للبوت الوصول لسجل تغيّر اليوزرنيم (الأسماء السابقة) عبر API الرسمي."
    ]
    notes_text = "\n".join(notes)

    caption_lines = [
        f"الاسم الكامل: {full_name or 'غير متوفر'}",
        f"اليوزر: {username}",
        f"الايدي: {user_id_str}",
        f"لغة المستخدم: {language}",
        f"هل بوت؟: {is_bot}",
        f"البايو: {bio_text}",
        "",
        notes_text
    ]
    caption = "\n".join(caption_lines)

    # نرسل الصورة إن وُجدت، وإلا نرسل رسالة نصية
    if photo_file_id:
        try:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo_file_id,
                caption=caption
            )
            return
        except Exception:
            # إذا فشل إرسال الملف عبر file_id نتابع ونرسل نص فقط
            pass

    # إرسال نص بديل إذا لم توجد صورة
    await context.bot.send_message(chat_id=query.message.chat_id, text=caption)

# أمر للمطور (اختياري) لإظهار معلومات خام في المحادثة (debug)
async def me_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(f"Debug: {user}\n\nUser object: {user.to_dict()}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    # أمر اختباري
    app.add_handler(CommandHandler("me", me_cmd))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

