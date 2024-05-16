# کتابخانه های ایمپورت شده
import telebot
import time
import sqlite3

# تعریف ربات و کانال
bot = telebot.TeleBot("your bot token")
channel_id = "your channel id"#integer

# تابعی که کاربر عادی نتواند از دستورات ادمین استفاده کند
def admin_commad(message):
    if not is_admin(message):
        bot.reply_to(message, "از دستوراتی که وجود داره استفاده کن😐")
        return

# ساخت دیتابیس
def db_setup():
    conn = sqlite3.connect('botuser.db')
    cur = conn.cursor()
    cmd = '''
    CREATE TABLE IF NOT EXISTS personals (
        chat_id INTEGER PRIMARY KEY,
        last_sent_time INTEGER
    )
    '''
    cur.execute(cmd)
    conn.commit()
    cur.close()
    conn.close()

# اضافه کردن کاربر به دیتابیس
def add_member(chat_id):
    conn = sqlite3.connect('botuser.db')
    cur = conn.cursor()
    cmd = f'SELECT * FROM personals WHERE chat_id={chat_id}'
    cur.execute(cmd)
    result = cur.fetchall()
    if result == []:
        cmd = f'INSERT INTO personals (chat_id, last_sent_time) VALUES ({chat_id}, 0)'
        cur.execute(cmd)
        conn.commit()
    cur.close()
    conn.close()

# آیا کاربر میتواند آهنگ ارسال کند
def can_send_music(chat_id):
    conn = sqlite3.connect('botuser.db')
    cur = conn.cursor()
    cmd = f'SELECT last_sent_time FROM personals WHERE chat_id={chat_id}'
    cur.execute(cmd)
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        last_sent_time = result[0]
        current_time = int(time.time())
        if current_time - last_sent_time < 60:  # 60 seconds = 1 minute
            return False
    return True

# آپدیت آخرین تایم ارسال موزیک کاربر
def update_last_sent_time(chat_id):
    current_time = int(time.time())
    conn = sqlite3.connect('botuser.db')
    cur = conn.cursor()
    cmd = f'UPDATE personals SET last_sent_time={current_time} WHERE chat_id={chat_id}'
    cur.execute(cmd)
    conn.commit()
    cur.close()
    conn.close()

# گرفتن تمام جت آیدی کاربران
def get_all_chat_ids():
    conn = sqlite3.connect('botuser.db')
    cur = conn.cursor()
    cmd = 'SELECT chat_id FROM personals'
    cur.execute(cmd)
    chat_ids = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in chat_ids]

# کاربر عضو کانال است یا خیر
def is_member(message):
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(channel_id, user_id)
    if chat_member.status not in ["member", "administrator", "creator"]:
        return False
    else:
        return True

# کاربر ادمین است یا خیر
def is_admin(message):
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(channel_id, user_id)
    if chat_member.status not in ["administrator", "creator"]:
        return False
    else:
        return True

# فعال شدن پیام همگانی
def broadcast_message(message_text):
    chat_ids = get_all_chat_ids()
    for chat_id in chat_ids:
        bot.send_message(chat_id, message_text)

# خاموش بودن حالت پیام همگانی
broadcast_mode = False

# دکمه تعداد کاربران ربات
@bot.message_handler(func= lambda m:m.text == "تعداد کاربران ربات")
def send_member_count(message):
    if not is_admin(message):
        admin_commad(message)
    else:
        count = len(get_all_chat_ids())
        m = bot.reply_to(message, "تعداد کاربرانی که تا این لحظه در ربات عضو شده اند👇")
        bot.reply_to(message, f"کاربران ربات : {count} عضو")

