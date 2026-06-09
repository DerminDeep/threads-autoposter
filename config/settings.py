import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_IDS = [
    int(id.strip())
    for id in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',')
    if id.strip()
]

THREADS_API_BASE = 'https://graph.threads.net/v1.0'

META_APP_ID = os.getenv('META_APP_ID')
META_APP_SECRET = os.getenv('META_APP_SECRET')
THREADS_REDIRECT_URI = os.getenv('THREADS_REDIRECT_URI', 'http://localhost:8080/callback')

PUBLISH_METHOD = os.getenv('PUBLISH_METHOD', 'api')
CLOAKBROWSER_CDP_URL = os.getenv('CLOAKBROWSER_CDP_URL', 'http://localhost:9222')

AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')
AI_BASE_URL = os.getenv('AI_BASE_URL', 'http://localhost:11434/v1')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_MODEL = os.getenv('AI_MODEL', 'llama3')
AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', '120'))
AI_PERSONA_PATH = os.getenv('AI_PERSONA_PATH', 'config/prompts/persona.md')
AI_SKILLS_DIR = os.getenv('AI_SKILLS_DIR', 'config/skills')

DEFAULT_POSTS_PER_DAY = int(os.getenv('DEFAULT_POSTS_PER_DAY', '3'))
DEFAULT_POST_TIMES = [
    time.strip()
    for time in os.getenv('DEFAULT_POST_TIMES', '10:00,15:00,20:00').split(',')
]

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

Path('data').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)
