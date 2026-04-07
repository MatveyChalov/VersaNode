import telebot
import random
import string
import os
from telebot import types

# --- CONFIG ---
TOKEN = "ТОКЕН"
bot = telebot.TeleBot(TOKEN)
USER_DB_FILE = "user_ids.txt"

# --- DB HELPERS ---
def save_user(user_id):
    if not os.path.exists(USER_DB_FILE): open(USER_DB_FILE, 'w').close()
    with open(USER_DB_FILE, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")

# --- MEMORY ---
tasks = []
passwords = []
game_sessions = {}

# --- MENUS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🌟 Нейросеть", "🔐 Безопасность")
    markup.add("🎮 Игры", "📅 Дела")
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    save_user(message.chat.id)
    welcome_text = (
        f"Здравствуйте, {message.from_user.first_name}. Вас приветствует VersaNode.\n\n"
        "Система активна. Доступные команды:\n/start — Меню\n/help — Справка."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# --- NEURAL NETWORK (WITH HINT) ---
@bot.message_handler(func=lambda m: m.text == "🌟 Нейросеть")
def neuro_stub(message):
    bot.send_message(
        message.chat.id,
        "Уважаемый пользователь, раздел «Нейросеть» на модернизации. Если Вы внимательно изучите слово МАЙ, Вы поймете точное число релиза. Ожидайте."
    )

# --- SECURITY (WITH LABELS) ---
@bot.message_handler(func=lambda m: m.text == "🔐 Безопасность")
def safety_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🆕 Создать пароль", "📜 История паролей", "🔙 Назад")
    bot.send_message(message.chat.id, "Система безопасности:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🆕 Создать пароль")
def ask_pass_label(message):
    msg = bot.send_message(message.chat.id, "Введите название ресурса (например, ВК):")
    bot.register_next_step_handler(msg, finalize_pass_gen)

def finalize_pass_gen(message):
    label = message.text
    p = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
    entry = f"{label}: `{p}`"
    passwords.append(entry)
    bot.send_message(message.chat.id, f"Данные сохранены:\n{entry}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📜 История паролей")
def pass_hist(message):
    res = "Архив идентификаторов:\n" + "\n".join(passwords) if passwords else "Архив пуст."
    bot.send_message(message.chat.id, res, parse_mode="Markdown")

# --- GAMES (PLAYER VS BOT) ---
@bot.message_handler(func=lambda m: m.text == "🚢 Морской Бой")
def sea_battle_init(message):
    player_ships = random.sample(range(25), 3)
    bot_ships = random.sample(range(25), 3)
    game_sessions[message.chat.id] = {
        'bot_ships': bot_ships,
        'player_ships': player_ships,
        'player_hits': [],
        'bot_hits': [],
        'turn': 'player'
    }
    render_sea_battle(message.chat.id, "Ваш ход! Найдите 3 корабля бота:")

def render_sea_battle(chat_id, text, message_id=None):
    s = game_sessions.get(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=5)
    btns = []
    for i in range(25):
        label = "🌊"
        if i in s['player_hits']:
            label = "💥" if i in s['bot_ships'] else "💦"
        btns.append(types.InlineKeyboardButton(label, callback_data=f"sb_{i}"))
    markup.add(*btns)
    if message_id: bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sb_'))
def sea_battle_click(call):
    s = game_sessions.get(call.message.chat.id)
    if not s or s['turn'] != 'player': return
    idx = int(call.data.split('_')[1])
    if idx in s['player_hits']: return

    s['player_hits'].append(idx)
    if idx in s['bot_ships']:
        msg = "💥 Вы попали!"
    else:
        msg = "💦 Мимо."
        s['turn'] = 'bot'

    found = len([h for h in s['player_hits'] if h in s['bot_ships']])
    if found == 3:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🏆 ПОБЕДА! Все корабли противника обнаружены. Поздравляем! 🎉")
        return

    if s['turn'] == 'bot':
        bot_move(call.message.chat.id, call.message.message_id)
    else:
        render_sea_battle(call.message.chat.id, f"{msg} Ваш ход! (Найдено: {found}/3)", call.message.message_id)

def bot_move(chat_id, message_id):
    s = game_sessions.get(chat_id)
    available = [i for i in range(25) if i not in s['bot_hits']]
    move = random.choice(available)
    s['bot_hits'].append(move)
    if move in s['player_ships']:
        bot_move(chat_id, message_id)
    else:
        s['turn'] = 'player'
        render_sea_battle(chat_id, f"Бот сходил в сектор {move+1} и промахнулся. Ваш ход!", message_id)

@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back(message): bot.send_message(message.chat.id, "Меню:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🎮 Игры")
def g_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚢 Морской Бой", "🔙 Назад")
    bot.send_message(message.chat.id, "Выберите игру:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📅 Дела")
def t_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Внести задачу", "📜 Список задач", "🔙 Назад")
    bot.send_message(message.chat.id, "Задачи:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📜 Список задач")
def todo_list(message):
    res = "Задачи:\n- " + "\n- ".join(tasks) if tasks else "Пусто."
    bot.send_message(message.chat.id, res)

@bot.message_handler(func=lambda m: m.text == "➕ Внести задачу")
def todo_add(message):
    msg = bot.send_message(message.chat.id, "Суть задачи:")
    bot.register_next_step_handler(msg, lambda m: [tasks.append(m.text), bot.send_message(m.chat.id, "Ок.")])

if __name__ == "__main__":
    bot.polling(none_stop=True)
