from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
import aiohttp
import os
import logging
import asyncio

load_dotenv()

token = os.getenv('TOKKEN_BOT')

FAST_API = os.getenv('FAST_API')

bot = Bot(token=token)

dp = Dispatcher()

@dp.message()
async def postUser(message: types.Message):
    question = message.text

    payload  = {
        'prompt': question,
        'model': 'llama3'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(FAST_API, json=payload) as resp:
            data = await resp.json()
            answer = data.get('generated_text', 'Ошибка модели, модель не смогла обработать ваш запрос')
    await message.answer(answer)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
