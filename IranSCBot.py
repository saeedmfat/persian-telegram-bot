import random
from typing import Final
import requests
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from decouple import config
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TOKEN: Final = config("TELEGRAM_TOKEN")
WEATHER_API_KEY: Final = config("WEATHER_API_KEY")
NEWS_API_KEY: Final = config("NEWS_API_KEY")  # Add your NewsAPI key here

# Fetch weather data with error handling
def get_weather(city: str) -> str:
    """Fetch weather information from WeatherAPI."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=fa"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'current' in data:
            weather_description = data['current']['condition']['text']
            temperature = data['current']['temp_c']
            humidity = data['current']['humidity']
            wind_speed = data['current']['wind_kph']
            
            weather_info = (
                f"آب و هوای {city.capitalize()}:\n"
                f"توضیحات: {weather_description}\n"
                f"دمای هوا: {temperature}°C\n"
                f"رطوبت: {humidity}%\n"
                f"سرعت باد: {wind_speed} کیلومتر/ساعت"
            )
            return weather_info
        else:
            return "متاسفم، اطلاعاتی درباره آب و هوای این شهر موجود نیست. لطفاً نام شهر را بررسی کنید و دوباره امتحان کنید."
    
    except requests.exceptions.Timeout:
        logger.error("WeatherAPI request timed out.")
        return "سرویس آب و هوا زمان زیادی برای پاسخ صرف کرد. لطفاً بعداً دوباره امتحان کنید."
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code}")
        return "خطایی در ارتباط با سرور آب و هوا رخ داده است. لطفاً بعداً دوباره امتحان کنید."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "متاسفم، خطایی رخ داده است. لطفاً بعداً دوباره امتحان کنید."

# Fetch a random joke from JokeAPI
def fetch_joke() -> str:
    """Fetch a random joke from JokeAPI."""
    url = "https://v2.jokeapi.dev/joke/Any"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("type") == "single":
            return data["joke"]
        elif data.get("type") == "twopart":
            return f'{data["setup"]} - {data["delivery"]}'
        else:
            return "Sorry, I couldn't find a joke right now. Try again later."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching joke: {e}")
        return "متاسفم، نتوانستم یک جوک پیدا کنم. لطفاً بعداً دوباره امتحان کنید."

# Fetch random news about AI and programming
def fetch_news() -> str:
    """Fetch random news articles about AI and programming using NewsAPI."""
    url = f"https://newsapi.org/v2/everything?q=AI OR programming&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        if articles:
            article = random.choice(articles)  # Pick a random article
            title = article.get("title", "عنوان نامشخص")
            description = article.get("description", "توضیحات موجود نیست.")
            url = article.get("url", "")
            
            news_info = (
                f"📢 خبر درباره AI و برنامه‌نویسی:\n\n"
                f"عنوان: {title}\n"
                f"توضیحات: {description}\n"
                f"لینک: {url}"
            )
            return news_info
        else:
            return "متاسفم، خبری درباره AI یا برنامه‌نویسی پیدا نشد."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return "متاسفم، خطایی در دریافت خبرها رخ داده است. لطفاً بعداً دوباره امتحان کنید."

# Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text('سلام! من ربات IranSC هستم. خوش آمدید!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    await update.message.reply_text('برای گرفتن اطلاعات آب و هوا، از دستور /weather <نام شهر> استفاده کنید. برای شنیدن یک جوک، از دستور /joke استفاده کنید! برای اخبار AI و برنامه‌نویسی، دستور /news را امتحان کنید!')

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /weather <city> command."""
    if context.args:
        city = " ".join(context.args)  # Get the city name from user input
    else:
        await update.message.reply_text("لطفاً نام یک شهر را وارد کنید. مثال: /weather تهران")
        return
    
    attempts = 3
    for attempt in range(attempts):
        weather_info = get_weather(city)
        if "متاسفم" not in weather_info:
            break
        elif attempt < attempts - 1:
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)
        else:
            logger.error("All attempts to fetch weather data failed.")
    
    await update.message.reply_text(weather_info)

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /joke command using JokeAPI."""
    joke = fetch_joke()  # Fetch a random joke
    await update.message.reply_text(joke)

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /news command using NewsAPI."""
    news = fetch_news()  # Fetch a random news article
    await update.message.reply_text(news)

def main():
    """Sets up and starts the bot."""
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('weather', weather_command))
    app.add_handler(CommandHandler('joke', joke_command))  # Add joke command handler
    app.add_handler(CommandHandler('news', news_command))  # Add news command handler

    # Set command descriptions
    commands = [
        BotCommand("start", "شروع گفتگو با ربات"),
        BotCommand("help", "دریافت راهنما"),
        BotCommand("weather", "دریافت اطلاعات آب و هوا برای یک شهر"),
        BotCommand("joke", "شنیدن یک جوک تصادفی"),
        BotCommand("news", "دریافت اخبار درباره AI و برنامه‌نویسی"),
    ]
    app.bot.set_my_commands(commands)

    logger.info("Bot is running...")
    app.run_polling(timeout=30, read_timeout=30, connect_timeout=30)

# Entry Point
if __name__ == '__main__':
    main()
