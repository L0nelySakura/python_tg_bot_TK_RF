from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🤖 Здравствуйте! Я - бот-консультант по ТК РФ.\n"
        "📜 Задайте мне вопрос, и я дам ответ \n"
        "Если вы желаете очистить 'контекст' чата, то нажмите на /clear"
    )
