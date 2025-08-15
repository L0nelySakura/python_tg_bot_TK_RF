from aiogram import Router, types
from aiogram.filters import Command
from internal.config.config import HISTORY_LIMIT
from internal.services.gigachat_service import ask_gigachat
from internal.services.db_service import save_message, get_history, clear_history

router = Router()


@router.message(Command("clear"))
async def clear_user_history(message: types.Message):
    user_id = message.from_user.id
    await clear_history(user_id)
    print(f"[INFO] Очищена история чата для пользователя {user_id}")
    await message.answer("✅ История чата очищена.")
    await message.answer(
        "🤖 Здравствуйте! Я - бот-консультант по ТК РФ.\n"
        "📜 Задайте мне вопрос, и я дам ответ \n"
        "Если вы желаете очистить 'историю' чата, то нажмите на /clear"
    )


@router.message()
async def handle_question(message: types.Message):
    user_id = message.from_user.id
    print(f"[INFO] Получено сообщение от {user_id}: {message.text}")
    history = await get_history(user_id, limit=HISTORY_LIMIT)

    processing_msg = await message.answer("⌛ Обрабатываю ваш запрос, подождите...")

    answer = await ask_gigachat(message.text, history)
    if answer is not ("🛑 Извините, я могу консультировать только по трудовому законодательству РФ.\n"
                      "Если вы уверены что ваш вопрос относится к законодательству РФ, "
                      "попробуйте очистить историю /clear и снова задать вопрос."):
        try:
            print(f"[INFO] Сохраняю вопрос и ответ в базу данных...")
            await save_message(user_id, "user", message.text)
            await save_message(user_id, "ai", answer)
            print(f"[INFO] Сохранение успешно.")
        except Exception as e:
            print(f"[WARN] Произошла ошибка во время записи: {e}")

    await processing_msg.edit_text(answer)
