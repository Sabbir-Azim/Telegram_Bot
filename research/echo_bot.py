import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN is missing in .env file")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY is missing in .env file")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


@dp.message_handler(commands=['start', 'help'])
async def command_start_handler(message: types.Message):
    """
    This handler receives messages with `/start` or `/help`
    """
    await message.reply("👋 Hi, I am your AI Chatbot!\nJust send me a message and I'll reply using OpenAI 🚀")


@dp.message_handler()
async def chatgpt_handler(message: types.Message):
    """
    This handler sends user messages to OpenAI and replies back
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": message.text},
            ],
        )

        content = getattr(response.choices[0].message, "content", None)
        if response and response.choices and content is not None:
            reply_text = content.strip()
        else:
            reply_text = "⚠️ Sorry, no response from OpenAI."

        # ✅ Reply back to user
        await message.answer(reply_text)

    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        await message.answer("❌ Sorry, I couldn't process your request right now.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)