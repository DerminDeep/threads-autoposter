import sys
import warnings


if sys.platform == 'win32':
    warnings.filterwarnings('ignore', category=ResourceWarning)
    warnings.filterwarnings('ignore', message='unclosed transport')
    warnings.filterwarnings('ignore', message='I/O operation on closed pipe')

import asyncio
from pathlib import Path
from database.models import initDb
from bot.tgbot import bot
from core.scheduler import scheduler
from core.browser_launcher import shutdownBrowser
from utils.logger import logger
from utils.i18n import setLang


def saveLang(lang: str):
    """Save selected language to .lang file"""
    Path('.lang').write_text(lang, encoding='utf-8')


def selectLanguage():
    """Select language, load from file or ask user"""
    langPath = Path('.lang')
    if langPath.exists():
        savedLang = langPath.read_text(encoding='utf-8').strip()
        if savedLang in ('en', 'ru'):
            setLang(savedLang)
            return savedLang


    print("\n🌍 Select language / Выберите язык:")
    print("1. English")
    print("2. Русский")

    while True:
        choice = input("\n> ").strip()
        if choice in ('1', 'en', 'english'):
            setLang('en')
            saveLang('en')
            return 'en'
        elif choice in ('2', 'ru', 'russian', 'русский'):
            setLang('ru')
            saveLang('ru')
            return 'ru'
        else:
            print("Please enter 1 or 2 / Введите 1 или 2")


def loadEnv():
    """Load environment variables from .env file"""
    env = {}
    envPath = Path('.env')
    if envPath.exists():
        with open(envPath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value
    return env


def validateConfig():
    """Validate required configuration before starting bot"""
    from utils.i18n import t
    env = loadEnv()

    required = {
        'TELEGRAM_BOT_TOKEN': t('cli', 'error_token'),
        'TELEGRAM_ADMIN_IDS': t('cli', 'error_admin_ids'),
    }

    missing = []
    for key, error_msg in required.items():
        if not env.get(key):
            missing.append(error_msg)

    publish_method = env.get('PUBLISH_METHOD', 'api')
    if publish_method == 'api':
        if not env.get('META_APP_ID'):
            missing.append(t('cli', 'error_meta_app_id'))
        if not env.get('META_APP_SECRET'):
            missing.append(t('cli', 'error_meta_app_secret'))

    if missing:
        print("\n❌ Configuration errors:")
        for error in missing:
            print(f"  - {error}")
        print(f"\n{t('cli', 'run_setup_hint')}\n")
        return False

    return True

async def shutdown():
    logger.info('Shutting down...')
    await scheduler.stop()
    await bot.stop()
    await shutdownBrowser()
    logger.info('Shutdown complete')

async def main():
    lang = selectLanguage()
    logger.info(f'Selected language: {lang}')

    logger.info('Starting Threads AutoPoster...')
    await initDb()
    logger.info('Database initialized')
    await scheduler.start()

    stopEvent = asyncio.Event()
    logger.info('Application running. Press Ctrl+C to stop.')
    botTask = asyncio.create_task(bot.start())

    try:
        while not stopEvent.is_set():
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info('Received Ctrl+C')
    finally:
        botTask.cancel()
        try:
            await botTask
        except asyncio.CancelledError:
            pass
        await shutdown()

def _silenceProactorErrors(hook_args):
    exc_type = hook_args.exc_type
    exc_value = hook_args.exc_value
    if exc_type is ValueError and exc_value and 'I/O operation on closed pipe' in str(exc_value):
        return
    if exc_type is ResourceWarning:
        return
    sys.__unraisablehook__(hook_args)


if __name__ == '__main__':
    sys.unraisablehook = _silenceProactorErrors

    envPath = Path('.env')
    needSetup = '--setup' in sys.argv or not envPath.exists()

    if needSetup:
        try:
            from core.setup_cli import runSetup
            if not runSetup():
                print('Setup cancelled. Exiting.')
                sys.exit(0)
        except KeyboardInterrupt:
            print('\nSetup cancelled. Exiting.')
            sys.exit(0)

    if not validateConfig():
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Application stopped by user')
