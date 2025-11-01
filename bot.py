import telebot
import os
from docx import Document
from pptx import Presentation

# Tokenni bu yerda qo'shtirnoq ichida yozing
bot = telebot.TeleBot("8493133123:AAG4XlRunfFMgrFKLp7yREeg-apn4jT93HI")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men sizga maqola yoki slayd yaratib bera olaman.\n\nTanlang:\n📝 Maqola\n📊 Slayd")

@bot.message_handler(func=lambda message: message.text.lower() == "maqola")
def maqola_handler(message):
    bot.reply_to(message, "Maqola uchun mavzu kiriting:")

@bot.message_handler(func=lambda message: message.text.lower() == "slayd")
def slayd_handler(message):
    bot.reply_to(message, "Slayd uchun mavzu kiriting:")

@bot.message_handler(func=lambda message: True)
def create_file(message):
    text = message.text
    if "maqola" in text.lower():
        # Maqola yaratish
        doc = Document()
        doc.add_heading(text, 0)
        for i in range(1, 6):
            doc.add_paragraph(f"{i}-qism: {text} haqida batafsil yozilgan matn.\n")
        filename = "maqola.docx"
        doc.save(filename)
        with open(filename, "rb") as f:
            bot.send_document(message.chat.id, f)
    elif "slayd" in text.lower():
        # Slayd yaratish
        prs = Presentation()
        for i in range(10):
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = f"{text} - {i+1}-slayd"
            slide.placeholders[1].text = f"{text} haqida ma'lumot."
        filename = "slayd.pptx"
        prs.save(filename)
        with open(filename, "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.reply_to(message, "Iltimos, /start deb yozing yoki 'Maqola' yoki 'Slayd' buyrug'ini tanlang.")

print("🤖 Bot ishga tushdi...")
bot.polling(non_stop=True)
