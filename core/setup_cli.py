import sys
import asyncio
import questionary
from pathlib import Path
from utils.logger import logger
from utils.i18n import t, setLang, getLang

def ask(q):
    return q.unsafe_ask()

LOGO = """
████████╗██╗  ██╗██████╗ ███████╗██╗  ██╗██████╗ ███████╗
╚══██╔══╝██║  ██║██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝
   ██║   ███████║██████╔╝█████╗  ███████║██║  ██║███████╗
   ██║   ██╔══██║██╔══██╗██╔══╝  ██╔══██║██║  ██║╚════██║
   ██║   ██║  ██║██║  ██║███████╗██║  ██║██████╔╝███████║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝

              A U T O P O S T E R   S E T U P
"""

def clearScreen():
    print("\033[H\033[J", end="")

ENV_PATH = Path('.env')
LANG_PATH = Path('.lang')

def loadEnv():
    env = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value
    return env


def loadLang():
    if LANG_PATH.exists():
        return LANG_PATH.read_text(encoding='utf-8').strip()
    return None


def saveLang(lang: str):
    LANG_PATH.write_text(lang, encoding='utf-8')

def saveEnv(env):
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.write("TELEGRAM_BOT_TOKEN={}\n".format(env.get('TELEGRAM_BOT_TOKEN', '')))
        f.write("TELEGRAM_ADMIN_IDS={}\n".format(env.get('TELEGRAM_ADMIN_IDS', '')))
        f.write("META_APP_ID={}\n".format(env.get('META_APP_ID', '')))
        f.write("META_APP_SECRET={}\n".format(env.get('META_APP_SECRET', '')))
        f.write("PUBLISH_METHOD={}\n".format(env.get('PUBLISH_METHOD', 'api')))
        f.write("CLOAKBROWSER_CDP_URL={}\n".format(env.get('CLOAKBROWSER_CDP_URL', 'http://localhost:9222')))
        f.write("AI_PROVIDER={}\n".format(env.get('AI_PROVIDER', 'openai')))
        f.write("AI_BASE_URL={}\n".format(env.get('AI_BASE_URL', 'http://localhost:11434/v1')))
        f.write("AI_API_KEY={}\n".format(env.get('AI_API_KEY', '')))
        f.write("AI_MODEL={}\n".format(env.get('AI_MODEL', 'llama3')))
        f.write("AI_TIMEOUT={}\n".format(env.get('AI_TIMEOUT', '120')))
        f.write("DEFAULT_POSTS_PER_DAY={}\n".format(env.get('DEFAULT_POSTS_PER_DAY', '3')))
        f.write("DEFAULT_POST_TIMES={}\n".format(env.get('DEFAULT_POST_TIMES', '10:00,15:00,20:00')))
        f.write("LOG_LEVEL={}\n".format(env.get('LOG_LEVEL', 'INFO')))
    logger.success(f"Configuration saved to {ENV_PATH}")

def editField(env, key, prompt, default=None):
    current = env.get(key, default or '')
    value = ask(questionary.text(
        prompt,
        default=current,
        instruction=f"(current: {current if current else 'empty'})"
    ))
    if value is not None:
        env[key] = value
    return env

def changeLanguage():
    lang = ask(questionary.select(
        "🌍 Select language / Выберите язык:",
        choices=[
            questionary.Choice("English", "en"),
            questionary.Choice("Русский", "ru"),
        ]
    ))
    setLang(lang)
    saveLang(lang)


