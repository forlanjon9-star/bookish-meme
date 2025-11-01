import telebot
from docx import Document
from pptx import Presentation
from pptx.util import Inches
import os
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")  # 8493133123:AAG4XlRunfFMgrFKLp7yREeg-apn4jT93HI
bot = telebot.TeleBot(8493133123:AAG4XlRunfFMgrFKLp7yREeg-apn4jT93HI)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📄 Maqola", "📘 Mustaqil ish", "📊 Slayd")
    bot.send_message(message.chat.id, "Assalomu alaykum! Qaysi turdagi hujjat kerak?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["📄 Maqola", "📘 Mustaqil ish", "📊 Slayd"])
def ask_topic(message):
    doc_type = message.text
    bot.send_message(message.chat.id, f"{doc_type} uchun mavzuni kiriting:")
    bot.register_next_step_handler(message, generate_file, doc_type)

def generate_file(message, doc_type):
    topic = message.text

    if doc_type in ["📄 Maqola", "📘 Mustaqil ish"]:
        doc = Document()
        doc.add_heading(topic, 0)
        doc.add_paragraph("Bu avtomatik yaratilgan hujjat namunasi.\n")
        for i in range(5):
            doc.add_paragraph(f"{i+1}. {topic} haqida matn joyi ...")
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        bot.send_document(message.chat.id, buffer, visible_file_name=f"{topic}.docx")

    elif doc_type == "📊 Slayd":
        prs = Presentation()
        for i in range(10):
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = slide.shapes.title
            content = slide.placeholders[1]
            title.text = f"{topic} — Slayd {i+1}"
            content.text = f"Bu {topic} mavzusidagi slayd matni (Slayd {i+1})."
        buffer = BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        bot.send_document(message.chat.id, buffer, visible_file_name=f"{topic}.pptx")

    bot.send_message(message.chat.id, "✅ Tayyor! Fayl yuborildi.")

bot.polling(non_stop=True)
