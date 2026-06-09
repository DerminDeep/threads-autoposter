from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config.settings import TELEGRAM_BOT_TOKEN
from bot.handlers import router
from utils.logger import logger

class TelegramBot:
    def __init__(self):
        self.bot = None
        self.dp = Dispatcher()
        self.dp.include_router(router)

    async def _setCommands(self):
        commands = [
            BotCommand(command="login", description="Авторизация в Threads"),
            BotCommand(command="post", description="Создать и опубликовать пост"),
            BotCommand(command="schedule", description="Запланировать пост"),
            BotCommand(command="topics", description="Список тем"),
            BotCommand(command="addtopic", description="Добавить тему"),
            BotCommand(command="queue", description="Очередь постов"),
            BotCommand(command="stats", description="Статистика"),
            BotCommand(command="settings", description="Настройки"),
            BotCommand(command="cancel", description="Отменить действие"),
            BotCommand(command="help", description="Помощь"),
        ]
        await self.bot.set_my_commands(commands)
        logger.success("Bot commands set")

    async def start(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error('TELEGRAM_BOT_TOKEN not set in .env')
            return

        logger.info('Starting Telegram bot...')

        try:
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)

            botInfo = await self.bot.get_me()
            logger.success(f'Telegram bot started: @{botInfo.username} (ID: {botInfo.id})')

            await self._setCommands()
            await self.bot.delete_webhook(drop_pending_updates=True)
            await self.dp.start_polling(self.bot)

        except Exception as e:
            logger.error(f'Failed to start Telegram bot: {e}')
            raise

    async def stop(self):
        logger.info('Stopping Telegram bot...')
        if self.bot:
            await self.bot.session.close()
        logger.info('Telegram bot stopped')

bot = TelegramBot()
