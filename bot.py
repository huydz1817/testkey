#!/usr/bin/python3
import telebot
import random, string, datetime, urllib.parse

# token bot của cậu (lấy từ BotFather)
TOKEN = "8279142566:AAE7719-93KPDHFXc0q8Y1eMCKJ_FUOpk0E"
bot = telebot.TeleBot(TOKEN)

# dict lưu key trong RAM
active_keys = {}  # key: {"user": user_id, "expire": datetime}

def generate_key(hours=1):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    expire = datetime.datetime.now() + datetime.timedelta(hours=hours)
    active_keys[key] = {"user": None, "expire": expire}
    return key

@bot.message_handler(commands=['getkey'])
def getkey_command(message):
    user_id = str(message.chat.id)
    # tạo key hạn 1h
    key = generate_key(hours=1)
    # tạo link vượt (fake link, cậu thay bằng link1s thật của cậu)
    base_link = "https://link1s.com/yourlink?key="
    link = base_link + urllib.parse.quote(key)

    bot.reply_to(message,
        f"🔑 Đây là link lấy key (hạn 1h):\n{link}\n\n"
        f"Sau khi vượt link, dùng lệnh:\n`/key {key}` để kích hoạt.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['key'])
def activate_key(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) < 2:
        bot.reply_to(message, "⚠️ Dùng đúng cú pháp: /key <KEY>")
        return

    key = command[1]
    if key not in active_keys:
        bot.reply_to(message, "❌ Key không tồn tại hoặc đã bị khoá.")
        return

    data = active_keys[key]
    if datetime.datetime.now() > data["expire"]:
        bot.reply_to(message, "⌛ Key đã hết hạn, vui lòng /getkey để lấy key mới.")
        del active_keys[key]
        return

    if data["user"] is None:
        active_keys[key]["user"] = user_id
        bot.reply_to(message, "✅ Key đã kích hoạt thành công cho tài khoản của bạn!")
    elif data["user"] == user_id:
        bot.reply_to(message, "✅ Key này đã kích hoạt cho tài khoản của bạn rồi.")
    else:
        bot.reply_to(message, "🚫 Key này đã bị người khác nhập, đã bị khoá.")
        del active_keys[key]

# chạy bot
bot.polling()