def settingsMenu(env):
    while True:
        clearScreen()
        print(LOGO)

        choice = ask(questionary.select(
            t('cli', 'settings_menu'),
            choices=[
                questionary.Choice(t('cli', 'language_settings'), "language"),
                questionary.Choice(t('cli', 'telegram_settings'), "telegram"),
                questionary.Choice(t('cli', 'threads_settings'), "threads"),
                questionary.Choice(t('cli', 'ai_settings'), "ai"),
                questionary.Choice(t('cli', 'mcp_settings'), "mcp"),
                questionary.Choice(t('cli', 'persona_settings'), "persona"),
                questionary.Choice(t('cli', 'scheduler_settings'), "scheduler"),
                questionary.Choice(t('cli', 'system_settings'), "system"),
                questionary.Separator(),
                questionary.Choice(t('cli', 'back'), "back"),
            ]
        ))

        if choice == "back":
            return env
        elif choice == "save":
            if ask(questionary.confirm(t('cli', 'save_confirm'))):
                saveEnv(env)
                questionary.print(t('cli', 'save_success'), style="bold green")
                ask(questionary.press_any_key_to_continue())
                return env
        elif choice == "language":
            changeLanguage()
        elif choice == "telegram":
            env = telegramSettings(env)
        elif choice == "threads":
            env = threadsSettings(env)
        elif choice == "ai":
            env = aiSettings(env)
        elif choice == "mcp":
            env = mcpSettings(env)
        elif choice == "persona":
            personaSettings()
        elif choice == "scheduler":
            env = schedulerSettings(env)
        elif choice == "system":
            env = systemSettings(env)

    return env

def telegramSettings(env):
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'telegram_instructions'))

    env = editField(env, 'TELEGRAM_BOT_TOKEN', t('cli', 'bot_token_prompt'))
    env = editField(env, 'TELEGRAM_ADMIN_IDS', t('cli', 'admin_ids_prompt'))

    return env

def threadsSettings(env):
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'threads_instructions'))

    env = editField(env, 'META_APP_ID', t('cli', 'meta_app_id_prompt'))
    env = editField(env, 'META_APP_SECRET', t('cli', 'meta_app_secret_prompt'))

    method = ask(questionary.select(
        t('cli', 'publish_method_prompt'),
        choices=[
            questionary.Choice(t('cli', 'method_api'), "api"),
            questionary.Choice(t('cli', 'method_browser'), "browser"),
        ],
        default=env.get('PUBLISH_METHOD', 'api')
    ))

    if method:
        env['PUBLISH_METHOD'] = method

        if method == 'browser':
            env = editField(env, 'CLOAKBROWSER_CDP_URL', t('cli', 'cdp_url_prompt'))

    return env

def aiSettings(env):
    while True:
        clearScreen()
        print(LOGO)
        print("\n" + t('cli', 'ai_instructions'))

        current_provider = env.get('AI_PROVIDER', 'openai')
        current_model = env.get('AI_MODEL', 'not set')

        choices = [
            questionary.Choice(f"{t('cli', 'ai_change_provider')} [{current_provider}]", "change_provider"),
            questionary.Choice(t('cli', 'ai_configure_current'), "configure"),
            questionary.Separator(),
            questionary.Choice(t('cli', 'back'), "back"),
        ]

        choice = ask(questionary.select(
            f"{t('cli', 'ai_current_settings', current_provider, current_model)}",
            choices=choices
        ))

        if choice == "back":
            return env
        elif choice == "change_provider":
            env = selectAIProvider(env)
        elif choice == "configure":
            env = configureAIProvider(env)

    return env


def selectAIProvider(env):
    clearScreen()
    print(LOGO)

    provider = ask(questionary.select(
        t('cli', 'ai_provider_prompt'),
        choices=[
            questionary.Choice(t('cli', 'provider_openai'), "openai"),
            questionary.Choice(t('cli', 'provider_anthropic'), "anthropic"),
            questionary.Separator(),
            questionary.Choice(t('cli', 'back'), "back"),
        ],
        default=env.get('AI_PROVIDER', 'openai')
    ))

    if provider == "back":
        return env

    env['AI_PROVIDER'] = provider
    questionary.print(t('cli', 'ai_provider_changed', provider), style="bold green")
    ask(questionary.press_any_key_to_continue())
    return env


def configureAIProvider(env):
    clearScreen()
    print(LOGO)

    provider = env.get('AI_PROVIDER', 'openai')

    if provider == 'openai':
        print("\n" + t('cli', 'ai_openai_settings'))
        env = editField(env, 'AI_BASE_URL', t('cli', 'ai_base_url_prompt'))
        env = editField(env, 'AI_API_KEY', t('cli', 'ai_api_key_prompt'))
        env = editField(env, 'AI_MODEL', t('cli', 'ai_model_prompt'))
        env = editField(env, 'AI_TIMEOUT', t('cli', 'ai_timeout_prompt'))

    elif provider == 'anthropic':
        print("\n" + t('cli', 'ai_anthropic_settings'))
        env = editField(env, 'AI_BASE_URL', t('cli', 'ai_base_url_prompt'), 'https://api.anthropic.com')
        env = editField(env, 'AI_API_KEY', t('cli', 'ai_api_key_prompt'))
        env = editField(env, 'AI_MODEL', t('cli', 'ai_model_prompt'), 'claude-3-5-sonnet-20241022')
        env = editField(env, 'AI_TIMEOUT', t('cli', 'ai_timeout_prompt'))

    return env


