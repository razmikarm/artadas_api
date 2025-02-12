from aiogram import Bot, Dispatcher

from tg_bot.config import settings

from tg_bot.handlers import router


bot = Bot(token=settings.TG_BOT_TOKEN)
dp = Dispatcher()

# Register Aiogram handlers
dp.include_router(router)
