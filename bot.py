#!/usr/bin/python3
import telebot
import random, string, datetime

# 🔑 Thay bằng token BotFather của cậu
TOKEN = "8279142566:AAE7719-93KPDHFXc0q8Y1eMCKJ_FUOpk0E"
bot = telebot.TeleBot(TOKEN)

# ID admin (list, dạng string)
admin_id = ["6132441793"]

# dict lưu key
# key: {"user": user_id, "expire": datetime, "active": False}
active_keys = {}

# 👉 Hàm sinh key random
def generate_key(user_id, hours=1):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    expire = datetime.datetime.now() + datetime.timedelta(hours=hours)
    active_keys[key] = {"user": user_id, "expire": expire, "active": False}
    return key

# 👉 User xin key
@bot.message_handler(commands=['getkey'])
def getkey_request(message):
    user_id = str(message.chat.id)
    key = generate_key(user_id, hours=1)
    # báo admin
    for admin in admin_id:
        bot.send_message(admin, f"📩 User {user_id} xin key:\nKEY: {key}\nDuyệt bằng /accept {key}")
    bot.reply_to(message, "⏳ Yêu cầu key đã gửi admin, vui lòng chờ duyệt.")

# 👉 Admin duyệt key
@bot.message_handler(commands=['accept'])
def accept_key(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "❌ Chỉ admin mới duyệt key được.")
        return
    command = message.text.split()
    if len(command) < 2:
        bot.reply_to(message, "⚠️ Dùng đúng cú pháp: /accept <KEY>")
        return

    key = command[1]
    if key not in active_keys:
        bot.reply_to(message, "❌ Key không tồn tại.")
        return
    
    data = active_keys[key]
    if data["active"]:
        bot.reply_to(message, "⚠️ Key này đã được duyệt trước đó.")
        return

    # duyệt
    active_keys[key]["active"] = True
    user_target = data["user"]
    bot.reply_to(message, f"✅ Key {key} đã được duyệt cho user {user_target}.")
    # gửi key cho user
    try:
        bot.send_message(user_target, f"🔑 Admin đã duyệt key của bạn:\nKEY: {key}\nDùng /key {key} để kích hoạt (hạn 1h).")
    except:
        pass

# 👉 User nhập key
@bot.message_handler(commands=['key'])
def activate_key(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) < 2:
        bot.reply_to(message, "⚠️ Dùng đúng cú pháp: /key <KEY>")
        return

    key = command[1]
    if key not in active_keys:
        bot.reply_to(message, "❌ Key không tồn tại.")
        return

    data = active_keys[key]
    if not data["active"]:
        bot.reply_to(message, "⌛ Key này chưa được admin duyệt.")
        return
    if datetime.datetime.now() > data["expire"]:
        bot.reply_to(message, "⌛ Key này đã hết hạn, hãy dùng /getkey để xin key mới.")
        del active_keys[key]
        return
    if data["user"] != user_id:
        bot.reply_to(message, "🚫 Key này không thuộc về bạn.")
        return

    bot.reply_to(message, "✅ Key đã được kích hoạt thành công, bạn có thể sử dụng bot.")

# 👉 User check thời gian key
@bot.message_handler(commands=['checkkey'])
def check_key_time(message):
    user_id = str(message.chat.id)
    now = datetime.datetime.now()
    for k, v in active_keys.items():
        if v["user"] == user_id:
            if now > v["expire"]:
                bot.reply_to(message, "⌛ Key của bạn đã hết hạn.")
                return
            remaining = v["expire"] - now
            minutes, seconds = divmod(remaining.seconds, 60)
            bot.reply_to(message, f"⏳ Key của bạn còn {minutes} phút {seconds} giây.")
            return
    bot.reply_to(message, "❌ Bạn chưa có key nào, hãy dùng /getkey để xin.")

# 👉 chạy bot
bot.polling()
