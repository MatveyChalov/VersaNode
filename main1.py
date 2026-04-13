#!pip install pyTelegramBotAPI transformers torch diffusers accelerate deep-translator google-generativeai
#!pip install groq
#!pip install requests
import telebot
import os
import random
import string
import requests
from groq import Groq
from telebot import types
from deep_translator import GoogleTranslator
from google.colab import drive
from urllib.parse import quote

# Подключение Google Drive
try:
    drive.mount('/content/drive')
    print("✅ Google Drive подключен")
except Exception as e:
    print(f"❌ Ошибка подключения Drive: {e}")

# Конфигурация
TELEGRAM_TOKEN = ""
GROQ_API_KEY = ""
MODEL_NAME = "llama-3.3-70b-versatile"
IMAGE_PATH = ""

sys_model_rules = (
    "Вы — полезный и вежливый ИИ-ассистент. Ваш стиль общения: профессиональный, но естественный и дружелюбный. "
    "Используйте уважительное обращение на 'Вы'."
)

try:
    client_groq = Groq(api_key=GROQ_API_KEY)
    print("✅ Интеллектуальный модуль инициализирован")
except Exception as e:
    print(f"❌ Ошибка инициализации: {e}")
    client_groq = None

bot = telebot.TeleBot(TELEGRAM_TOKEN)
translator = GoogleTranslator(source='ru', target='en')
user_data = {}

def get_duck_image_url():
    url = 'https://random-d.uk/api/v2/random'
    res = requests.get(url)
    data = res.json()
    return data['url']

def get_storage(uid):
    if uid not in user_data:
        user_data[uid] = {
            'ai_mode': False, 'image_mode': False, 'sec_mode': False,
            'plan_mode': False, 'tasks': [], 'passwords': []
        }
    return user_data[uid]

def reset_modes(uid):
    storage = get_storage(uid)
    storage.update({'ai_mode': False, 'image_mode': False, 'sec_mode': False, 'plan_mode': False})

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💬 Интеллект-чат", "🎨 ИИ-рисование")
    markup.add("🔐 Безопасность", "📅 Планы")
    markup.add("❓ Справка")
    return markup

def get_sec_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Создать пароль", "📋 Список паролей")
    markup.add("⬅️ Назад")
    return markup

def get_plan_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить задачу", "📋 Список задач")
    markup.add("⬅️ Назад")
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    reset_modes(message.from_user.id)
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}! 👋\nЯ Ваш ассистент.", reply_markup=get_main_menu())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "❓ **Доступные команды:**\n\n"
        "/start - Запустить бота\n"
        "/help - Показать это сообщение\n"
        "/mem, /mem1, /mem2 - Отправить мем\n"
        "/duck - Случайная уточка\n\n"
        "**Функции меню:**\n"
        "💬 Интеллект-чат - Общение с ИИ\n"
        "🎨 ИИ-рисование - Генерация картинок\n"
        "🔐 Безопасность - Пароли\n"
        "📅 Планы - Список задач"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back_to_main(message):
    reset_modes(message.from_user.id)
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == "💬 Интеллект-чат")
def chat_mode(message):
    reset_modes(message.from_user.id)
    get_storage(message.from_user.id)['ai_mode'] = True
    bot.send_message(message.chat.id, "🤖 Чат активен. Жду Ваш вопрос!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад"))

@bot.message_handler(func=lambda m: m.text == "🎨 ИИ-рисование")
def image_mode(message):
    reset_modes(message.from_user.id)
    get_storage(message.from_user.id)['image_mode'] = True
    bot.send_message(message.chat.id, "🎨 Режим рисования. Что мне изобразить?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад"))

