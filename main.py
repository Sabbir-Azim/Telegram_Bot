import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize API clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing OPENAI_API_KEY or TELEGRAM_BOT_TOKEN in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)

# Model to use
MODEL_NAME = "gpt-3.5-turbo"


class ConversationMemory:
    """Class to manage conversation history with OpenAI."""

    def __init__(self) -> None:
        self.previous_response: str = ""

    def clear(self) -> None:
        """Reset conversation history."""
        self.previous_response = ""


memory = ConversationMemory()


# --- Command Handlers --- #
@dispatcher.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    """Send a welcome message when user starts the bot."""
    await message.reply(
        "👋 Hi, I am your AI Assistant Bot!\n"
        "Created by Sabbir.\n\n"
        "Type your message, and I’ll respond.\n"
        "Use /help to see available commands."
    )


@dispatcher.message_handler(commands=["help"])
async def handle_help(message: types.Message):
    """Provide list of available commands."""
    help_text = (
        "🤖 *Available Commands:*\n\n"
        "/start - Start the conversation\n"
        "/clear - Clear past conversation and context\n"
        "/help - Show this help menu\n"
    )
    await message.reply(help_text, parse_mode="Markdown")


@dispatcher.message_handler(commands=["clear"])
async def handle_clear(message: types.Message):
    """Clear previous conversation and context."""
    memory.clear()
    await message.reply("✅ Conversation history cleared.")


# --- Chat Handler --- #
@dispatcher.message_handler()
async def handle_chat(message: types.Message):
    """Process user input and generate AI response."""
    user_input = message.text.strip()
    logging.info(f"User ({message.from_user.id}): {user_input}")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "assistant", "content": memory.previous_response},
                {"role": "user", "content": user_input},
            ],
        )

        bot_reply = response.choices[0].message.content.strip()
        memory.previous_response = bot_reply  # Store last response

        logging.info(f"ChatGPT Response: {bot_reply}")
        await message.answer(bot_reply)

    except Exception as e:
        logging.error(f"Error while processing message: {e}", exc_info=True)
        await message.reply("⚠️ Sorry, something went wrong while processing your request.")


# --- Main Entry Point --- #
if __name__ == "__main__":
    logging.info("🚀 Starting Telegram bot...")
    executor.start_polling(dispatcher, skip_updates=True)
