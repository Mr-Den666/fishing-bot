import json
import datetime
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = "7169725825:AAGXk23HS97bzP8Sau8BHlGa5eXLFbkKI7I"
WEATHER_API_KEY = "14d291053160882096c5fc6690932b8c"

USERS_FILE = "users.json"
REGIONS_FILE = "regions.json"
TIPS_FILE = "tips.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_tips():
    try:
        with open(TIPS_FILE, "r", encoding="utf-8") as f:
            tips = json.load(f)
            return tips if isinstance(tips, list) and tips else ["(Поради з’являться пізніше)"]
    except FileNotFoundError:
        return ["(Поради з’являться пізніше)"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.effective_user.id)
    lang = users.get(user_id, {}).get("language", "ua")
    users[user_id] = users.get(user_id, {})
    users[user_id]["language"] = lang
    save_users(users)

    keyboard = [[
        "🎣 Дізнатися кльов" if lang == "ua" else "🎣 Check Bite",
        "💡 Корисні підказки" if lang == "ua" else "💡 Tips"
    ], [
        "📄 Інструкція" if lang == "ua" else "📄 Instructions",
        "⚙️ Налаштування" if lang == "ua" else "⚙️ Settings"
    ]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome = (
        "👋 Привіт! Я бот, який підкаже, чи сьогодні добре клює риба в обраному місті України 🎣.\n\n"
        "✅ Я вмію:\n"
        "— Показувати, чи буде гарний кльов\n"
        "— Давати прогноз на сьогодні або до 6 днів\n"
        "— Працювати по всіх областях України\n\n"
        "Вибери дію з меню нижче 👇"
    ) if lang == "ua" else (
        "👋 Hi! I'm a bot that tells you if the fish are biting in your selected Ukrainian city 🎣.\n\n"
        "✅ I can:\n"
        "— Show bite forecast\n"
        "— Give forecast for today or next 6 days\n"
        "— Work in all Ukrainian regions\n\n"
        "Choose an action from the menu 👇"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.effective_user.id)
    lang = users.get(user_id, {}).get("language", "ua")

    help_text = (
      "📄 Інструкція користувача\n\n"
        "Привіт 👋\nЯ – телеграм-бот, що підкаже, чи сьогодні гарний день для риболовлі 🎣\n\n"
        "🔹 Основні функції:\n"
        "— Дізнайся, чи клює риба у твоєму місті\n"
        "— Обирай область, місто та день (сьогодні або наступні 6 днів)\n"
        "— Отримай прогноз кльову на основі погоди (температура, вітер, тиск)\n"
        "— Враховується і фаза місяця 🌙\n\n"
        "🔹 Як користуватись:\n"
        "1. Натисни «🎣 Дізнатися кльов»\n"
        "2. Обери область → місто → день\n"
        "3. Отримай прогноз і пораду\n\n"
        "🔹 Команди:\n"
        "/start – Почати роботу з ботом\n"
        "/help – Інструкція та список можливостей\n"
        "/bite – Відкрити прогноз кльову вручну\n"
        "/settings – Налаштування мови та теми\n"
        "/idea — корисна порада\n\n"
        "🔹 Додаткові кнопки:\n"
        "💡 Корисні підказки – Дасть випадкову пораду\n"
        "⚙️ Налаштування – вибір мови та теми\n"
        "📄 Інструкція – повернутися до цієї сторінки\n\n"
        "🔁 Якщо ти вже користувався ботом — просто натисни кнопку з минулим містом!\n\n"
        "Гарного кльову! 🎣"
    ) if lang == "ua" else (
         "📄 User Guide\n\n"
        "Hi 👋\nI'm a Telegram bot that tells you if today is good for fishing 🎣\n\n"
        "🔹 Key features:\n"
        "— Find out if the fish are biting in your city\n"
        "— Choose a region, city, and day (today or up to the next 6 days)\n"
        "— Get a forecast based on weather (temperature, wind, pressure)\n"
        "— Moon phase 🌙 is also considered\n\n"
        "🔹 How to use:\n"
        "1. Tap '🎣 Check Bite'\n"
        "2. Choose region → city → day\n"
        "3. Receive forecast and advice\n\n"
        "🔹 Commands:\n"
        "/start – Start using the bot\n"
        "/help – Instructions and feature list\n"
        "/bite – Open bite forecast manually\n"
        "/settings – Change language and theme\n"
        "/idea — get a random fishing tip\n\n"
        "🔹 Extra buttons:\n"
        "💡 Tips – random fishing tip\n"
        "⚙️ Settings – language and theme options\n"
        "📄 Instructions – show this guide again\n\n"
        "🔁 If you've used the bot before — just tap the last city button!\n\n"
        "Happy fishing! 🎣"
    )
    await update.message.reply_text(help_text)

def load_tips():
    try:
        with open(TIPS_FILE, "r", encoding="utf-8") as f:
            tips = json.load(f)
            if isinstance(tips, list) and tips:
                return tips
    except Exception:
        pass
    return ["Поради недоступні."]

async def idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = load_tips()
    tip = random.choice(tips)
    await update.message.reply_text(tip)
    
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang|ua"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("⚪ Світла тема", callback_data="theme|light"),
         InlineKeyboardButton("⚫ Темна тема", callback_data="theme|dark")]
    ]
    await update.message.reply_text("⚙️ Налаштування:" if str(update.effective_user.id) not in load_users() or load_users()[str(update.effective_user.id)].get("language", "ua") == "ua" else "⚙️ Settings:", reply_markup=InlineKeyboardMarkup(keyboard))