# مدیریت کامنت استارت
@bot.message_handler(['start'])
def welcome(message):
    add_member(message.chat.id)
    if not is_admin(message):
        if not is_member(message):
            inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
            inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
            markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
            markup_channel.add(inline_channel, inline_check)
            bot.send_chat_action(message.chat.id, action='typing')
            m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
            time.sleep(10)
            bot.delete_message(message.chat.id, message_id=m.id)
            return
        else:
            keyboard_button = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
            keyboard_button.add("ادمین", "کانال", "سازنده", "ارسال موزیک")
            bot.send_chat_action(message.chat.id, action='typing')
            bot.reply_to(message, "سلام دوست عزیز , به ربات خوش اومدی😃", reply_markup=keyboard_button)
    else:
        keyboard_admin = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard_admin.add("تعداد کاربران ربات", "ارسال پیام","کانال","ارسال موزیک")
        bot.send_message(message.chat.id, "شما ادمین یا مدیر هستید .\n\n برای ادامه یکی از دکمه های زیر را انتخاب کنید 👇", reply_markup=keyboard_admin)

# دکمه ارسال پیام
@bot.message_handler(func= lambda m:m.text == "ارسال پیام")
def enable_broadcast_mode(message):
    if not is_admin(message):
        admin_commad(message)
    else:
        keyboard_admin = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard_admin.add("پیام به کاربران", "کنسل 🔙")
        bot.reply_to(message, "یکی از دکمه ها را انتخاب کن", reply_markup=keyboard_admin)

# دکمه پیام به کاربران
@bot.message_handler(func= lambda m:m.text == "پیام به کاربران")
def enable_broadcast_mode(message):
    if not is_admin(message):
        admin_commad(message)
    else:
        global broadcast_mode
        broadcast_mode = True
        bot.reply_to(message, "حالت ارسال پیام همگانی فعال شد.")

# دکمه کنسل برای ادمین
@bot.message_handler(func= lambda m:m.text == "کنسل 🔙")
def enable_broadcast_mode(message):
    if not is_admin(message):
        admin_commad(message)
    else:
        global broadcast_mode
        broadcast_mode = False
        bot.reply_to(message, "عملیات لغو گردید.")
        keyboard_admin = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard_admin.add("تعداد کاربران ربات", "ارسال پیام","کانال","ارسال موزیک")
        bot.send_message(message.chat.id, "شما ادمین یا مدیر هستید .\n\n برای ادامه یکی از دکمه های زیر را انتخاب کنید 👇", reply_markup=keyboard_admin)

# اجرای دکمه ادمین
@bot.message_handler(func= lambda m:m.text == "ادمین")
def admin(message):
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(message.chat.id, action='typing')
        m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(message.chat.id, message_id=m.id)
        return
    else:
        key_admin = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        key_admin.add("admin", "back ⬅️")
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, "ارتباط با ادمین", reply_markup=key_admin)

# اجرای دکمه ادمین
@bot.message_handler(func= lambda m:m.text == "admin")
def adin_key(message):
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(message.chat.id, action='typing')
        m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(message.chat.id, message_id=m.id)
        return
    else:
        inline_admin = telebot.types.InlineKeyboardButton("پیوی ادمین", url="https://t.me/mohwmmad86")
        markup_admin = telebot.types.InlineKeyboardMarkup()
        markup_admin.add(inline_admin)
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, "برای پیام به ادمین روی لینک زیر کلیک کن", reply_markup=markup_admin)

# اجرای دکمه کانال
@bot.message_handler(func= lambda m:m.text == "کانال")
def adin_key(message):
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(message.chat.id, action='typing')
        m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(message.chat.id, message_id=m.id)
        return
    else:
        inline_channel = telebot.types.InlineKeyboardButton("کانال", url="your channel url")
        markup_channel = telebot.types.InlineKeyboardMarkup()
        markup_channel.add(inline_channel)
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, "لینک کانال 🔗", reply_markup=markup_channel)
        return

# اجرای دکمه سازنده
@bot.message_handler(func= lambda m:m.text == "سازنده")
def adin_key(message):
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(message.chat.id, action='typing')
        m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(message.chat.id, message_id=m.id)
        return
    else:
        inline_builder = telebot.types.InlineKeyboardButton("سازنده ربات", callback_data="bot_builder")
        markup_builder = telebot.types.InlineKeyboardMarkup()
        markup_builder.add(inline_builder)
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, " سازنده 🔗", reply_markup=markup_builder)

