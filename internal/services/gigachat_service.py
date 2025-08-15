import aiohttp
import asyncio
from internal.config.config import GIGACHAT_AUTH, GIGACHAT_SCOPE, GIGACHAT_URL

_cached_token = None

SYSTEM_PROMPT = (
    "Ты - эксперт по трудовому праву РФ."
    "Отвечай строго по Трудовому кодексу РФ. "
    "Если вопрос не относится к трудовому законодательству РФ, "
    "отвечай: '🛑 Извините, я могу консультировать только по трудовому законодательству РФ.\n"
    "Если вы уверены что ваш вопрос относится к законодательству РФ, "
    "попробуйте очистить историю /clear и снова задать вопрос.'"
)


async def get_access_token(force_refresh: bool = False):
    global _cached_token
    if _cached_token and not force_refresh:
        return _cached_token

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Authorization": f"Basic {GIGACHAT_AUTH}",
        "RqUID": "123e4567-e89b-12d3-a456-426614174000",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"scope": GIGACHAT_SCOPE}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data, ssl=False) as resp:
            result = await resp.json()
            _cached_token = result.get("access_token")
            return _cached_token


async def ask_gigachat(question: str, chat_history: list[dict]) -> str:
    print("[INFO] Создаю ответ пользователю...")

    async def _send_request(token: str):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in chat_history[-5:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})

        messages.append({"role": "user", "content": question})

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(15):
                async with session.post(f"{GIGACHAT_URL}/chat/completions", headers=headers, json={"model": "GigaChat", "messages": messages}, ssl=False) as resp:
                    if resp.status == 401:
                        return None
                    return await resp.json()

    token = await get_access_token()

    result = await _send_request(token)
    if result is None:
        token = await get_access_token(force_refresh=True)
        result = await _send_request(token)
    if not result:
        print("[WARN] Не удалось получить ответ от GigaChat!")
        return "🛑 Не удалось получить ответ от GigaChat."

    try:
        answer = result["choices"][0]["message"]["content"]
        print(f"[INFO] Получен ответ от GigaChat: {answer}")
    except (KeyError, IndexError):
        print("[WARN] Ошибка при обработке ответа от GigaChat!")
        return "🛑 Ошибка при обработке ответа от GigaChat."

    is_valid = await _validate_answer(answer)
    print(f"[INFO] Вердикт валидатора: {is_valid}")
    if not is_valid:
        print("[INFO] Некорректный ответ от GigaChat")
        return ("🛑 Извините, я могу консультировать только по трудовому законодательству РФ.\n"
                "Если вы уверены что ваш вопрос относится к законодательству РФ, "
                "попробуйте очистить историю /clear и снова задать вопрос.")

    return answer


async def _validate_answer(answer: str) -> bool:
    validation_prompt = (
        "Ты эксперт по трудовому праву РФ. "
        "Проверь следующий текст и ответь только 'Да' или 'Нет', "
        "относится ли он к трудовому законодательству РФ:\n\n"
        f"{answer}"
    )

    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GIGACHAT_URL}/chat/completions",
            headers=headers,
            json={"model": "GigaChat", "messages": [{"role": "user", "content": validation_prompt}]},
            ssl=False
        ) as resp:
            if resp.status != 200:
                return False
            data = await resp.json()

    try:
        result_text = data["choices"][0]["message"]["content"].lower()
        return "да" in result_text
    except (KeyError, IndexError):
        return False