async def bite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.effective_user.id)
    user_data = users.get(user_id, {})
    lang = user_data.get("language", "ua")

    with open(REGIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    region_names = list(data.keys())
    keyboard = []

    if "region" in user_data and "city" in user_data:
        last_btn = InlineKeyboardButton(f"🔁 {user_data['region']}, {user_data['city']}", callback_data="last")
        keyboard.append([last_btn])

    keyboard += [
        [InlineKeyboardButton(region_names[i], callback_data=f"region|{region_names[i]}"),
         InlineKeyboardButton(region_names[i + 1], callback_data=f"region|{region_names[i + 1]}")]
        for i in range(0, len(region_names) - 1, 2)
    ]

    if len(region_names) % 2 != 0:
        keyboard.append([InlineKeyboardButton(region_names[-1], callback_data=f"region|{region_names[-1]}")])

    await update.message.reply_text("Оберіть область:" if lang == "ua" else "Choose a region:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")

    users = load_users()
    user_id = str(query.from_user.id)
    if user_id not in users:
        users[user_id] = {}

    with open(REGIONS_FILE, "r", encoding="utf-8") as f:
        regions = json.load(f)

    lang = users[user_id].get("language", "ua")

    if data[0] == "region":
        region = data[1]
        users[user_id]["region"] = region
        keyboard = [[InlineKeyboardButton(city, callback_data=f"city|{city}")]
                    for city in regions[region]]
        await query.edit_message_text((f"Область: {region}\nОберіть місто:" if lang == "ua" else f"Region: {region}\nChoose a city:"),
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    elif data[0] == "city":
        city = data[1]
        users[user_id]["city"] = city
        keyboard = [
            [InlineKeyboardButton("Сьогодні" if lang == "ua" else "Today", callback_data="day|0")],
            [InlineKeyboardButton("Завтра" if lang == "ua" else "Tomorrow", callback_data="day|1")],
            [InlineKeyboardButton("Через 2 дні" if lang == "ua" else "In 2 days", callback_data="day|2")],
            [InlineKeyboardButton("Через 3 дні" if lang == "ua" else "In 3 days", callback_data="day|3")],
            [InlineKeyboardButton("Через 4 дні" if lang == "ua" else "In 4 days", callback_data="day|4")],
            [InlineKeyboardButton("Через 5 днів" if lang == "ua" else "In 5 days", callback_data="day|5")]
        ]
        await query.edit_message_text((f"Місто: {city}\nОберіть день:" if lang == "ua" else f"City: {city}\nChoose a day:"),
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    elif data[0] == "last":
        region = users[user_id].get("region")
        city = users[user_id].get("city")
        keyboard = [
            [InlineKeyboardButton("Сьогодні" if lang == "ua" else "Today", callback_data="day|0")],
            [InlineKeyboardButton("Завтра" if lang == "ua" else "Tomorrow", callback_data="day|1")],
            [InlineKeyboardButton("Через 2 дні" if lang == "ua" else "In 2 days", callback_data="day|2")],
            [InlineKeyboardButton("Через 3 дні" if lang == "ua" else "In 3 days", callback_data="day|3")],
            [InlineKeyboardButton("Через 4 дні" if lang == "ua" else "In 4 days", callback_data="day|4")],
            [InlineKeyboardButton("Через 5 днів" if lang == "ua" else "In 5 days", callback_data="day|5")]
        ]
        await query.edit_message_text((f"Останнє місто: {region}, {city}\nОберіть день:" if lang == "ua" else f"Last city: {region}, {city}\nChoose a day:"),
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    elif data[0] == "day":
        day_offset = int(data[1])
        region = users[user_id].get("region")
        city = users[user_id].get("city")
        result = get_weather_and_bite(city, day_offset, lang)
        await query.edit_message_text(f"🎣 {region}, {city}:\n\n{result}")

    elif data[0] == "lang":
        users[user_id]["language"] = data[1]
        save_users(users)
        await start(update, context)
        return

    elif data[0] == "theme":
        users[user_id]["theme"] = data[1]
        await query.edit_message_text("Тему змінено ✅" if lang == "ua" else "Theme changed ✅")

    save_users(users)

def get_weather_and_bite(city, day_offset, lang="ua"):
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},UA&appid={WEATHER_API_KEY}&units=metric&lang=ua"
    response = requests.get(forecast_url)
    data = response.json()

    if "list" not in data or "city" not in data:
        return "Не вдалося отримати прогноз або координати." if lang == "ua" else "Could not retrieve forecast."

    target_date = (datetime.datetime.now() + datetime.timedelta(days=day_offset)).date()

    temps = []
    winds = []
    pressures = []
    descriptions = []

    for entry in data["list"]:
        dt = datetime.datetime.fromtimestamp(entry["dt"])
        if dt.date() == target_date:
            temps.append(entry["main"]["temp"])
            winds.append(entry["wind"]["speed"])
            pressures.append(entry["main"]["pressure"])
            descriptions.append(entry["weather"][0]["description"])

    if not temps:
        return "Немає погодних даних на цей день." if lang == "ua" else "No weather data available."

    avg_temp = sum(temps) / len(temps)
    avg_wind = sum(winds) / len(winds)
    avg_pressure = sum(pressures) / len(pressures)
    main_desc = max(set(descriptions), key=descriptions.count)

    score = 0
    if 15 <= avg_temp <= 25:
        score += 1
    if avg_wind <= 4:
        score += 1
    if "дощ" not in main_desc:
        score += 1
    if 1005 <= avg_pressure <= 1025:
        score += 1

    if score >= 4:
        status = "🟢 Чудово клює!" if lang == "ua" else "🟢 Great bite!"
    elif 2 <= score < 4:
        status = "🟡 Посередній кльов" if lang == "ua" else "🟡 Average bite"
    else:
        status = "🔴 Погано клює" if lang == "ua" else "🔴 Poor bite"

    return (
        f"{status}\n\n"
        f"🌡 Температура: {avg_temp:.1f}°C\n"
        f"💨 Вітер: {avg_wind:.1f} м/с\n"
        f"🧭 Тиск: {avg_pressure:.1f} гПа\n"
        f"☁️ Погода: {main_desc}"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = str(update.effective_user.id)
    users = load_users()
    lang = users.get(user_id, {}).get("language", "ua")

    if "привіт" in text or "hello" in text:
        await update.message.reply_text("Привіт-привіт 👋" if lang == "ua" else "Hello 👋")
    elif "як справи" in text or "how are you" in text:
        await update.message.reply_text("Працюю, як годинник ⏰" if lang == "ua" else "Working like clockwork ⏰")
    elif "кльов" in text or "bite" in text:
        await bite_command(update, context)
    elif "налаштування" in text or "settings" in text:
        await settings_command(update, context)
    elif "інструкція" in text or "instruction" in text:
        await help_command(update, context)
    elif "підказки" in text or "tips" in text:
        await idea_command(update, context)
    else:
        await update.message.reply_text("Вибери дію з меню нижче 👇" if lang == "ua" else "Choose an action from the menu 👇")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("bite", bite_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    main()