def mcpSettings():
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'mcp_instructions'))

    from core.mcp_client import mcpManager

    while True:
        servers = mcpManager.list_servers()

        choices = []
        if servers:
            for server in servers:
                choices.append(questionary.Choice(
                    f"🔧 {server['name']} ({server['command']})",
                    f"view_{server['name']}"
                ))
            choices.append(questionary.Separator())

        choices.extend([
            questionary.Choice(t('cli', 'mcp_add_server'), "add"),
            questionary.Choice(t('cli', 'mcp_remove_server'), "remove"),
            questionary.Separator(),
            questionary.Choice(t('cli', 'back'), "back"),
        ])

        choice = ask(questionary.select(
            t('cli', 'mcp_settings_menu'),
            choices=choices
        ))

        if choice == "back":
            return
        elif choice == "add":
            addMcpServer()
        elif choice == "remove":
            removeMcpServer()
        elif choice.startswith("view_"):
            server_name = choice.replace("view_", "")
            viewMcpServer(server_name)


def addMcpServer():
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'mcp_add_instructions'))

    name = ask(questionary.text(t('cli', 'mcp_name_prompt')))
    if not name:
        return

    command = ask(questionary.text(t('cli', 'mcp_command_prompt')))
    if not command:
        return

    args_str = ask(questionary.text(t('cli', 'mcp_args_prompt'), default=""))
    args = args_str.split() if args_str else []

    from core.mcp_client import mcpManager
    mcpManager.add_server(name, command, args)

    questionary.print(t('cli', 'mcp_server_added', name), style="bold green")
    ask(questionary.press_any_key_to_continue())


def removeMcpServer():
    from core.mcp_client import mcpManager
    servers = mcpManager.list_servers()

    if not servers:
        questionary.print(t('cli', 'mcp_no_servers'), style="yellow")
        ask(questionary.press_any_key_to_continue())
        return

    server_name = ask(questionary.select(
        t('cli', 'mcp_select_remove'),
        choices=[questionary.Choice(s['name'], s['name']) for s in servers]
    ))

    if server_name and ask(questionary.confirm(t('cli', 'mcp_confirm_remove', server_name))):
        mcpManager.remove_server(server_name)
        questionary.print(t('cli', 'mcp_server_removed', server_name), style="bold green")
        ask(questionary.press_any_key_to_continue())


def viewMcpServer(server_name: str):
    from core.mcp_client import mcpManager
    servers = mcpManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)

    if not server:
        return

    clearScreen()
    print(LOGO)
    print(f"\n{t('cli', 'mcp_server_details', server_name)}\n")
    print(f"  Command: {server['command']}")
    print(f"  Args: {' '.join(server.get('args', []))}")
    if server.get('env'):
        print(f"  Env: {', '.join(server['env'].keys())}")
    print()

    ask(questionary.press_any_key_to_continue())


def schedulerSettings(env):
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'scheduler_instructions'))

    env = editField(env, 'DEFAULT_POSTS_PER_DAY', t('cli', 'posts_per_day_prompt'))
    env = editField(env, 'DEFAULT_POST_TIMES', t('cli', 'post_times_prompt'))

    return env

def systemSettings(env):
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'system_instructions'))

    level = ask(questionary.select(
        t('cli', 'log_level_prompt'),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=env.get('LOG_LEVEL', 'INFO')
    ))

    if level:
        env['LOG_LEVEL'] = level

    return env

