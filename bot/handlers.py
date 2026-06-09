import asyncio
import aiofiles
import webbrowser
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.models import addPost, updatePostStatus, getTopics, addTopic, getStats, getPendingPosts, setSetting
from core.generator import ContentGenerator
from utils.logger import logger
from utils.i18n import t

router = Router()
generator = ContentGenerator()


def getBackButton() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=t('bot', 'back_to_menu'), callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

_loginPage = None
_loginAgent = None
_pendingPosts = {}


class LoginStates(StatesGroup):
    waitingLoginMethod = State()
    waitingOAuthCode = State()
    waitingUsername = State()
    waitingPassword = State()
    waitingTwoFA = State()


class PostStates(StatesGroup):
    waitingTopic = State()
    waitingApproval = State()
    waitingEdit = State()


class ScheduleStates(StatesGroup):
    waitingTopic = State()
    waitingTime = State()
    waitingApproval = State()


class AddtopicStates(StatesGroup):
    waitingName = State()


class PersonaStates(StatesGroup):
    waitingEdit = State()
    waitingMode = State()


def isAuthorized(userId: int) -> bool:
    from config.settings import TELEGRAM_ADMIN_IDS
    return userId in TELEGRAM_ADMIN_IDS


async def isThreadsAuthorized() -> bool:
    from database.models import getSetting
    from config.settings import PUBLISH_METHOD

    activeMethod = await getSetting('active_publish_method', PUBLISH_METHOD)

    browserAuthorized = await getSetting('browser_authorized')
    if browserAuthorized == 'true':
        if activeMethod == 'browser' or PUBLISH_METHOD == 'browser':
            return True

    if PUBLISH_METHOD == 'api':
        accessToken = await getSetting('threads_access_token')
        return accessToken is not None

    return False


async def _sendScreenshot(message: Message, screenshotData: bytes, caption: str = ""):
    try:
        photo = BufferedInputFile(screenshotData, filename="screenshot.png")
        await message.answer_photo(photo=photo, caption=caption)
    except Exception as e:
        logger.error(f"Send screenshot error: {e}")


def getMainMenu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=t('bot', 'menu_btn_post'), callback_data="menu_post")],
        [InlineKeyboardButton(text=t('bot', 'menu_btn_schedule'), callback_data="menu_schedule"),
         InlineKeyboardButton(text=t('bot', 'menu_btn_topics'), callback_data="menu_topics")],
        [InlineKeyboardButton(text=t('bot', 'menu_btn_stats'), callback_data="menu_stats"),
         InlineKeyboardButton(text=t('bot', 'menu_btn_queue'), callback_data="menu_queue")],
        [InlineKeyboardButton(text=t('bot', 'menu_btn_login'), callback_data="menu_login"),
         InlineKeyboardButton(text=t('bot', 'menu_btn_settings'), callback_data="menu_settings")],
        [InlineKeyboardButton(text=t('bot', 'menu_btn_persona'), callback_data="menu_persona"),
         InlineKeyboardButton(text=t('bot', 'menu_btn_skills'), callback_data="menu_skills")],
        [InlineKeyboardButton(text=t('bot', 'menu_btn_help'), callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def getLoginMethodKeyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=t('bot', 'login_oauth_btn'), callback_data="login_oauth")],
        [InlineKeyboardButton(text=t('bot', 'login_browser_btn'), callback_data="login_browser")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def startOAuthCallbackServer():
    from aiohttp import web
    import os

    auth_code = None
    auth_event = asyncio.Event()

    async def handle_callback(request):
        nonlocal auth_code
        auth_code = request.query.get('code')
        if auth_code:
            auth_event.set()
            return web.Response(text=t('bot', 'oauth_callback_success'))
        else:
            error = request.query.get('error', 'unknown')
            return web.Response(text=t('bot', 'oauth_callback_error', error))

    app = web.Application()
    app.router.add_get('/callback', handle_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    return runner, auth_event, lambda: auth_code


async def saveOauthTokensToDb(userId: str, accessToken: str):
    from database.models import setSetting
    await setSetting('threads_user_id', userId)
    await setSetting('threads_access_token', accessToken)
    logger.info(f"OAuth tokens saved to database for user {userId}")


async def sendMainMenu(message: Message):
    await message.answer(t('bot', 'welcome'), parse_mode='Markdown', reply_markup=getMainMenu())


@router.message(Command('start'))
async def startCommand(message: Message):
    logger.info(f'Received /start from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        logger.warning(f'Unauthorized access attempt: {message.from_user.id}')
        return

    await sendMainMenu(message)


@router.callback_query(F.data == "menu_back")
async def menuBackCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        t('bot', 'welcome'),
        parse_mode='Markdown',
        reply_markup=getMainMenu()
    )


@router.callback_query(F.data == "menu_post")
async def menuPostCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(t('bot', 'post_enter_topic'), reply_markup=getBackButton())
    await state.set_state(PostStates.waitingTopic)


@router.callback_query(F.data == "menu_schedule")
async def menuScheduleCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(t('bot', 'schedule_enter_topic'), reply_markup=getBackButton())
    await state.set_state(ScheduleStates.waitingTopic)


@router.callback_query(F.data == "menu_queue")
async def menuQueueCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    posts = await getPendingPosts(limit=20)
    if not posts:
        await callback.message.answer(t('bot', 'menu_queue_empty'), reply_markup=getBackButton())
        return

    text = f'*{t("bot", "menu_queue_header")} ({len(posts)}):*\n\n'
    for post in posts:
        scheduled = t('bot', 'queue_scheduled', post["scheduledTime"]) if post.get('scheduledTime') else ''
        text += f'• ID {post["id"]}: {post["content"][:50]}...{scheduled}\n'
    await callback.message.answer(text, parse_mode='Markdown', reply_markup=getBackButton())


@router.callback_query(F.data == "menu_login")
async def menuLoginCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(t('bot', 'menu_login'), reply_markup=getBackButton())


@router.callback_query(F.data == "menu_persona")
async def menuPersonaCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    from pathlib import Path
    personaPath = Path('config/prompts/persona.md')
    if not personaPath.exists():
        await callback.message.answer(t('bot', 'persona_not_found'), reply_markup=getBackButton())
        return

    content = personaPath.read_text(encoding='utf-8')
    if len(content) > 4000:
        content = content[:4000] + t('bot', 'persona_truncated')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t('bot', 'persona_edit'), callback_data="persona_edit")],
        [InlineKeyboardButton(text=t('bot', 'back_to_menu'), callback_data="menu_back")]
    ])

    await callback.message.answer(
        f'{t("bot", "persona_current")}\n\n```markdown\n{content}\n```',
        parse_mode='Markdown',
        reply_markup=keyboard
    )


