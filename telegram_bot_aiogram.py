from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram import Router
import asyncio
from datetime import datetime
import os

# ------------------------------
BOT_TOKEN = "7819901403:AAGbY15x2HiknkmWHUOqIj7hdXUs6STSGGo"   # Tokenni shu yerga yozing
ADMIN_ID = 5027912447              # Sizning admin ID
# ------------------------------

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
dp.include_router(router)

USERS_FILE = "users.txt"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return [int(line.strip()) for line in f.readlines()]

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        with open(USERS_FILE, "a") as f:
            f.write(str(user_id) + "\n")

USERS = load_users()

class Register(StatesGroup):
    ism = State()
    telfon = State()
    eshitdi = State()
    kurs = State()

class Reklama(StatesGroup):
    matn = State()

def contact_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Kontaktni yuborish", request_contact=True)]],
        resize_keyboard=True
    )

def eshitgan_btn():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Instagram"), KeyboardButton(text="✈ Telegram")],
            [KeyboardButton(text="🤝 Tanish orqali")]
        ],
        resize_keyboard=True
    )

def kurs_btn():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 1. Professional Buxgalteriya")],
            [KeyboardButton(text="💻 2. 1C Dasturi")],
            [KeyboardButton(text="⌨ 3. Kompyuter Savodxonligi")]
        ],
        resize_keyboard=True
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    save_user(message.from_user.id)
    await state.set_state(Register.ism)
    await message.answer("Assalomu alaykum! 😊\nIsm familiyangizni yozing:")


@router.message(Register.ism)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(ism=message.text)
    await state.set_state(Register.telfon)
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=contact_button())


@router.message(Register.telfon, F.contact)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(telfon=message.contact.phone_number)
    await state.set_state(Register.eshitdi)
    await message.answer("Qayerdan biz haqimizda eshitdingiz? 👇", reply_markup=eshitgan_btn())


@router.message(Register.eshitdi)
async def get_source(message: Message, state: FSMContext):
    await state.update_data(eshitdi=message.text)
    await state.set_state(Register.kurs)
    await message.answer("Qaysi kursni tanlaysiz? 🎓", reply_markup=kurs_btn())


@router.message(Register.kurs)
async def finish(message: Message, state: FSMContext):
    await state.update_data(kurs=message.text)
    data = await state.get_data()
    vaqt = datetime.now().strftime("%Y-%m-%d %H:%M")

    txt = f"""
📥 Yangi ariza:

👤 Ism: {data['ism']}
📞 Telefon: {data['telfon']}
📍 Qayerdan eshitgan: {data['eshitdi']}
🎓 Kurs: {data['kurs']}
🕒 Sana & vaqt: {vaqt}
"""

    await message.answer("✅ Arizangiz qabul qilindi!\n📞 Adminlar tez orada siz bilan bog‘lanadi 😊")
    await bot.send_message(ADMIN_ID, txt)

    await state.clear()


# === ADMIN REKLAMA ===
@router.message(Command("reklama"))
async def reklama_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Siz admin emassiz!")
    await message.answer("📣 Reklama matn, rasm, video yoki ovoz yuboring:")
    await state.set_state(Reklama.matn)


@router.message(Reklama.matn)
async def reklama_send(message: Message, state: FSMContext):
    users = load_users()
    count = 0

    for user in users:
        try:
            if message.content_type == ContentType.TEXT:
                await bot.send_message(user, message.text)

            elif message.content_type == ContentType.PHOTO:
                await bot.send_photo(user, message.photo[-1].file_id, caption=message.caption)

            elif message.content_type == ContentType.VIDEO:
                await bot.send_video(user, message.video.file_id, caption=message.caption)

            elif message.content_type == ContentType.VOICE:
                await bot.send_voice(user, message.voice.file_id)

            elif message.content_type == ContentType.DOCUMENT:
                await bot.send_document(user, message.document.file_id)

            count += 1
        except:
            pass

    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga yuborildi.")
    await state.clear()


async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