def personaSettings():
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'persona_instructions'))

    while True:
        choice = ask(questionary.select(
            t('cli', 'ai_settings_menu'),
            choices=[
                questionary.Choice(t('cli', 'edit_persona'), "edit_persona"),
                questionary.Choice(t('cli', 'view_skills'), "view_skills"),
                questionary.Separator(),
                questionary.Choice(t('cli', 'back'), "back"),
            ]
        ))

        if choice == "back":
            return
        elif choice == "edit_persona":
            editPersona()
        elif choice == "view_skills":
            viewSkills()

def editPersona():
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'edit_persona_instructions'))

    personaPath = Path('config/prompts/persona.md')

    if personaPath.exists():
        currentContent = personaPath.read_text(encoding='utf-8')
        print(t('cli', 'current_persona_label') + "\n")
        print(currentContent)
        print("\n" + "="*60 + "\n")

        if ask(questionary.confirm(t('cli', 'edit_persona_confirm'))):
            print(t('cli', 'enter_persona_prompt'))
            try:
                newContent = sys.stdin.read()
                personaPath.write_text(newContent, encoding='utf-8')
                questionary.print(t('cli', 'persona_updated'), style="bold green")
            except KeyboardInterrupt:
                questionary.print("\n" + t('cli', 'cancelled'), style="yellow")
    else:
        print(t('cli', 'no_persona_found'))
        if ask(questionary.confirm(t('cli', 'create_default_persona'))):
            personaPath.parent.mkdir(parents=True, exist_ok=True)
            personaPath.write_text(DEFAULT_PERSONA, encoding='utf-8')
            questionary.print(t('cli', 'persona_created'), style="bold green")

    ask(questionary.press_any_key_to_continue())

def viewSkills():
    clearScreen()
    print(LOGO)
    print("\n" + t('cli', 'skills_instructions'))

    skillsDir = Path('config/skills')

    if skillsDir.exists():
        skills = list(skillsDir.glob('*.md'))

        if skills:
            for skill in skills:
                print(f"📚 {skill.stem}")
                content = skill.read_text(encoding='utf-8')
                lines = content.split('\n')[:5]
                for line in lines:
                    print(f"   {line}")
                print()
        else:
            print(t('cli', 'no_skills_found'))
    else:
        print(t('cli', 'skills_dir_not_found'))

    ask(questionary.press_any_key_to_continue())

DEFAULT_PERSONA = """# AI Persona

You are a creative social media expert specializing in Threads content.

## Writing Style
- Casual and conversational tone
- Use emojis sparingly (1-2 max per post)
- Keep posts under 500 characters
- Make content engaging and shareable

## Content Guidelines
- Ask questions to drive engagement
- Use storytelling techniques
- Include call-to-action when appropriate
- Focus on value and entertainment

## Personal Touch
- Add personal opinions and experiences
- Be authentic and relatable
- Avoid corporate language
- Use humor when appropriate
"""

def runSetup():
    try:
        clearScreen()
        print(LOGO)

        savedLang = loadLang()
        if savedLang:
            setLang(savedLang)
        else:
            lang = ask(questionary.select(
                "🌍 Select language / Выберите язык:",
                choices=[
                    questionary.Choice("English", "en"),
                    questionary.Choice("Русский", "ru"),
                ]
            ))
            setLang(lang)
            saveLang(lang)

        env = loadEnv()

        if not env:
            questionary.print(t('cli', 'no_env'), style="bold yellow")
            ask(questionary.press_any_key_to_continue())

        while True:
            clearScreen()
            print(LOGO)

            choice = ask(questionary.select(
                t('cli', 'main_menu'),
                choices=[
                    questionary.Choice(t('cli', 'settings'), "settings"),
                    questionary.Choice(t('cli', 'run_bot'), "run"),
                    questionary.Choice(t('cli', 'exit'), "exit"),
                ]
            ))

            if choice == "settings":
                env = settingsMenu(env)
            elif choice == "run":
                if not env.get('TELEGRAM_BOT_TOKEN'):
                    questionary.print(t('cli', 'error_token'), style="bold red")
                    ask(questionary.press_any_key_to_continue())
                else:
                    saveEnv(env)
                    return True
            elif choice == "exit":
                return False

        return True

    except KeyboardInterrupt:
        return False

if __name__ == '__main__':
    try:
        runSetup()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        exit(0)
