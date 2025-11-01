import telebot
from docx import Document
from pptx import Presentation
from pptx.util import Inches
import os
from io import BytesIO
from openai import OpenAI

# Tokenlar
TOKEN = os.getenv("8493133123:AAG4XlRunfFMgrFKLp7yREeg-apn4jT93HI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=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)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📄 Maqola", "📘 Mustaqil ish", "📊 Slayd")
    bot.send_message(message.chat.id, "Assalomu alaykum!\nQaysi turdagi hujjatni xohlaysiz?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["📄 Maqola", "📘 Mustaqil ish", "📊 Slayd"])
def ask_topic(message):
    doc_type = message.text
    bot.send_message(message.chat.id, f"{doc_type} uchun mavzuni kiriting:")
    bot.register_next_step_handler(message, generate_ai_text, doc_type)

def generate_ai_text(message, doc_type):
    topic = message.text
    bot.send_message(message.chat.id, f"⏳ '{topic}' mavzusi bo‘yicha matn yaratilmoqda...")

    prompt = f"{doc_type} uchun {topic} mavzusida 2-3 sahifalik o‘zbek tilida batafsil matn yozing."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        text = response.choices[0].message.content
        send_file(message, doc_type, topic, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Xato yuz berdi: {e}")

def send_file(message, doc_type, topic, text):
    if doc_type in ["📄 Maqola", "📘 Mustaqil ish"]:
        doc = Document()
        doc.add_heading(topic, 0)
        doc.add_paragraph(text)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        bot.send_document(message.chat.id, buffer, visible_file_name=f"{topic}.docx")

    elif doc_type == "📊 Slayd":
        prs = Presentation()
        slides = text.split("\n\n")
        for i, content in enumerate(slides[:10]):
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = slide.shapes.title
            body = slide.placeholders[1]
            title.text = f"{topic} — Slayd {i+1}"
            body.text = content.strip()
        buffer = BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        bot.send_document(message.chat.id, buffer, visible_file_name=f"{topic}.pptx")

    bot.send_message(message.chat.id, "✅ Tayyor! Fayl yuborildi.")

bot.polling(non_stop=True)
