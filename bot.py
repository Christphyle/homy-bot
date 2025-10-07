import os
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# === Logs ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# === Chemins ===
BASE_DIR = Path(__file__).resolve().parent
TARIFFS_FILE = BASE_DIR / "tarifs.txt"

# === Helpers ===
def load_token() -> str:
    t = os.getenv("BOT_TOKEN")
    if t:
        return t.strip()
    with open(BASE_DIR / "token.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def read_tarifs_text() -> str:
    """Lit tarifs.txt (UTF-8). Renvoie un message de secours en cas d'erreur."""
    try:
        text = TARIFFS_FILE.read_text(encoding="utf-8").strip()
        if not text:
            return "Тарифы временно недоступны. Попробуйте позже."
        return text
    except FileNotFoundError:
        logging.warning("Файл тарифов не найден: %s", TARIFFS_FILE)
        return "Тарифы временно недоступны. Свяжитесь с администратором."
    except Exception as e:
        logging.exception("Ошибка чтения тарифов: %s", e)
        return "Произошла ошибка при загрузке тарифов."

# === Bot / Dispatcher ===
TOKEN = load_token()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Clavier ===
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Тарифы"), KeyboardButton(text="📅 Запись")],
        [KeyboardButton(text="📍 Адрес"), KeyboardButton(text="✉️ Контакт")]
    ],
    resize_keyboard=True
)

# === Handlers ===
@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "Привет! Это бот Homy Studio.\n"
        "Выберите действие ниже или используйте команды: /tarifs, /rdv, /contact.",
        reply_markup=kb
    )

@dp.message(Command("tarifs"))
async def tarifs(m: Message):
    await m.answer(read_tarifs_text())

@dp.message(Command("rdv"))
async def rdv(m: Message):
    await m.answer(
        "Чтобы записаться, отправьте ваше <b>имя</b>, <b>телефон</b> и "
        "<b>желаемое время/направление</b> (например: «Ср 18:00, йога для новичков»)."
    )

@dp.message(Command("contact"))
async def contact(m: Message):
    await m.answer(
        "📍 <b>Адрес:</b> Ломоносовский просп., 29, корп. 2, Москва\n"
        "⏰ <b>Время работы:</b> 09:00–21:00\n"
        "Пишите нам прямо здесь — ответим как можно быстрее."
    )

# Boutons → mêmes handlers
@dp.message(F.text == "💰 Тарифы")
async def tarifs_btn(m: Message):
    await tarifs(m)

@dp.message(F.text == "📅 Запись")
async def rdv_btn(m: Message):
    await rdv(m)

@dp.message(F.text == "📍 Адрес")
async def addr_btn(m: Message):
    await contact(m)

@dp.message(F.text == "✉️ Контакт")
async def contact_btn(m: Message):
    await contact(m)

# === Main ===
async def main():
    me = await bot.get_me()
    logging.info(f"Запуск @{me.username} (long polling). Нажмите Ctrl+C для остановки.")

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="tarifs", description="Посмотреть тарифы"),
        BotCommand(command="rdv", description="Записаться на тренировку"),
        BotCommand(command="contact", description="Написать нам"),
    ])

    # (optionnel) descriptions
    try:
        await bot.set_my_short_description("Фитнес-студия: тарифы, запись и контакты.")
        await bot.set_my_description(
            "Homy Studio — тренировки, абонементы и персональные занятия. "
            "Адрес: Ломоносовский просп., 29, корп. 2, Москва. Время: 07:00–21:00."
        )
    except Exception as e:
        logging.debug(f"Не удалось установить описание: {e}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановлено.")
