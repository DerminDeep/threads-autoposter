from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable
from database.models import getPendingPosts, updatePostStatus, claimPost
from core.threads import getPublisher
from utils.logger import logger

class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.publisher = getPublisher()

    async def start(self):
        self.scheduler.add_job(
            self.processPendingPosts,
            'interval',
            seconds=30,
            id='process_posts',
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60
        )
        self.scheduler.start()
        logger.info('Scheduler started (checking every 30s)')

    async def stop(self):
        self.scheduler.shutdown()
        logger.info('Scheduler stopped')

    async def processPendingPosts(self):
        try:
            posts = await getPendingPosts(limit=10)

            if not posts:
                return

            logger.info(f'Processing {len(posts)} pending posts')

            for post in posts:
                await self.publishPost(post)

        except Exception as e:
            logger.error(f'Error processing pending posts: {e}')

    async def publishPost(self, post: dict):
        postId = post['id']
        content = post['content']
        topic = post.get('topic', '')
        scheduled_time = post.get('scheduledTime')

        try:
            if not await claimPost(postId):
                logger.info(f'Post {postId} уже обрабатывается, пропускаем')
                return

            logger.info(f'Publishing post {postId}...')

            threadsPostId = await self.publisher.publish(content)

            if threadsPostId:
                await updatePostStatus(postId, 'published', threadsPostId)
                logger.success(f'Post {postId} published: {threadsPostId}')

                if scheduled_time:
                    await self._notifyPublished(postId, content, topic)
            else:
                await updatePostStatus(postId, 'failed')
                logger.error(f'Post {postId} failed to publish')

        except Exception as e:
            logger.error(f'Error publishing post {postId}: {e}')
            await updatePostStatus(postId, 'failed')

    async def _notifyPublished(self, postId: int, content: str, topic: str):
        """Отправляет уведомление в Telegram о публикации запланированного поста"""
        try:
            from bot.tgbot import bot
            from config.settings import TELEGRAM_ADMIN_IDS

            message = (
                f"✅ *Запланированный пост опубликован!*\n\n"
                f"*Тема:* {topic}\n"
                f"*ID поста:* {postId}\n\n"
                f"*Содержание:*\n{content}"
            )

            for admin_id in TELEGRAM_ADMIN_IDS:
                try:
                    await bot.bot.send_message(admin_id, message, parse_mode='Markdown')
                except Exception as e:
                    logger.warning(f"Не удалось отправить уведомление админу {admin_id}: {e}")

        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление о публикации: {e}")

    def addSchedule(self, hour: int, minute: int, callback: Callable):
        self.scheduler.add_job(
            callback,
            CronTrigger(hour=hour, minute=minute),
            id=f'daily_{hour}_{minute}',
            replace_existing=True
        )
        logger.info(f'Added daily schedule: {hour:02d}:{minute:02d}')

    def removeSchedule(self, scheduleId: str):
        try:
            self.scheduler.remove_job(scheduleId)
            logger.info(f'Removed schedule: {scheduleId}')
        except Exception as e:
            logger.error(f'Error removing schedule: {e}')

scheduler = Scheduler()
