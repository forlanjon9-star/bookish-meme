import telebot
import os
import tempfile
from docx import Document
from pptx import Presentation
from pptx.util import Pt, Inches
import textwrap
import logging

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")  # Render yoki boshqa joyda BOT_TOKEN sifatida qo'shing
if not TOKEN:
    logger.error("BOT_TOKEN environment variable not set. Exiting.")
    raise SystemExit("Please set BOT_TOKEN environment variable.")

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# --- Helper: generate 'content' for maqola/referat ---
def build_article_text(topic: str, approx_pages: int = 10):
    """
    Yaratuvchi funksiya: soddalashtirilgan maqola matni hosil qiladi.
    approx_pages — taxminiy sahifa soni (har bir sahifa ~ 450-500 soʻzga teng hisoblandi).
    Bu funksiya haqiqiy NLU model emas — shuning uchun struktura va bo'limlar bilan to'ldiradi.
    """
    # Har sahifada taxminan 450 so'z -> jami so'z = approx_pages * 450
    words_per_page = 450
    total_words = approx_pages * words_per_page

    # Strukturani belgilaymiz
    sections = [
        ("Kirish", 0.12),
        ("Adabiyot va tarixiy ma'lumot", 0.08),
        ("Asosiy qism: muammo tavsifi", 0.18),
        ("Asosiy qism: sabablar va tahlil", 0.18),
        ("Amaliy yechimlar va tavsiyalar", 0.18),
        ("Xulosa va kelajak uchun tavsiyalar", 0.12),
        ("Foydalanilgan adabiyotlar", 0.02),
    ]

    article = []
    used_words = 0
    for title, frac in sections:
        section_words = int(total_words * frac)
        used_words += section_words
        # Har bo'lim uchun bir nechta paragraf
        para_count = max(3, section_words // 120)
        article.append(f"{title}\n")
        for p in range(para_count):
            sent = generate_paragraph(topic, target_words=section_words // para_count)
            article.append(sent + "\n\n")

    # Agar so'zlar yetmasa, qo'shimcha fikrlar qo'shish
    if used_words < total_words:
        extra = generate_paragraph(topic, target_words=(total_words - used_words))
        article.append("Qo'shimcha izoh\n\n" + extra)

    return "\n".join(article)


def generate_paragraph(topic: str, target_words: int = 120):
    """Sodda paragraph generator — mavzu atrofida gaplar yaratadi."""
    # Bazaviy jumlalar kombinatsiyasi
    snippets = [
        f"{topic} mavzusi bugungi kunda katta e'tiborni tortmoqda.",
        "Mazkur masala nazariy va amaliy jihatlari bilan ahamiyatlidir.",
        "Muammoni tahlil qilish jarayonida bir qator muhim omillar aniqlanadi.",
        "Tadqiqot natijalari amaliy tavsiyalarni shakllantirishga yordam beradi.",
        "Ilgari olingan tajribalar va adabiyotlardan kelib chiqib, quyidagi xulosalar ishlab chiqildi.",
        "Shu bilan birga, kelgusida qoʻshimcha tadqiqotlar o‘tkazish zarur.",
        "Jarayonni optimallashtirish uchun bir qancha tavsiyalar berish mumkin.",
        "Har bir tadqiqotning uslubiy chegaralari mavjudligini eʼtiborga olish lozim."
    ]
    text = []
    words = 0
    i = 0
    while words < target_words:
        s = snippets[i % len(snippets)]
        # ozgina variant qo'shish
        if i % 3 == 0:
            s = s + " " + snippets[(i+1) % len(snippets)]
        text.append(s)
        words += len(s.split())
        i += 1
        if i > 200:
            break
    return " ".join(text)


# --- DOCX yaratish va saqlash ---
def create_docx(topic: str, pages: int = 10, title="Maqola"):
    doc = Document()
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].font.size = Pt(12)

    # sarlavha
    h = doc.add_heading(title, level=1)
    h.alignment = 1  # center if desired

    doc.add_paragraph(f"Mavzu: {topic}")
    doc.add_paragraph("Muallif: Avtomatlashtirilgan bot")
    doc.add_paragraph("")

    article_text = build_article_text(topic, approx_pages=pages)
    # bo'limlarni paragraf qilib qo'shamiz
    for block in article_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        # agar bu bo'lim sarlavhaga o'xshasa
        if "\n" not in block and len(block) < 60 and block.endswith(":") is False and len(block.split()) < 8:
            doc.add_heading(block, level=2)
        else:
            # broken to multiple lines
            for para in textwrap.wrap(block, width=100):
                doc.add_paragraph(para)
    # saqlash
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp.close()
    doc.save(tmp.name)
    return tmp.name


# --- PPTX yaratish va saqlash ---
def create_pptx(topic: str, slides_count: int = 10, title_prefix="Slayd"):
    prs = Presentation()
    # font size defaults
    for i in range(slides_count):
        # simple layout: title + content
        slide_layout = prs.slide_layouts[1]  # title + content
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        body = slide.shapes.placeholders[1].text_frame

        title.text = f"{topic} — Slayd {i+1}"

        # Add 3-5 bullet points
        bullets = [
            f"Asosiy nuqta {i+1}.1 — {topic}-ga oid tushuncha.",
            f"Asosiy nuqta {i+1}.2 — muhim tafsilotlar.",
            f"Asosiy nuqta {i+1}.3 — amaliy tavsiya yoki misol.",
        ]
        body.clear()
        for j, b in enumerate(bullets):
            p = body.add_paragraph() if j > 0 else body.paragraphs[0]
            p.text = b
            p.level = 0

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    tmp.close()
    prs.save(tmp.name)
    return tmp.name


# --- Handlers ---
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    txt = (
        "Salom! Men maqola va slayd yaratadigan botman.\n\n"
        "Buyruqlar:\n"
        "/maqola — 10 betlik maqola yaratish (bot sizdan mavzuni soʻraydi)\n"
        "/referat — qisqaroq referat (bot sizdan mavzuni soʻraydi)\n"
        "/slayd — 10 slayddan iborat PowerPoint (bot sizdan mavzuni soʻraydi)\n\n"
        "Masalan: /maqola\n"
        "So'ng bot sizdan mavzuni so'raydi."
    )
    bot.send_message(message.chat.id, txt)


# helper: ask topic then generate
def ask_topic_and_register(message, next_handler):
    msg = bot.send_message(message.chat.id, "Mavzuni kiriting (qisqacha):")
    bot.register_next_step_handler(msg, next_handler)


@bot.message_handler(commands=['maqola'])
def cmd_maqola(message):
    ask_topic_and_register(message, maqola_topic_handler)


def maqola_topic_handler(message):
    topic = message.text.strip()
    sending = bot.send_message(message.chat.id, f"'{topic}' mavzusi bo'yicha 10 betlik maqola tayyorlanyapti... Iltimos kuting.")
    try:
        path = create_docx(topic, pages=10, title=f"Maqola: {topic}")
        with open(path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"Maqola: {topic}")
    except Exception as e:
        logger.exception("Error creating/sending DOCX")
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
        bot.delete_message(sending.chat.id, sending.message_id)


@bot.message_handler(commands=['referat'])
def cmd_referat(message):
    ask_topic_and_register(message, referat_topic_handler)


def referat_topic_handler(message):
    topic = message.text.strip()
    sending = bot.send_message(message.chat.id, f"'{topic}' mavzusi bo'yicha referat tayyorlanyapti... Iltimos kuting.")
    try:
        path = create_docx(topic, pages=2, title=f"Referat: {topic}")
        with open(path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"Referat: {topic}")
    except Exception as e:
        logger.exception("Error creating/sending referat")
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
        bot.delete_message(sending.chat.id, sending.message_id)


@bot.message_handler(commands=['slayd'])
def cmd_slayd(message):
    ask_topic_and_register(message, slayd_topic_handler)


def slayd_topic_handler(message):
    topic = message.text.strip()
    sending = bot.send_message(message.chat.id, f"'{topic}' mavzusi bo'yicha 10 slayd tayyorlanyapti... Iltimos kuting.")
    try:
        path = create_pptx(topic, slides_count=10)
        with open(path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"Slayd: {topic}")
    except Exception as e:
        logger.exception("Error creating/sending PPTX")
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
        bot.delete_message(sending.chat.id, sending.message_id)


# small echo for debug
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.text and message.text.startswith("/"):
        # Unknown command
        bot.send_message(message.chat.id, "Noto'g'ri buyruq. /help bilan ko'proq ma'lumot oling.")
    else:
        bot.send_message(message.chat.id, "Mavzuni yuborish uchun /maqola, /referat yoki /slayd buyrug'ini ishlating.")


# --- Start polling ---
if __name__ == "__main__":
    logger.info("Bot ishga tushdi. Polling boshlanmoqda...")
    # Note: on hosting like Render you may need worker/background service
    bot.infinity_polling(timeout=60, long_polling_timeout = 60)