# اجرای دکمه ارسال موزیک
@bot.message_handler(func= lambda m:m.text == "ارسال موزیک")
def adin_key(message):
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(message.chat.id, action='typing')
        m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(message.chat.id, message_id=m.id)
        return
    else:
        inline_builder = telebot.types.InlineKeyboardButton("نحوه ارسال موزیک", callback_data="send_music")
        markup_builder = telebot.types.InlineKeyboardMarkup()
        markup_builder.add(inline_builder)
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, "ارسال موزیک", reply_markup=markup_builder)

# مدیریت موزیک های ارسالی
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    chat_id = message.chat.id
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(chat_id, action='typing')
        m = bot.send_message(chat_id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(chat_id, message_id=m.id)
        return
    else:
        if not can_send_music(chat_id):
            bot.reply_to(message, "شما فقط می‌توانید هر یک دقیقه یک آهنگ ارسال کنید. لطفاً کمی صبر کنید.")
            return
        
        new_caption = "آهنگ ارسالی کاربران 🎵🎵\n\n #ارسالی \n\n your channel url"
        bot.send_chat_action(chat_id, action='typing')
        m = bot.reply_to(message, "آهنگ شما تا لحظاتی دیگر ارسال میشود")
        time.sleep(3)
        bot.send_audio(
            chat_id=channel_id,
            audio=message.audio.file_id,
            caption=new_caption,
            performer=message.audio.performer,
            title=message.audio.title
        )
        bot.send_chat_action(chat_id, action='typing')
        bot.edit_message_text(chat_id=chat_id, message_id=m.id, text="آهنگ شما در کانال آپلود شد")

        # به‌روزرسانی زمان آخرین ارسال
        update_last_sent_time(chat_id)

# دکمه برگشت
@bot.message_handler(func=lambda m: m.text == "back ⬅️")
def back(message):
    if not is_member(message):
        inline_channel = telebot.types.InlineKeyboardButton("کانال🔗", url="your channel url")
        inline_check = telebot.types.InlineKeyboardButton("چک کردن", url="your bot url with ?start=1")
        markup_channel = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup_channel.add(inline_channel, inline_check)
        bot.send_chat_action(message.chat.id, action='typing')
        m = bot.send_message(message.chat.id, "دوست عزیز , شما توی کانال عضو نیستی😕\n\nبرای فعال شدن ربات روی دکمه زیر کلیک کن و\n\n توی کانال عضو شو و سپس دستور /start رو دوباره ارسال کن", reply_markup=markup_channel)
        time.sleep(10)
        bot.delete_message(message.chat.id, message_id=m.id)
        return

    else:
        keyboard_button = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard_button.add("ادمین", "کانال", "سازنده", "ارسال موزیک")
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, "به صفحه اصلی برگشتی", reply_markup=keyboard_button)

# در این تابع اگر حالت پیام همگانی فعال بود پیام فرستاده شده به کاربران ارسال میشود
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global broadcast_mode
    if broadcast_mode:
        broadcast_message(message.text)
        bot.reply_to(message, "پیام به کاربران ارسال شد")
        broadcast_mode = False
    else:
        add_member(message.chat.id)
        admin_commad(message)
        
# جواب دادن به دکمه شیشه ای سازنده ربات
@bot.callback_query_handler(func=lambda call: call.data == "bot_builder")
def bulider(call):
    bot.answer_callback_query(call.id, text="سازنده ربات : @mohwmmad86\n\nاگه ربات مشکلی داشت حتما توی پیویم بگو 😉", show_alert=True)

# جواب دادن به دکمه شیشه ای ارسال موزیک
@bot.callback_query_handler(func=lambda call: call.data == "send_music")
def bulider(call):
    bot.answer_callback_query(call.id, text="برای ارسال موزیک اول باید توی کانال عضو باشی.بعد از این که عضو شدی آهنگت رو برای ربات ارسال کن", show_alert=True)

# اجرای تابع ساخت دیتابیس
db_setup()

# اجرای ربات
bot.infinity_polling(skip_pending=True)













