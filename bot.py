import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")  # yoki to‘g‘ridan yoz: TOKEN = "123456:ABC..."
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Bot ishga tushdi ✅")

bot.polling(non_stop=True)