@router.callback_query(F.data == "persona_edit")
async def personaEditCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from pathlib import Path
    personaPath = Path('config/prompts/persona.md')

    currentContent = ''
    if personaPath.exists():
        currentContent = personaPath.read_text(encoding='utf-8')

    await state.update_data(currentContent=currentContent)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t('bot', 'persona_append_mode'), callback_data="persona_mode:append")],
        [InlineKeyboardButton(text=t('bot', 'persona_replace_mode'), callback_data="persona_mode:replace")],
        [InlineKeyboardButton(text=t('bot', 'back_to_menu'), callback_data="menu_back")]
    ])

    await callback.message.answer(t('bot', 'persona_edit_choice'), reply_markup=keyboard)


@router.callback_query(F.data == "persona_mode:append")
async def personaAppendMode(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    currentContent = data.get('currentContent', '')

    if currentContent:
        await callback.message.answer(t('bot', 'persona_append_prompt', currentContent))
    else:
        await callback.message.answer(t('bot', 'persona_edit_prompt'))

    await state.update_data(mode='append')
    await state.set_state(PersonaStates.waitingEdit)


@router.callback_query(F.data == "persona_mode:replace")
async def personaReplaceMode(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(t('bot', 'persona_edit_prompt'))
    await state.update_data(mode='replace')
    await state.set_state(PersonaStates.waitingEdit)


@router.message(StateFilter(PersonaStates.waitingEdit))
async def processPersonaEdit(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    from pathlib import Path
    personaPath = Path('config/prompts/persona.md')
    personaPath.parent.mkdir(parents=True, exist_ok=True)

    data = await state.get_data()
    mode = data.get('mode', 'replace')
    currentContent = data.get('currentContent', '')

    if mode == 'append' and currentContent:
        newContent = currentContent.rstrip() + '\n\n' + message.text
    else:
        newContent = message.text

    personaPath.write_text(newContent, encoding='utf-8')

    await message.answer(t('bot', 'persona_saved'))
    await state.clear()


@router.callback_query(F.data == "menu_skills")
async def menuSkillsCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    from pathlib import Path
    from config.settings import AI_SKILLS_DIR

    skillsDir = Path(AI_SKILLS_DIR)
    if not skillsDir.exists():
        await callback.message.answer(t('bot', 'skills_dir_not_found'), reply_markup=getBackButton())
        return

    skills = list(skillsDir.glob('*.md'))
    if not skills:
        await callback.message.answer(t('bot', 'skills_empty'), reply_markup=getBackButton())
        return

    text = t('bot', 'skills_header') + '\n\n'
    for skill in skills:
        content = skill.read_text(encoding='utf-8')
        lines = content.split('\n')
        name = skill.stem
        description = ''
        for line in lines:
            if line.startswith('# '):
                description = line[2:].strip()
                break
        text += f'• *{name}*: {description}\n'

    text += t('bot', 'skills_hint')
    await callback.message.answer(text, parse_mode='Markdown', reply_markup=getBackButton())


@router.callback_query(F.data == "menu_topics")
async def menuTopicsCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    topics = await getTopics()
    if not topics:
        await callback.message.answer(t('bot', 'menu_topics_empty'), reply_markup=getBackButton())
    else:
        text = f'*{t("bot", "menu_topics_header")}*\n\n' + '\n'.join([f'• {topic}' for topic in topics])
        await callback.message.answer(text, parse_mode='Markdown', reply_markup=getBackButton())


def _buildStatsText(stats: dict) -> str:
    diff = stats['today'] - stats['yesterday']
    trend = '📈' if diff > 0 else '📉' if diff < 0 else '➡️'
    trendText = t('bot', 'stats_yesterday_trend', trend=trend, diff=diff) if stats['yesterday'] > 0 else ''

    text = (
        f'{t("bot", "stats_title")}\n\n'
        f'*{t("bot", "stats_total")}* {stats["total"]}\n'
        f'✅ {t("bot", "stats_published")} {stats["published"]}\n'
        f'⏳ {t("bot", "stats_pending")} {stats["pending"]}\n'
        f'❌ {t("bot", "stats_failed")} {stats["failed"]}\n'
        f'📈 {t("bot", "stats_success_rate")} {stats["successRate"]}%\n\n'
        f'*{t("bot", "stats_today")}* {stats["today"]}{trendText}\n'
        f'*{t("bot", "stats_yesterday_label")}* {stats["yesterday"]}\n\n'
        f'{t("bot", "stats_activity")}\n'
    )

    maxBars = 8
    for date, count in stats['weekly']:
        bars = '█' * min(count, maxBars)
        text += f'`{date}` {bars} {count}\n'

    return text


def _buildSettingsText() -> str:
    from config.settings import AI_BASE_URL, AI_MODEL, PUBLISH_METHOD, DEFAULT_POSTS_PER_DAY, DEFAULT_POST_TIMES
    text = (
        f'{t("bot", "settings_header")}\n\n'
        f'`{t("bot", "settings_ai_url")}` `{AI_BASE_URL}`\n'
        f'`{t("bot", "settings_model")}` `{AI_MODEL}`\n'
        f'`{t("bot", "settings_method")}` `{PUBLISH_METHOD}`\n'
        f'`{t("bot", "settings_posts_per_day")}` `{DEFAULT_POSTS_PER_DAY}`\n'
        f'`{t("bot", "settings_times")}` `{", ".join(DEFAULT_POST_TIMES)}`'
    )
    return text


@router.callback_query(F.data == "menu_stats")
async def menuStatsCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    stats = await getStats()
    text = _buildStatsText(stats)
    await callback.message.answer(text, parse_mode='Markdown', reply_markup=getBackButton())


@router.callback_query(F.data == "menu_settings")
async def menuSettingsCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    text = _buildSettingsText()
    await callback.message.answer(text, parse_mode='Markdown', reply_markup=getBackButton())


@router.callback_query(F.data == "menu_help")
async def menuHelpCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(t('bot', 'menu_help'), parse_mode='Markdown', reply_markup=getBackButton())


@router.message(Command('help'))
async def helpCommand(message: Message):
    logger.info(f'Received /help from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return
    await startCommand(message)


@router.message(Command('login'))
async def loginCommand(message: Message, state: FSMContext):
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    from database.models import getSetting
    from config.settings import PUBLISH_METHOD

    await state.set_state(LoginStates.waitingLoginMethod)

    oauthToken = await getSetting('threads_access_token')
    browserAuth = await getSetting('browser_authorized')
    activeMethod = await getSetting('active_publish_method', PUBLISH_METHOD)

    oauthLabel = "📱 OAuth"
    if oauthToken:
        oauthLabel += " ✅"
    if activeMethod == 'api' and oauthToken:
        oauthLabel += " ⭐"

    browserLabel = "🌐 Browser"
    if browserAuth == 'true':
        browserLabel += " ✅"
    if activeMethod == 'browser' and browserAuth == 'true':
        browserLabel += " ⭐"

    keyboardRows = [
        [InlineKeyboardButton(text=oauthLabel, callback_data="login_method:oauth")],
        [InlineKeyboardButton(text=browserLabel, callback_data="login_method:browser")],
    ]

    if (oauthToken and activeMethod == 'browser') or (browserAuth == 'true' and activeMethod == 'api'):
        switchTo = 'api' if activeMethod == 'browser' else 'browser'
        switchLabel = f"🔄 {t('bot', 'switch_to', switchTo.upper())}"
        keyboardRows.append([InlineKeyboardButton(text=switchLabel, callback_data=f"switch_method:{switchTo}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboardRows)

    statusText = t('bot', 'login_select_method')
    statusText += f"\n\n{t('bot', 'active_method', activeMethod.upper())}"

    await message.answer(
        statusText,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


@router.callback_query(StateFilter(LoginStates.waitingLoginMethod))
async def processLoginMethodSelection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = callback.data

    if choice == 'login_method:oauth':
        await setSetting('active_publish_method', 'api')
        await startOAuthFlow(callback.message, state)
    elif choice == 'login_method:browser':
        await setSetting('active_publish_method', 'browser')
        await startBrowserLogin(callback.message, state)
    elif choice.startswith('switch_method:'):
        newMethod = choice.replace('switch_method:', '')
        await setSetting('active_publish_method', newMethod)
        await callback.message.answer(t('bot', 'method_switched', newMethod.upper()))
        await state.clear()
    else:
        await callback.message.answer(t('bot', 'login_unknown_method'))
        await state.clear()


async def startOAuthFlow(message: Message, state: FSMContext):
    from core.oauth_handler import OAuthHandler
    from config.settings import META_APP_ID, META_APP_SECRET

    if not META_APP_ID or not META_APP_SECRET:
        await message.answer(t('bot', 'oauth_not_configured'), parse_mode='Markdown')
        await state.clear()
        return

    from database.models import getSetting
    access_token = await getSetting('threads_access_token')

    if access_token:
        oauth_handler = OAuthHandler()
        is_valid = await oauth_handler.validate_token(access_token)

        if is_valid:
            await message.answer(t('bot', 'oauth_token_exists'), parse_mode='Markdown')
            await state.clear()
            return

    oauth_handler = OAuthHandler()
    await message.answer(t('bot', 'oauth_start'), parse_mode='Markdown')

    try:
        runner, auth_event, get_code = await startOAuthCallbackServer()
        auth_url = oauth_handler.get_auth_url()
        webbrowser.open(auth_url)

        await message.answer(t('bot', 'oauth_browser_opened', auth_url), parse_mode='Markdown')

        try:
            await asyncio.wait_for(auth_event.wait(), timeout=300)
        except asyncio.TimeoutError:
            await runner.cleanup()
            await message.answer(t('bot', 'oauth_timeout'))
            await state.clear()
            return

        auth_code = get_code()
        await runner.cleanup()

        if not auth_code:
            await message.answer(t('bot', 'oauth_no_code'))
            await state.clear()
            return

        await message.answer(t('bot', 'oauth_exchanging'))

        short_lived_token = await oauth_handler.exchange_code_for_token(auth_code)
        if not short_lived_token:
            await message.answer(t('bot', 'oauth_exchange_failed'))
            await state.clear()
            return

        long_lived_token = await oauth_handler.exchange_for_long_lived_token(short_lived_token)
        if not long_lived_token:
            await message.answer(t('bot', 'oauth_long_lived_failed'))
            await state.clear()
            return

        user_id = await oauth_handler.get_user_id(long_lived_token)
        if not user_id:
            await message.answer(t('bot', 'oauth_user_id_failed'))
            await state.clear()
            return

        await saveOauthTokensToDb(user_id, long_lived_token)
        logger.success(f"OAuth tokens saved for user {user_id}")

        await message.answer(t('bot', 'oauth_success_msg', user_id), parse_mode='Markdown')
        await state.clear()

    except Exception as e:
        logger.error(f'OAuth flow error: {e}')
        await message.answer(t('bot', 'oauth_error', str(e)))
        await state.clear()


async def startBrowserLogin(message: Message, state: FSMContext):
    global _loginPage, _loginAgent
    from config.settings import CLOAKBROWSER_CDP_URL
    from core.browser_launcher import isBrowserRunning, launchBrowser

    await message.answer(t('bot', 'browser_checking'))

    if not await isBrowserRunning():
        await message.answer(t('bot', 'browser_not_running'))
        success = await launchBrowser()
        if not success:
            await message.answer(t('bot', 'browser_launch_failed'), parse_mode='Markdown')
            await state.clear()
            return
        await message.answer(t('bot', 'browser_launched'))
        await asyncio.sleep(3)

    await message.answer(t('bot', 'browser_connecting'))

    try:
        from playwright.async_api import async_playwright
        from core.threadsLogin import ThreadsLoginAgent

        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(CLOAKBROWSER_CDP_URL, timeout=10000)
        logger.success('Connected to CloakBrowser')

        if not browser.contexts:
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        else:
            context = browser.contexts[0]

        _loginPage = await context.new_page()
        _loginAgent = ThreadsLoginAgent(_loginPage)
        _loginAgent.setScreenshotCallback(lambda data, caption: _sendScreenshot(message, data, caption))

        await message.answer(t('bot', 'browser_checking_auth'))

        if await _loginAgent.isLoggedIn():
            await setSetting('browser_authorized', 'true')
            await message.answer(t('bot', 'browser_auth_active'))
            _loginPage = None
            _loginAgent = None
            await state.clear()
            await sendMainMenu(message)
            return

        await message.answer(t('bot', 'browser_opening_login'))
        if not await _loginAgent.navigateToLogin():
            await message.answer(t('bot', 'browser_login_page_failed'))
            _loginPage = None
            _loginAgent = None
            await state.clear()
            return

        await _sendScreenshot(message, await _loginPage.screenshot(), t('bot', 'browser_login_page_caption'))
        await message.answer(t('bot', 'browser_enter_username'))
        await state.set_state(LoginStates.waitingUsername)

    except Exception as e:
        logger.error(f'Login command error: {e}')
        await message.answer(t('bot', 'login_error', str(e)))
        _loginPage = None
        _loginAgent = None
        await state.clear()


@router.message(StateFilter(LoginStates.waitingUsername))
async def processUsername(message: Message, state: FSMContext):
    global _loginPage, _loginAgent

    if not _loginPage or not _loginAgent:
        await message.answer(t('bot', 'login_session_expired'))
        await state.clear()
        return

    username = message.text.strip()
    await state.update_data(username=username)
    await message.answer(t('bot', 'login_entering_username'))

    try:
        if await _loginAgent.fillUsername(username):
            await message.answer(t('bot', 'login_enter_password'))
            await state.set_state(LoginStates.waitingPassword)
        else:
            await message.answer(t('bot', 'login_username_field_not_found'))
            await state.clear()
    except Exception as e:
        logger.error(f'Error filling username: {e}')
        await message.answer(t('bot', 'login_error', str(e)))
        await state.clear()


@router.message(StateFilter(LoginStates.waitingPassword))
async def processPassword(message: Message, state: FSMContext):
    global _loginPage, _loginAgent

    if not _loginPage or not _loginAgent:
        await message.answer(t('bot', 'login_session_expired'))
        await state.clear()
        return

    password = message.text
    await state.update_data(password=password)
    await message.answer(t('bot', 'login_entering_password'))

    try:
        if not await _loginAgent.fillPassword(password):
            await message.answer(t('bot', 'login_password_field_not_found'))
            await state.clear()
            return

        status = await _loginAgent.submitLogin()

        if status == "logged_in":
            await setSetting('browser_authorized', 'true')
            await message.answer(t('bot', 'login_success_msg'))
            _loginPage = None
            _loginAgent = None
            await state.clear()
            await sendMainMenu(message)

        elif status == "needs_2fa" or await _loginAgent.needs2FA():
            await _sendScreenshot(message, await _loginPage.screenshot(), t('bot', 'login_2fa_caption'))
            await message.answer(t('bot', 'login_enter_2fa'))
            await state.set_state(LoginStates.waitingTwoFA)

        elif status.startswith("error:"):
            errorText = status.replace("error:", "")
            await _sendScreenshot(message, await _loginPage.screenshot(), t('bot', 'login_error_caption', errorText))
            await message.answer(t('bot', 'login_wrong_credentials'))
            _loginPage = None
            _loginAgent = None
            await state.clear()

        else:
            await _sendScreenshot(message, await _loginPage.screenshot(), t('bot', 'login_unknown_status', status))
            await message.answer(t('bot', 'login_unknown_status_msg'))
            _loginPage = None
            _loginAgent = None
            await state.clear()

    except Exception as e:
        logger.error(f'Error during login: {e}')
        await message.answer(t('bot', 'login_error', str(e)))
        _loginPage = None
        _loginAgent = None
        await state.clear()


@router.message(StateFilter(LoginStates.waitingTwoFA))
async def processTwoFA(message: Message, state: FSMContext):
    global _loginPage, _loginAgent

    if not _loginPage or not _loginAgent:
        await message.answer(t('bot', 'login_session_expired'))
        await state.clear()
        return

    code = message.text.strip()
    if len(code) != 6 or not code.isdigit():
        await message.answer(t('bot', 'login_2fa_invalid'))
        return

    await message.answer(t('bot', 'login_entering_2fa'))

    try:
        status = await _loginAgent.fill2FA(code)

        if status == "logged_in":
            await setSetting('browser_authorized', 'true')
            await message.answer(t('bot', 'login_success_msg'))
            _loginPage = None
            _loginAgent = None
            await state.clear()
            await sendMainMenu(message)
        else:
            await _sendScreenshot(message, await _loginPage.screenshot(), t('bot', 'login_2fa_error', status))
            await message.answer(t('bot', 'login_2fa_wrong'))
            _loginPage = None
            _loginAgent = None
            await state.clear()

    except Exception as e:
        logger.error(f'Error during 2FA: {e}')
        await message.answer(t('bot', 'login_error', str(e)))
        _loginPage = None
        _loginAgent = None
        await state.clear()


@router.message(Command('cancel'))
async def cancelLogin(message: Message, state: FSMContext):
    global _loginPage, _loginAgent

    current_state = await state.get_state()
    if current_state:
        await state.clear()
        _loginPage = None
        _loginAgent = None
        await message.answer(t('bot', 'login_cancelled'))
    else:
        await message.answer(t('bot', 'login_no_active'))


@router.message(Command('post'))
async def postCommand(message: Message, command: Command, state: FSMContext):
    logger.info(f'Received /post from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    if not await isThreadsAuthorized():
        await message.answer(t('bot', 'threads_not_authorized'))
        return

    args = command.args
    if not args:
        await message.answer(t('bot', 'post_enter_topic'))
        await state.set_state(PostStates.waitingTopic)
        return

    await processPostGeneration(message, args.strip(), state)


@router.message(StateFilter(PostStates.waitingTopic))
async def processPostTopic(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    topic = message.text.strip()
    await processPostGeneration(message, topic, state)


async def processPostGeneration(message: Message, topic: str, state: FSMContext):
    imagePath = None

    if message.photo:
        await message.answer(t('bot', 'post_image_received'))
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        Path('data/images').mkdir(exist_ok=True)
        imagePath = f'data/images/post_{message.message_id}.jpg'

        async with aiofiles.open(imagePath, 'wb') as f:
            file_data = await message.bot.download_file(file.file_path)
            await f.write(file_data.read())
        logger.info(f'Saved image: {imagePath}')

    await message.answer(t('bot', 'post_generating', topic))

    try:
        content = await generator.generateNow(topic)

        if not content:
            await message.answer(t('bot', 'post_generation_failed'))
            return

        postId = str(message.message_id)
        _pendingPosts[postId] = {
            'content': content,
            'topic': topic,
            'imagePath': imagePath,
            'userId': message.from_user.id
        }

        previewText = f'{t("bot", "post_preview")}\n\n{content}'
        if imagePath:
            previewText += t('bot', 'post_image_attached')

        keyboard = [
            [InlineKeyboardButton(text=t('bot', 'post_approve'), callback_data=f"approve_{postId}"),
             InlineKeyboardButton(text=t('bot', 'post_edit'), callback_data=f"edit_{postId}")],
            [InlineKeyboardButton(text=t('bot', 'post_cancel'), callback_data=f"cancel_{postId}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await message.answer(previewText, parse_mode='Markdown', reply_markup=markup)
        await state.set_state(PostStates.waitingApproval)
        await state.update_data(postId=postId)

    except Exception as e:
        logger.error(f'Error in /post: {e}')
        import traceback
        logger.error(traceback.format_exc())
        error_msg = str(e)
        if '500' in error_msg or 'Internal Server Error' in error_msg:
            await message.answer(
                t('bot', 'ai_server_error'),
                parse_mode='Markdown'
            )
        else:
            await message.answer(t('bot', 'post_generation_error', str(e)))


@router.callback_query(F.data.startswith("approve_"))
async def approvePostCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    postId = callback.data.replace("approve_", "")
    postData = _pendingPosts.get(postId)

    if not postData:
        await callback.message.edit_text(t('bot', 'post_not_found'))
        await state.clear()
        return

    await callback.message.edit_text(t('bot', 'post_publishing'))

    try:
        from core.threads import getPublisher

        publisher = getPublisher()

        dbPostId = await addPost(postData['content'], postData['topic'], imagePath=postData.get('imagePath'), initialStatus='publishing')

        threadsPostId = await publisher.publish(postData['content'], imagePath=postData.get('imagePath'))

        if threadsPostId:
            await updatePostStatus(dbPostId, 'published', threadsPostId)
            await callback.message.edit_text(t('bot', 'post_published'))
        else:
            await updatePostStatus(dbPostId, 'failed')
            await callback.message.edit_text(t('bot', 'post_publish_failed'))

        del _pendingPosts[postId]
        await state.clear()

    except Exception as e:
        logger.error(f'Error publishing post: {e}')
        import traceback
        logger.error(traceback.format_exc())
        await callback.message.edit_text(t('bot', 'post_publish_error', str(e)))
        await state.clear()


@router.callback_query(F.data.startswith("edit_"))
async def editPostCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    postId = callback.data.replace("edit_", "")
    postData = _pendingPosts.get(postId)
    currentText = postData.get('content', '') if postData else ''
    await callback.message.edit_text(
        f'{t("bot", "post_edit_prompt")}\n\n{currentText}'
    )
    await state.set_state(PostStates.waitingEdit)
    await state.update_data(postId=postId)


@router.message(StateFilter(PostStates.waitingEdit))
async def processEditedPost(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    data = await state.get_data()
    postId = data.get('postId')
    postData = _pendingPosts.get(postId)

    if not postData:
        await message.answer(t('bot', 'post_not_found'))
        await state.clear()
        return

    postData['content'] = message.text
    _pendingPosts[postId] = postData

    previewText = f'{t("bot", "post_edited_preview")}\n\n{message.text}'
    if postData.get('imagePath'):
        previewText += t('bot', 'post_image_attached')

    keyboard = [
        [InlineKeyboardButton(text=t('bot', 'post_approve'), callback_data=f"approve_{postId}"),
         InlineKeyboardButton(text=t('bot', 'post_edit'), callback_data=f"edit_{postId}")],
        [InlineKeyboardButton(text=t('bot', 'post_cancel'), callback_data=f"cancel_{postId}")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(previewText, parse_mode='Markdown', reply_markup=markup)
    await state.set_state(PostStates.waitingApproval)


@router.callback_query(F.data.startswith("cancel_"))
async def cancelPostCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    postId = callback.data.replace("cancel_", "")

    if postId in _pendingPosts:
        del _pendingPosts[postId]

    await callback.message.edit_text(t('bot', 'post_cancelled'))
    await state.clear()


@router.message(Command('schedule'))
async def scheduleCommand(message: Message, command: Command, state: FSMContext):
    logger.info(f'Received /schedule from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    if not await isThreadsAuthorized():
        await message.answer(t('bot', 'threads_not_authorized'))
        return

    args = command.args
    if not args or len(args.split()) < 2:
        await message.answer(t('bot', 'schedule_enter_topic'))
        await state.set_state(ScheduleStates.waitingTopic)
        return

    parts = args.split()
    timeStr = parts[-1]
    topic = ' '.join(parts[:-1])
    await processScheduleTime(message, topic, timeStr, state)


@router.message(StateFilter(ScheduleStates.waitingTopic))
async def processScheduleTopic(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    topic = message.text.strip()
    await state.update_data(topic=topic)
    await message.answer(t('bot', 'schedule_enter_time'))
    await state.set_state(ScheduleStates.waitingTime)


@router.message(StateFilter(ScheduleStates.waitingTime))
async def processScheduleTimeInput(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    timeStr = message.text.strip()
    data = await state.get_data()
    topic = data.get('topic', '')
    await processScheduleTime(message, topic, timeStr, state)


async def processScheduleTime(message: Message, topic: str, timeStr: str, state: FSMContext):
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        scheduledTime = datetime.strptime(timeStr, '%H:%M').replace(
            year=now.year, month=now.month, day=now.day
        )
        if scheduledTime < now:
            scheduledTime += timedelta(days=1)

        await message.answer(t('bot', 'schedule_generating', topic))

        content = await generator.generateNow(topic)
        if not content:
            await message.answer(t('bot', 'schedule_failed'))
            await state.clear()
            return

        postId = str(message.message_id) + '_schedule'
        _pendingPosts[postId] = {
            'content': content,
            'topic': topic,
            'imagePath': None,
            'userId': message.from_user.id,
            'scheduledTime': scheduledTime
        }

        previewText = f'{t("bot", "schedule_preview", scheduledTime.strftime("%Y-%m-%d %H:%M"))}\n\n{content}'
        keyboard = [
            [InlineKeyboardButton(text=t('bot', 'post_approve'), callback_data=f"schedule_approve_{postId}"),
             InlineKeyboardButton(text=t('bot', 'post_edit'), callback_data=f"schedule_edit_{postId}")],
            [InlineKeyboardButton(text=t('bot', 'post_cancel'), callback_data=f"schedule_cancel_{postId}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await message.answer(previewText, parse_mode='Markdown', reply_markup=markup)
        await state.set_state(ScheduleStates.waitingApproval)
        await state.update_data(postId=postId)

    except ValueError:
        await message.answer(t('bot', 'schedule_time_error'))
        await state.clear()
    except Exception as e:
        logger.error(f'Error in /schedule: {e}')
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(t('bot', 'schedule_error', str(e)))
        await state.clear()


@router.callback_query(F.data.startswith("schedule_approve_"))
async def scheduleApproveCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    postId = callback.data.replace("schedule_approve_", "")
    postData = _pendingPosts.get(postId)

    if not postData:
        await callback.message.edit_text(t('bot', 'post_not_found'))
        await state.clear()
        return

    try:
        postIds = await generator.generateAndQueue(
            postData['topic'],
            count=1,
            scheduledTime=postData['scheduledTime']
        )

        if postIds:
            await callback.message.edit_text(
                t('bot', 'schedule_success', postData['scheduledTime'].strftime("%Y-%m-%d %H:%M"), postIds[0])
            )
        else:
            await callback.message.edit_text(t('bot', 'schedule_failed'))

        del _pendingPosts[postId]
        await state.clear()

    except Exception as e:
        logger.error(f'Error approving schedule: {e}')
        await callback.message.edit_text(t('bot', 'schedule_error', str(e)))
        await state.clear()


@router.callback_query(F.data.startswith("schedule_edit_"))
async def scheduleEditCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    postId = callback.data.replace("schedule_edit_", "")
    postData = _pendingPosts.get(postId)
    currentText = postData.get('content', '') if postData else ''
    await callback.message.edit_text(
        f'{t("bot", "post_edit_prompt")}\n\n{currentText}'
    )
    await state.set_state(ScheduleStates.waitingApproval)
    await state.update_data(postId=postId, editing=True)


@router.message(StateFilter(ScheduleStates.waitingApproval))
async def processScheduleEdit(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    data = await state.get_data()
    postId = data.get('postId')
    postData = _pendingPosts.get(postId)

    if not postData:
        await message.answer(t('bot', 'post_not_found'))
        await state.clear()
        return

    postData['content'] = message.text
    _pendingPosts[postId] = postData

    previewText = f'{t("bot", "schedule_preview", postData["scheduledTime"].strftime("%Y-%m-%d %H:%M"))}\n\n{message.text}'
    keyboard = [
        [InlineKeyboardButton(text=t('bot', 'post_approve'), callback_data=f"schedule_approve_{postId}"),
         InlineKeyboardButton(text=t('bot', 'post_edit'), callback_data=f"schedule_edit_{postId}")],
        [InlineKeyboardButton(text=t('bot', 'post_cancel'), callback_data=f"schedule_cancel_{postId}")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(previewText, parse_mode='Markdown', reply_markup=markup)


@router.callback_query(F.data.startswith("schedule_cancel_"))
async def scheduleCancelCallback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    postId = callback.data.replace("schedule_cancel_", "")

    if postId in _pendingPosts:
        del _pendingPosts[postId]

    await callback.message.edit_text(t('bot', 'post_cancelled'))
    await state.clear()


@router.message(Command('topics'))
async def topicsCommand(message: Message):
    logger.info(f'Received /topics from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    topics = await getTopics()
    if not topics:
        await message.answer(t('bot', 'menu_topics_empty'))
        return

    text = f'*{t("bot", "menu_topics_header")}*\n\n' + '\n'.join([f'• {topic}' for topic in topics])
    await message.answer(text, parse_mode='Markdown')


@router.message(Command('addtopic'))
async def addtopicCommand(message: Message, command: Command, state: FSMContext):
    logger.info(f'Received /addtopic from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    args = command.args
    if not args:
        await message.answer(t('bot', 'addtopic_enter_name'))
        await state.set_state(AddtopicStates.waitingName)
        return

    await saveTopic(message, args.strip())


@router.message(StateFilter(AddtopicStates.waitingName))
async def processAddtopicName(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        await message.answer(t('bot', 'cancelled'))
        return

    await saveTopic(message, message.text.strip())
    await state.clear()


async def saveTopic(message: Message, name: str):
    topicId = await addTopic(name)
    if topicId:
        await message.answer(t('bot', 'addtopic_success', name, topicId))
    else:
        await message.answer(t('bot', 'addtopic_failed'))


@router.message(Command('queue'))
async def queueCommand(message: Message):
    logger.info(f'Received /queue from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    posts = await getPendingPosts(limit=20)
    if not posts:
        await message.answer(t('bot', 'menu_queue_empty'))
        return

    text = f'*{t("bot", "menu_queue_header")} ({len(posts)}):*\n\n'
    for post in posts:
        scheduled = t('bot', 'queue_scheduled', post["scheduledTime"]) if post.get('scheduledTime') else ''
        text += f'• ID {post["id"]}: {post["content"][:50]}...{scheduled}\n'
    await message.answer(text, parse_mode='Markdown')


@router.message(Command('stats'))
async def statsCommand(message: Message):
    logger.info(f'Received /stats from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    stats = await getStats()
    text = _buildStatsText(stats)
    await message.answer(text, parse_mode='Markdown')


@router.message(Command('settings'))
async def settingsCommand(message: Message):
    logger.info(f'Received /settings from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    text = _buildSettingsText()
    await message.answer(text, parse_mode='Markdown')


@router.message(Command('persona'))
async def personaCommand(message: Message):
    logger.info(f'Received /persona from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    from pathlib import Path

    personaPath = Path('config/prompts/persona.md')
    if not personaPath.exists():
        await message.answer(t('bot', 'persona_not_found'))
        return

    content = personaPath.read_text(encoding='utf-8')

    if len(content) > 4000:
        content = content[:4000] + t('bot', 'persona_truncated')

    await message.answer(
        f'{t("bot", "persona_current")}\n\n```markdown\n{content}\n```',
        parse_mode='Markdown'
    )


@router.message(Command('skills'))
async def skillsCommand(message: Message):
    logger.info(f'Received /skills from user {message.from_user.id}')
    if not isAuthorized(message.from_user.id):
        await message.answer(t('bot', 'access_denied'))
        return

    from pathlib import Path
    from config.settings import AI_SKILLS_DIR

    skillsDir = Path(AI_SKILLS_DIR)
    if not skillsDir.exists():
        await message.answer(t('bot', 'skills_dir_not_found'))
        return

    skills = list(skillsDir.glob('*.md'))
    if not skills:
        await message.answer(t('bot', 'skills_empty'))
        return

    text = t('bot', 'skills_header') + '\n\n'
    for skill in skills:
        content = skill.read_text(encoding='utf-8')
        lines = content.split('\n')

        name = skill.stem
        description = ''
        for line in lines:
            if line.startswith('# '):
                description = line[2:].strip()
                break

        text += f'• *{name}*: {description}\n'

    text += t('bot', 'skills_hint')

    await message.answer(text, parse_mode='Markdown')
