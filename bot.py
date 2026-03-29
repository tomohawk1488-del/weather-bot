import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("WEATHER_KEY")

keyboard = [
    [KeyboardButton("📍 Моя погода", request_location=True)],
    [KeyboardButton("🌍 Ввести город")],
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери 👇", reply_markup=markup)

async def weather_city(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
    return requests.get(url).json()

async def send_weather(update, data, city):
    if not data.get("main"):
        await update.message.reply_text("❌ Город не найден")
        return

    msg = (
        f"📍 {city}\n"
        f"🌡 {data['main']['temp']}°C\n"
        f"🤔 Ощущается: {data['main']['feels_like']}°C\n"
        f"☁️ {data['weather'][0]['description']}"
    )
    await update.message.reply_text(msg)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌍 Ввести город":
        context.user_data["wait_city"] = True
        await update.message.reply_text("Напиши город:")
        return

    if context.user_data.get("wait_city"):
        data = await weather_city(text)
        await send_weather(update, data, text)
        context.user_data["wait_city"] = False

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    lon = update.message.location.longitude

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"
    data = requests.get(url).json()

    await send_weather(update, data, "Твоя локация")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, text_handler))
app.add_handler(MessageHandler(filters.LOCATION, location_handler))

print("Бот запущен")
app.run_polling()
