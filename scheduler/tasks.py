from tg_bot.bot import bot
from tg_bot.config import settings
from scheduler.celery_worker import celery_app


@celery_app.task
def create_group_topic(training_name: str, creator_username: str):
    """Celery task to create a new forum topic in Telegram"""
    import asyncio

    async def send_request():
        topic = await bot.create_forum_topic(
            chat_id=settings.TG_STUDENT_GROUP_ID, name=f"{training_name} | {creator_username}"
        )
        print(">- " * 30, topic)

    asyncio.run(send_request())
