import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Токени боти шумо
TOKEN = "8782383492:AAFUh9OKDbBj1iVmRfBe73bp0nC_K9CsqYY"
ADMIN_ID = 8863442172

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_player_id = State()
    waiting_for_receipt = State()

# Фармони /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛒 Мағоза")
    builder.button(text="👤 Профил")
    builder.button(text="📞 Дастгирӣ")
    builder.adjust(2, 1)

    await message.answer(
        f"Салом, {message.from_user.full_name}!\n\n"
        "🔥 **UC Shop TJ** — беҳтарин боти донат дар Тоҷикистон.\n"
        "⬇️ Менюи асосӣ дар поёни экран дастрас аст:",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(F.text == "🛒 Мағоза")
async def open_shop(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Харидани UC", callback_data="buy_uc")
    builder.adjust(1)

    await message.answer(
        "📦 **Категорияи мағозаро интихоб кунед:**",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(F.text == "👤 Профил")
async def open_profile(message: types.Message):
    await message.answer(
        f"👤 **Маълумоти профили шумо:**\n\n"
        f"• Ном: {message.from_user.full_name}\n"
        f"• ID-и Телеграм: `{message.from_user.id}`",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(F.text == "📞 Дастгирӣ")
async def open_support(message: types.Message):
    await message.answer(
        "📞 Барои тамос бо администратор ба ин линк муроҷиат кунед: https://t.me/Niyozov_Sayfullo"
    )

# Нишон додани тугмаҳои пакетҳои UC
@dp.callback_query(F.data == "buy_uc")
async def process_buy_uc(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 60 UC - 10 сомонӣ", callback_data="uc_60")
    builder.button(text="💎 325 UC - 50 сомонӣ", callback_data="uc_325")
    builder.button(text="💎 660 UC - 95 сомонӣ", callback_data="uc_660")
    builder.adjust(1)

    await callback.message.edit_text(
        "📦 **Бастаҳои мавҷудаи UC-ро интихоб кунед:**",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()

# Кор бо интихоби пакети мушаххас
@dp.callback_query(F.data.startswith("uc_"))
async def process_package_choice(callback: types.CallbackQuery, state: FSMContext):
    package_data = callback.data
    
    if package_data == "uc_60":
        package_name = "60 UC (10 сомонӣ)"
    elif package_data == "uc_325":
        package_name = "325 UC (50 сомонӣ)"
    elif package_data == "uc_660":
        package_name = "660 UC (95 сомонӣ)"
    else:
        package_name = "Номаълум"

    # Захира кардани пакет дар ҳолат (FSM)
    await state.update_data(package=package_name)

    await callback.message.edit_text(
        f"✅ Шумо интихоб кардед: **{package_name}**\n\n"
        "🎮 Лутфан **Player ID**-и PUBG-и худро нависед (масалан: `5123456789`):",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(OrderState.waiting_for_player_id)
    await callback.answer()

# Қабули Player ID
@dp.message(OrderState.waiting_for_player_id)
async def process_player_id(message: types.Message, state: FSMContext):
    player_id = message.text
    await state.update_data(player_id=player_id)

    await message.answer(
        f"✅ Player ID-и шумо қабул шуд: `{player_id}`\n\n"
        "💳 **Маълумот барои пардохт:**\n"
        "Корти Алиф/Спитамен: `9999 0000 1111 2222` (Номи Админ)\n\n"
        "📸 Лутфан акси чеки пардохтро ба ин ҷо фиристед!",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(OrderState.waiting_for_receipt)

# Қабули чеки пардохт ва фиристодан ба админ бо маълумоти пакет
@dp.message(OrderState.waiting_for_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    player_id = data.get("player_id")
    package = data.get("package")
    user = message.from_user

    await message.answer(
        "🎉 **Фармоиши шумо бо муваффақият қабул шуд!**\n\n"
        f"📦 Пакет: {package}\n"
        f"🎮 Player ID: `{player_id}`\n"
        "⏳ Администратор чеки шуморо месанҷад ва ба зудӣ UC ба ҳисоби шумо илова мешавад.",
        parse_mode=ParseMode.MARKDOWN
    )

    username_str = f"@{user.username}" if user.username else "Ном надорад"

    admin_text = (
        f"🔔 **ФАРМОИШИ НАВ!**\n\n"
        f"👤 Харидор: {user.full_name} ({username_str})\n"
        f"🆔 Telegram ID: `{user.id}`\n"
        f"📦 Пакет: **{package}**\n"
        f"🎮 PUBG Player ID: `{player_id}`"
    )

    photo_file_id = message.photo[-1].file_id

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_file_id,
        caption=admin_text,
        parse_mode=ParseMode.MARKDOWN
    )

    await state.clear()

@dp.message(OrderState.waiting_for_receipt)
async def wrong_receipt(message: types.Message):
    await message.answer("⚠️ Лутфан танҳо **акси чеки пардохтро** фиристед!")

async def main():
    print("Бот бо интихоби тугмаҳои пакетҳо ба кор даромад...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