@bot.message_handler(func=lambda m: m.text == "🔐 Безопасность")
def sec_menu_call(message):
    bot.send_message(message.chat.id, "🔐 Раздел безопасности:", reply_markup=get_sec_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Создать пароль")
def sec_add_start(message):
    reset_modes(message.from_user.id)
    get_storage(message.from_user.id)['sec_mode'] = True
    bot.send_message(message.chat.id, "Введите название сервиса:")

@bot.message_handler(func=lambda m: m.text == "📋 Список паролей")
def sec_list(message):
    pwds = get_storage(message.from_user.id).get('passwords', [])
    text = "🔑 Ваши пароли:\n" + "\n".join(pwds) if pwds else "Список пуст."
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📅 Планы")
def plan_menu_call(message):
    bot.send_message(message.chat.id, "📅 Ваши планы:", reply_markup=get_plan_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Добавить задачу")
def plan_add_start(message):
    reset_modes(message.from_user.id)
    get_storage(message.from_user.id)['plan_mode'] = True
    bot.send_message(message.chat.id, "Что нужно записать?")

@bot.message_handler(func=lambda m: m.text == "📋 Список задач")
def plan_list(message):
    tasks = get_storage(message.from_user.id).get('tasks', [])
    text = "📌 Задачи:\n" + "\n".join([f"- {t}" for t in tasks]) if tasks else "Задач нет."
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['mem'])
def send_mem(message):
    try:
        path = os.path.join(IMAGE_PATH, 'mem.png')
        with open(path, 'rb') as f: bot.send_photo(message.chat.id, f)
    except: bot.send_message(message.chat.id, "Файл не найден.")

@bot.message_handler(commands=['mem1'])
def send_mem1(message):
    try:
        path = os.path.join(IMAGE_PATH, 'mem1.webp')
        with open(path, 'rb') as f: bot.send_photo(message.chat.id, f)
    except: bot.send_message(message.chat.id, "Файл не найден.")

@bot.message_handler(commands=['mem2'])
def send_mem2(message):
    try:
        path = os.path.join(IMAGE_PATH, 'mem2.jpg')
        with open(path, 'rb') as f: bot.send_photo(message.chat.id, f)
    except: bot.send_message(message.chat.id, "Файл не найден.")

@bot.message_handler(commands=['duck'])
def duck(message):
    '''По команде duck вызывает функцию get_duck_image_url и отправляет URL изображения утки'''
    image_url = get_duck_image_url()
    bot.reply_to(message, image_url)

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid = message.from_user.id
    storage = get_storage(uid)
    if message.text in ["💬 Интеллект-чат", "🎨 ИИ-рисование", "🔐 Безопасность", "📅 Планы", "➕ Создать пароль", "📋 Список паролей", "➕ Добавить задачу", "📋 Список задач", "⬅️ Назад"]: return

    if storage['ai_mode']:
        msg = bot.send_message(message.chat.id, "⏳...")
        try:
            res = client_groq.chat.completions.create(model=MODEL_NAME, messages=[{"role":"system","content":sys_model_rules},{"role":"user","content":message.text}])
            bot.edit_message_text(res.choices[0].message.content, message.chat.id, msg.message_id)
        except: bot.edit_message_text("Ошибка ИИ.", message.chat.id, msg.message_id)

    elif storage['image_mode']:
        bot.send_message(message.chat.id, "🎨 Принято! Секунду, рисую твой шедевр...")
        try:
            translated_text = translator.translate(message.text)
            image_url = f"https://image.pollinations.ai/prompt/{quote(translated_text)}?width=1024&height=1024&model=flux&nologo=true"
            bot.send_photo(message.chat.id, image_url, caption="Готово!")
        except:
            bot.send_message(message.chat.id, "Ошибка генерации.")

    elif storage['sec_mode']:
        new_pass = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=12))
        storage['passwords'].append(f"**{message.text}**: `{new_pass}`")
        bot.send_message(message.chat.id, f"🔐 Пароль для **{message.text}** создан!", reply_markup=get_sec_menu(), parse_mode='Markdown')
        storage['sec_mode'] = False

    elif storage['plan_mode']:
        storage['tasks'].append(message.text)
        bot.send_message(message.chat.id, f"📅 Задача зафиксирована!", reply_markup=get_plan_menu())
        storage['plan_mode'] = False

if __name__ == '__main__':
    bot.infinity_polling()
