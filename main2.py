import telebot
import os
import random
import string
import requests
from groq import Groq
from telebot import types
from deep_translator import GoogleTranslator
from urllib.parse import quote

# Подключение Google Drive
try:
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)
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

eco_tips = [
    "Сегодня попробуй не брать в магазине пакет, если у тебя не много покупок.",
    "Выключай воду, пока чистишь зубы — это экономит до 10 литров в минуту.",
    "Старайся использовать многоразовую бутылку для воды вместо пластиковых.",
    "Сдавай батарейки в специальные пункты приема, не выбрасывай их в общий мусор.",
    "Выключай свет в комнатах, где никого нет.",
    "Используйте обе стороны листа бумаги при печати или письме.",
    "Предпочитайте душ вместо принятия ванны, чтобы сэкономить воду.",
    "Выбирайте товары с минимальной упаковкой.",
    "Отдавайте предпочтение местным продуктам — это снижает транспортный след.",
    "Вынимайте зарядные устройства из розеток, когда они не используются."
]

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
    markup.add("🌍 Эко-статус")
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
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}! 👋", reply_markup=get_main_menu())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = "❓ **Доступные команды:**\n/start - Запустить бота\n/help - Показать это сообщение\n/help_world - Эко-статус\n/mem, /mem1, /mem2 - Отправить мем\n/duck - Случайная уточка\n\n**Функции меню:**\n💬 Интеллект-чат - ИИ ассистент\n🎨 ИИ-рисование - Генерация картинок\n🔐 Безопасность - Пароли\n📅 Планы - Список задач\n🌍 Эко-статус - Советы по экологии"
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['help_world'])
@bot.message_handler(func=lambda m: m.text == "🌍 Эко-статус")
def help_world(message):
    try:
        res = requests.get("https://api.climateclock.world/v1/clock", timeout=10)
        data = res.json()['data']['modules']['carbon_deadline_1']
        years = data['timestamp'].split('T')[0]
        status_text = f"🌍 **Экологические часы (New York):**\nДо критического порога осталось до: `{years}`\n\n🌱 **Совет:** {random.choice(eco_tips)}"
    except:
        status_text = f"🌱 **Эко-совет дня:**\n{random.choice(eco_tips)}"
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back_to_main(message):
    reset_modes(message.from_user.id)
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == "💬 Интеллект-чат")
def chat_mode(message):
    reset_modes(message.from_user.id)
    get_storage(message.from_user.id)['ai_mode'] = True
    bot.send_message(message.chat.id, "🤖 Чат активен.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад"))

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

@bot.message_handler(commands=['mem', 'mem1', 'mem2'])
def send_mems(message):
    ext = 'png' if message.text == '/mem' else ('webp' if message.text == '/mem1' else 'jpg')
    cmd = 'mem' if message.text == '/mem' else ('mem1' if message.text == '/mem1' else 'mem2')
    try:
        path = os.path.join(IMAGE_PATH, f"{cmd}.{ext}")
        with open(path, 'rb') as f: bot.send_photo(message.chat.id, f)
    except: bot.send_message(message.chat.id, "Файл не найден.")

@bot.message_handler(commands=['duck'])
def duck(message):
    try:
        image_url = get_duck_image_url()
        bot.reply_to(message, image_url)
    except: bot.send_message(message.chat.id, "Уточка уплыла...")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid = message.from_user.id
    storage = get_storage(uid)
    if message.text in ["💬 Интеллект-чат", "🎨 ИИ-рисование", "🔐 Безопасность", "📅 Планы", "⬅️ Назад", "🌍 Эко-статус"]: return

    if storage['ai_mode']:
        try:
            res = client_groq.chat.completions.create(model=MODEL_NAME, messages=[{"role":"system","content":sys_model_rules},{"role":"user","content":message.text}])
            bot.send_message(message.chat.id, res.choices[0].message.content)
        except: bot.send_message(message.chat.id, "Ошибка ИИ.")

    elif storage['image_mode']:
        bot.send_message(message.chat.id, "🎨 Принято! Рисую...")
        try:
            translated_text = translator.translate(message.text)
            image_url = f"https://image.pollinations.ai/prompt/{quote(translated_text)}?width=1024&height=1024&model=flux&nologo=true"
            bot.send_photo(message.chat.id, image_url, caption="Готово!")
        except: bot.send_message(message.chat.id, "Ошибка генерации.")

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
    print("🚀 Бот запущен...")
    bot.infinity_polling()
