from tg_bot.bot import bot
from tg_bot.config import settings
from scheduler.celery_worker import celery_app


@celery_app.task
def create_group_topic(training_name: str, creator_username: str):
    """Celery task to create a new forum topic in Telegram"""
    import asyncio

    loop = asyncio.get_event_loop()

    async def send_request():
        topic = await bot.create_forum_topic(
            chat_id=settings.TG_FREE_GROUP_ID, name=f"{training_name} | {creator_username}"
        )
        print(">- " * 30, topic)  # TODO: Add topic id into Course record

    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(send_request())
