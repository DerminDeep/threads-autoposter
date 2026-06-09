translations = {
    'ru': {
        'bot': {
            'welcome': (
                '👋 *Привет! Я Threads AutoPoster*\n\n'
                'Я помогу тебе автоматически публиковать посты в Threads.\n\n'
                '*Основные команды:*\n'
                '/login - авторизация в Threads\n'
                '/post - создать пост (с подтверждением)\n'
                '/topics - управление темами\n'
                '/stats - статистика\n\n'
                'Выбери действие:'
            ),
            'access_denied': 'Доступ запрещен.',
            'back_to_menu': '◀️ Назад в меню',
            'recommended': 'Рекомендуется',
            'cancelled': '✅ Отменено',


            'menu_btn_post': '📝 Создать пост',
            'menu_btn_schedule': '⏰ Запланировать',
            'menu_btn_topics': '📋 Темы',
            'menu_btn_stats': '📊 Статистика',
            'menu_btn_queue': '📬 Очередь',
            'menu_btn_login': '🔐 Авторизация',
            'menu_btn_settings': '⚙️ Настройки',
            'menu_btn_persona': '🎭 Persona',
            'menu_btn_skills': '🎯 Скиллы',
            'menu_btn_help': '❓ Помощь',


            'menu_post': 'Отправь /post чтобы создать новый пост.\n\nМожешь также прикрепить картинку к посту!',
            'menu_schedule': 'Отправь /schedule чтобы запланировать пост.\n\nБот спросит тему и время публикации.',
            'menu_queue_empty': '📭 Очередь пуста.',
            'menu_queue_header': '📋 Посты в очереди',
            'menu_login': 'Отправь /login чтобы авторизоваться в Threads.\n\nВыберите метод: OAuth или Browser.',
            'menu_topics_empty': '📭 Тем пока нет. Добавьте с помощью /addtopic <название>',
            'menu_topics_header': '📋 Темы:',
            'menu_help': (
                '*❓ Помощь:*\n\n'
                '/login - авторизация в Threads через CloakBrowser\n'
                '/post - сгенерировать и опубликовать пост (с подтверждением)\n'
                '/schedule <тема> <ЧЧ:ММ> - запланировать пост\n'
                '/topics - список тем для постов\n'
                '/addtopic <название> - добавить тему\n'
                '/queue - очередь постов\n'
                '/stats - статистика публикаций\n'
                '/settings - текущие настройки\n'
                '/cancel - отменить текущее действие\n\n'
                '💡 Можешь прикрепить картинку к /post!'
            ),


            'oauth_callback_success': '✅ Авторизация успешна! Можете закрыть это окно и вернуться в Telegram.',
            'oauth_callback_error': '❌ Ошибка авторизации: {}',


            'login_oauth_btn': '📱 OAuth (Рекомендуется)',
            'login_browser_btn': '🌐 Browser (CloakBrowser)',
            'login_select_method': '🔐 *Выберите метод авторизации:*\n\n• 📱 *OAuth* (Рекомендуется) - официальная авторизация через Meta API\n• 🌐 *Browser* - авторизация через CloakBrowser\n\nВыберите метод:',
            'login_unknown_method': '❌ Неизвестный метод. Отправьте /login снова.',
            'login_session_expired': '❌ Сессия логина истекла. Отправьте /login снова.',
            'switch_to': 'Переключиться на {}',
            'active_method': '🎯 *Активный метод:* `{}`',
            'method_switched': '✅ Метод публикации переключен на `{}`',


            'oauth_not_configured': (
                '❌ *OAuth не настроен*\n\n'
                'Необходимо настроить переменные в `.env`:\n'
                '• `META_APP_ID`\n'
                '• `META_APP_SECRET`\n\n'
                'Следуйте инструкции в README для настройки OAuth.'
            ),
            'oauth_token_exists': (
                '✅ *У вас уже есть действующий токен!*\n\n'
                'Авторизация уже выполнена. Можете использовать /post для публикации.'
            ),
            'oauth_start': (
                '📱 *OAuth авторизация*\n\n'
                'Запускаю локальный сервер для получения авторизации...\n'
                'После этого откроется браузер для авторизации в Meta.'
            ),
            'oauth_browser_opened': (
                '🌐 *Браузер открыт автоматически!*\n\n'
                'Авторизуйтесь в Meta. После успешной авторизации вы вернетесь в бота.\n\n'
                'Если браузер не открылся, перейдите по ссылке вручную:\n'
                '{}'
            ),
            'oauth_timeout': '❌ Время ожидания авторизации истекло. Попробуйте снова.',
            'oauth_no_code': '❌ Не удалось получить код авторизации. Попробуйте снова.',
            'oauth_exchanging': '🔄 Обмениваю код на токен...',
            'oauth_exchange_failed': '❌ Не удалось обменять код на токен. Попробуйте снова.',
            'oauth_long_lived_failed': '❌ Не удалось получить long-lived токен. Попробуйте снова.',
            'oauth_user_id_failed': '❌ Не удалось получить Threads User ID. Попробуйте снова.',
            'oauth_success_msg': (
                '✅ *OAuth авторизация успешна!*\n\n'
                'Получен long-lived токен (действует 60 дней).\n'
                'Threads User ID: `{}`\n\n'
                'Теперь вы можете использовать /post для публикации постов.'
            ),
            'oauth_error': '❌ Ошибка OAuth авторизации: {}',

            'threads_not_authorized': '❌ Сначала авторизуйтесь в Threads через команду /login',

            'browser_checking': '🔍 Проверяю CloakBrowser...',
            'browser_not_running': '🔄 CloakBrowser не запущен, запускаю автоматически...',
            'browser_launch_failed': (
                '❌ Не удалось запустить CloakBrowser.\n\n'
                'Проверьте логи (logs/app.log) для подробностей.\n\n'
                '*Попробуйте вручную:*\n'
                '1. `CloakBrowser.exe install`\n'
                '2. Перезапустите бота и снова /login'
            ),
            'browser_launched': '✅ CloakBrowser запущен!',
            'browser_connecting': '🔗 Подключаюсь к браузеру...',
            'browser_checking_auth': '🤖 Проверяю статус авторизации...',
            'browser_already_logged_in': '✅ Вы уже авторизованы в Threads! Можете отправлять /post <тема>',
            'browser_auth_active': '✅ Авторизация уже активна. Отправьте /post <тема> для публикации.',
            'browser_opening_login': '🤖 Открываю страницу входа...',
            'browser_login_page_failed': '❌ Не удалось открыть страницу входа. Попробуйте /login снова.',
            'browser_enter_username': '📝 Введите имя пользователя (email или username):',
            'browser_login_page_caption': '🤖 Страница входа открыта. Готов заполнить форму.',

            'login_entering_username': '🤖 Ввожу имя пользователя...',
            'login_enter_password': '🔐 Введите пароль:',
            'login_username_field_not_found': '❌ Не удалось найти поле для имени пользователя. Попробуйте /login снова.',
            'login_entering_password': '🤖 Ввожу пароль и нажимаю вход...',
            'login_password_field_not_found': '❌ Не удалось найти поле для пароля.',
            'login_success_caption': '✅ Успешная авторизация в Threads!',
            'login_success_msg': '✅ Авторизовано! Можете отправлять /post <тема> для публикации.',
            'login_2fa_required': '🔐 Требуется код двухфакторной аутентификации.',
            'login_2fa_caption': '🔐 Требуется код двухфакторной аутентификации.',
            'login_enter_2fa': '🔢 Отправьте 6-значный код:',
            'login_2fa_invalid': '⚠️ Код должен содержать 6 цифр. Попробуйте снова:',
            'login_entering_2fa': '🤖 Ввожу код 2FA...',
            'login_2fa_error': '❌ Ошибка 2FA: {}',
            'login_2fa_wrong': '❌ Неверный код. Отправьте /login для повторной попытки.',
            'login_error_caption': '❌ Ошибка входа: {}',
            'login_wrong_credentials': '❌ Неверный логин или пароль. Отправьте /login для повторной попытки.',
            'login_unknown_status': '⚠️ Статус: {}',
            'login_unknown_status_msg': '⚠️ Не удалось определить результат. Проверьте скриншот и попробуйте /login снова.',
            'login_cancelled': '✅ Процесс авторизации отменён.',
            'login_no_active': 'ℹ️ Нет активного процесса авторизации.',
            'login_error': '❌ Ошибка: {}',

            # Post
            'post_enter_topic': '📝 Введите тему для поста:\n\n💡 Можете также прикрепить картинку!',
            'post_generating': '🤖 Генерирую пост на тему: {}...',
            'post_image_received': '📸 Получена картинка, сохраняю...',
            'post_generation_failed': '❌ Не удалось сгенерировать пост. Проверьте логи.',
            'post_preview': '📝 *Сгенерированный пост:*',
            'post_image_attached': '\n\n🖼️ Картинка прикреплена',
            'post_approve': '✅ Опубликовать',
            'post_edit': '✏️ Редактировать',
            'post_cancel': '❌ Отменить',
            'post_generation_error': '❌ Ошибка при генерации: {}',
            'ai_server_error': (
                '❌ AI сервис недоступен (500 ошибка)\n\n'
                'Проверьте:\n'
                '• AI сервис запущен\n'
                '• Модель доступна\n'
                '• Настройки через /settings'
            ),
            'post_not_found': '❌ Пост не найден или время истекло.',
            'post_publishing': '🚀 Публикую пост в Threads...',
            'post_published': '✅ Пост успешно опубликован в Threads!',
            'post_publish_failed': (
                '❌ Не удалось опубликовать пост.\n\n'
                'Возможные причины:\n'
                '• Не авторизован в Threads (отправьте /login)\n'
                '• CloakBrowser не запущен\n'
                '• Изменился интерфейс Threads'
            ),
            'post_publish_error': '❌ Ошибка при публикации: {}',
            'post_edit_prompt': '✏️ Скопируй текст ниже, отредактируй и отправь обратно:\n\n(Или /cancel для отмены)',
            'post_edited_preview': '📝 *Отредактированный пост:*',
            'post_cancelled': '❌ Пост отменен.',

            'schedule_enter_topic': '📝 Введите тему для поста:',
            'schedule_enter_time': '⏰ Введите время публикации (ЧЧ:ММ):',
            'schedule_generating': '🤖 Генерирую пост на тему: {}...',
            'schedule_preview': '⏰ *Запланированный пост на {}:*',
            'schedule_success': '✅ Пост запланирован на {}\nID: {}\n\nКонтент уже сгенерирован и будет опубликован в указанное время.',
            'schedule_failed': (
                '❌ Не удалось сгенерировать пост.\n\n'
                'Возможные причины:\n'
                '• AI сервис недоступен\n'
                '• Неверные настройки AI (AI_BASE_URL, AI_API_KEY, AI_MODEL)\n\n'
                'Проверьте настройки через /settings'
            ),
            'schedule_time_error': '⚠️ Неверный формат времени. Используйте ЧЧ:ММ (например, 15:30)',
            'schedule_error': '❌ Ошибка: {}',
            'scheduled_post_published': '✅ *Запланированный пост опубликован!*\n\n*Тема:* {}\n*ID:* {}\n\n*Содержание:*\n{}',

  
            'addtopic_enter_name': '📝 Введите название темы:',
            'addtopic_success': '✅ Тема добавлена: {} (ID: {})',
            'addtopic_failed': '❌ Не удалось добавить тему.',

            'queue_scheduled': ' (запланирован: {})',
            'stats_title': '*📊 Статистика:*',
            'stats_total': 'Всего:',
            'stats_published': 'Опубликовано:',
            'stats_pending': 'В очереди:',
            'stats_failed': 'Ошибок:',
            'stats_success_rate': 'Успешность:',
            'stats_today': 'Сегодня:',
            'stats_yesterday_label': 'Вчера:',
            'stats_yesterday_trend': ' ({trend} {diff:+d} к вчера)',
            'stats_activity': 'Активность за 7 дней:',

            'settings_header': '⚙️ *Текущие настройки:*',
            'settings_ai_url': 'AI URL:',
            'settings_model': 'Модель:',
            'settings_method': 'Метод:',
            'settings_posts_per_day': 'Постов/день:',
            'settings_times': 'Время:',

            'persona_not_found': '❌ Persona файл не найден. Создайте `config/prompts/persona.md`',
            'persona_truncated': '\n\n...(обрезано)',
            'persona_current': '🎭 *Текущая Persona:*',
            'persona_edit': '✏️ Редактировать',
            'persona_edit_prompt': '✏️ Отправьте новый текст persona:\n\n(Или /cancel для отмены)',
            'persona_saved': '✅ Persona сохранена',

            'skills_dir_not_found': '❌ Директория скиллов не найдена.',
            'skills_empty': '📭 Нет доступных скиллов.',
            'skills_header': '🎯 *Доступные скиллы:*',
            'skills_hint': '\n💡 Используйте `/post <тема>` и ИИ автоматически выберет подходящий скилл!',
        },
        'cli': {
            'main_menu': 'Главное меню:',
            'settings': 'Настройки',
            'run_bot': 'Запустить бота',
            'exit': 'Выход',
            'language_select': 'Выберите язык / Select language:',
            'settings_menu': 'Настройки:',
            'language_settings': '🌍 Язык / Language',
            'telegram_bot': 'Telegram бот',
            'threads_api': 'Threads API',
            'ai_config': 'Настройка AI',
            'ai_persona': 'AI персонализация',
            'scheduler': 'Планировщик',
            'system': 'Система',
            'save_exit': 'Сохранить и выйти',
            'back': 'Назад',
            'persona_description': (
                '=== AI Персонализация ===\n\n'
                'Persona - это файл с инструкциями для AI, определяющий стиль письма и характер.\n'
                'Файл: config/prompts/persona.md\n\n'
                'Здесь вы можете:\n'
                '- Просмотреть текущую persona\n'
                '- Отредактировать стиль письма AI\n\n'
            ),
            'skills_description': (
                '=== Скиллы контента ===\n\n'
                'Скиллы - это шаблоны для разных типов контента.\n'
                'Файлы: config/skills/*.md\n\n'
                'Каждый скилл определяет:\n'
                '- Когда использовать (например, для туториалов)\n'
                '- Инструкции по написанию\n\n'
                'AI автоматически выбирает подходящий скилл на основе темы поста.\n\n'
            ),
            'edit_persona': 'Редактировать Persona',
            'view_skills': 'Просмотреть скиллы',
            'no_env': 'Файл .env не найден. Давайте настроим конфигурацию.',
            'error_token': 'Ошибка: TELEGRAM_BOT_TOKEN обязателен!',
            'error_admin_ids': 'Ошибка: TELEGRAM_ADMIN_IDS обязателен!',
            'error_meta_app_id': 'Ошибка: META_APP_ID обязателен!',
            'error_meta_app_secret': 'Ошибка: META_APP_SECRET обязателен!',
            'run_setup_hint': 'Запустите с флагом --setup для настройки: python main.py --setup',
            'telegram_settings': 'Telegram бот',
            'threads_settings': 'Threads API',
            'ai_settings': 'Настройка AI',
            'persona_settings': 'AI персонализация',
            'scheduler_settings': 'Планировщик',
            'system_settings': 'Система',
            'save_confirm': 'Сохранить конфигурацию?',
            'save_success': 'Конфигурация успешно сохранена!',
            'telegram_instructions': (
                '=== Настройка Telegram бота ===\n\n'
                '• Bot Token - получите от @BotFather в Telegram\n'
                '• Admin IDs - ID пользователей через запятую, кто может управлять ботом\n\n'
            ),
            'bot_token_prompt': 'Bot Token (от @BotFather)',
            'admin_ids_prompt': 'Admin IDs (через запятую)',
            'threads_instructions': (
                '=== Настройка Threads API ===\n\n'
                '• Meta App ID и Secret - из Meta Developer Console\n'
                '• Метод API - официальный, с лимитами (~250 постов/сутки)\n'
                '• Метод Browser - через CloakBrowser, без API лимитов\n\n'
            ),
            'meta_app_id_prompt': 'Meta App ID',
            'meta_app_secret_prompt': 'Meta App Secret',
            'publish_method_prompt': 'Метод публикации:',
            'method_api': 'API (Официальное Threads API)',
            'method_browser': 'Browser (CloakBrowser)',
            'cdp_url_prompt': 'CloakBrowser CDP URL',
            'ai_instructions': (
                '=== Настройка AI ===\n\n'
                'Поддерживается любой OpenAI-compatible API:\n'
                '• Ollama (локально): http://localhost:11434/v1\n'
                '• OpenAI: https://api.openai.com/v1\n'
                '• Любой совместимый сервер\n\n'
            ),
            'ai_base_url_prompt': 'AI Base URL (OpenAI-compatible)',
            'ai_api_key_prompt': 'AI API Key',
            'ai_model_prompt': 'AI Model',
            'ai_timeout_prompt': 'AI Timeout (секунды, по умолчанию 120)',
            'scheduler_instructions': (
                '=== Настройка планировщика ===\n\n'
                '• Posts per day - сколько постов в день\n'
                '• Post times - время публикации через запятую (ЧЧ:ММ)\n\n'
            ),
            'posts_per_day_prompt': 'Постов в день',
            'post_times_prompt': 'Время публикации (через запятую, ЧЧ:ММ)',
            'system_instructions': (
                '=== Системные настройки ===\n\n'
                'Уровень логирования: DEBUG показывает все, INFO - основное.\n\n'
            ),
            'log_level_prompt': 'Уровень логирования:',
            'persona_instructions': (
                '💡 Настройка AI Персонализации\n\n'
                'Persona - файл с инструкциями для AI, определяющий стиль письма и характер.\n'
                'Файл: config/prompts/persona.md\n\n'
                'Здесь вы можете:\n'
                '• Просмотреть текущую persona\n'
                '• Отредактировать стиль письма AI\n\n'
                'Совет: Хорошая persona включает тон, стиль и ключевые характеристики.'
            ),
            'ai_settings_menu': 'AI Настройки:',
            'edit_persona_instructions': (
                '=== Редактирование AI Persona ===\n\n'
                'Persona определяет как AI пишет посты.\n'
                'Вы можете описать характер, тон, стиль и правила.\n\n'
            ),
            'current_persona_label': 'Текущая persona:',
            'edit_persona_confirm': 'Редактировать persona?',
            'enter_persona_prompt': 'Введите новую persona (Ctrl+D или Ctrl+Z когда закончите):',
            'persona_updated': 'Persona обновлена!',
            'cancelled': 'Отменено',
            'no_persona_found': 'Файл persona не найден.',
            'create_default_persona': 'Создать persona по умолчанию?',
            'persona_created': 'Persona по умолчанию создана!',
            'skills_instructions': (
                '💡 Контентные Скиллы\n\n'
                'Скиллы - это шаблоны для разных типов контента.\n'
                'Файлы: config/skills/*.md\n\n'
                'Каждый скилл определяет:\n'
                '• Когда использовать (например, для туториалов)\n'
                '• Инструкции по написанию\n\n'
                'AI автоматически выбирает подходящий скилл на основе темы поста.\n\n'
            ),
            'no_skills_found': 'Скиллы не найдены.',
            'skills_dir_not_found': 'Директория скиллов не найдена.',
            'ai_provider_prompt': 'AI провайдер:',
            'provider_openai': 'OpenAI (совместимый API)',
            'provider_anthropic': 'Anthropic (Claude)',
            'ai_change_provider': 'Сменить провайдер',
            'ai_configure_current': 'Настроить текущий',
            'ai_current_settings': 'Текущий провайдер: {} | Модель: {}',
            'ai_provider_changed': 'Провайдер изменён на {}',
            'ai_openai_settings': '=== Настройка OpenAI (совместимый API) ===',
            'ai_anthropic_settings': '=== Настройка Anthropic ===',
            'mcp_settings': '🔌 MCP серверы',
            'mcp_instructions': (
                '=== MCP (Model Context Protocol) ===\n\n'
                'MCP серверы позволяют AI использовать внешние инструменты:\n'
                '• Веб-поиск\n'
                '• Базы данных\n'
                '• API интеграции\n\n'
                'Конфигурация: config/mcp_servers.json\n\n'
            ),
            'mcp_settings_menu': 'MCP Настройки:',
            'mcp_add_server': '➕ Добавить сервер',
            'mcp_remove_server': '➖ Удалить сервер',
            'mcp_add_instructions': (
                '=== Добавление MCP сервера ===\n\n'
                'Формат команды:\n'
                '• Python: python -m mcp_server_name\n'
                '• Node: npx @org/mcp-server\n'
                '• Исполняемый файл: ./path/to/server\n\n'
            ),
            'mcp_name_prompt': 'Название сервера (например: web-search)',
            'mcp_command_prompt': 'Команда запуска (python/node/npx)',
            'mcp_args_prompt': 'Аргументы (через пробел)',
            'mcp_server_added': '✅ MCP сервер "{}" добавлен!',
            'mcp_select_remove': 'Выберите сервер для удаления:',
            'mcp_confirm_remove': 'Удалить MCP сервер "{}"?',
            'mcp_server_removed': '✅ MCP сервер "{}" удалён',
            'mcp_no_servers': 'Нет настроенных MCP серверов',
            'mcp_server_details': 'Детали MCP сервера: {}',
        }
    },
    'en': {
        'bot': {
            'welcome': (
                '👋 *Hello! I\'m Threads AutoPoster*\n\n'
                'I help you automatically publish posts to Threads.\n\n'
                '*Main commands:*\n'
                '/login - authorize in Threads\n'
                '/post - create post (with confirmation)\n'
                '/topics - manage topics\n'
                '/stats - statistics\n\n'
                'Choose action:'
            ),
            'access_denied': 'Access denied.',
            'back_to_menu': '◀️ Back to menu',
            'recommended': 'Recommended',
            'cancelled': '✅ Cancelled',

            # Menu buttons
            'menu_btn_post': '📝 Create post',
            'menu_btn_schedule': '⏰ Schedule',
            'menu_btn_topics': '📋 Topics',
            'menu_btn_stats': '📊 Statistics',
            'menu_btn_queue': '📬 Queue',
            'menu_btn_login': '🔐 Authorization',
            'menu_btn_settings': '⚙️ Settings',
            'menu_btn_persona': '🎭 Persona',
            'menu_btn_skills': '🎯 Skills',
            'menu_btn_help': '❓ Help',

            # Menu callbacks
            'menu_post': 'Send /post to create a new post.\n\nYou can also attach an image!',
            'menu_schedule': 'Send /schedule to schedule a post.\n\nBot will ask for topic and time.',
            'menu_queue_empty': '📭 Queue is empty.',
            'menu_queue_header': '📋 Posts in queue',
            'menu_login': 'Send /login to authorize in Threads.\n\nChoose method: OAuth or Browser.',
            'menu_topics_empty': '📭 No topics yet. Add with /addtopic <name>',
            'menu_topics_header': '📋 Topics:',
            'menu_help': (
                '*❓ Help:*\n\n'
                '/login - authorize in Threads via CloakBrowser\n'
                '/post - generate and publish post (with confirmation)\n'
                '/schedule <topic> <HH:MM> - schedule a post\n'
                '/topics - list of topics\n'
                '/addtopic <name> - add topic\n'
                '/queue - post queue\n'
                '/stats - publishing statistics\n'
                '/settings - current settings\n'
                '/cancel - cancel current action\n\n'
                '💡 You can attach an image to /post!'
            ),

            'oauth_callback_success': '✅ Authorization successful! You can close this window and return to Telegram.',
            'oauth_callback_error': '❌ Authorization error: {}',

         
            'login_oauth_btn': '📱 OAuth (Recommended)',
            'login_browser_btn': '🌐 Browser (CloakBrowser)',
            'login_select_method': '🔐 *Select authorization method:*\n\n• 📱 *OAuth* (Recommended) - official authorization via Meta API\n• 🌐 *Browser* - authorization via CloakBrowser\n\nSelect method:',
            'login_unknown_method': '❌ Unknown method. Send /login again.',
            'login_session_expired': '❌ Login session expired. Send /login again.',
            'switch_to': 'Switch to {}',
            'active_method': '🎯 *Active method:* `{}`',
            'method_switched': '✅ Publish method switched to `{}`',


            'oauth_not_configured': (
                '❌ *OAuth not configured*\n\n'
                'You need to configure variables in `.env`:\n'
                '• `META_APP_ID`\n'
                '• `META_APP_SECRET`\n\n'
                'Follow the README instructions for OAuth setup.'
            ),
            'oauth_token_exists': (
                '✅ *You already have a valid token!*\n\n'
                'Authorization is already done. You can use /post to publish.'
            ),
            'oauth_start': (
                '📱 *OAuth authorization*\n\n'
                'Starting local server for authorization...\n'
                'After that, a browser will open for Meta authorization.'
            ),
            'oauth_browser_opened': (
                '🌐 *Browser opened automatically!*\n\n'
                'Authorize in Meta. After successful authorization you will return to the bot.\n\n'
                'If the browser didn\'t open, follow the link manually:\n'
                '{}'
            ),
            'oauth_timeout': '❌ Authorization timeout expired. Try again.',
            'oauth_no_code': '❌ Failed to get authorization code. Try again.',
            'oauth_exchanging': '🔄 Exchanging code for token...',
            'oauth_exchange_failed': '❌ Failed to exchange code for token. Try again.',
            'oauth_long_lived_failed': '❌ Failed to get long-lived token. Try again.',
            'oauth_user_id_failed': '❌ Failed to get Threads User ID. Try again.',
            'oauth_success_msg': (
                '✅ *OAuth authorization successful!*\n\n'
                'Received long-lived token (valid for 60 days).\n'
                'Threads User ID: `{}`\n\n'
                'Now you can use /post to publish posts.'
            ),
            'oauth_error': '❌ OAuth authorization error: {}',

          
            'browser_checking': '🔍 Checking CloakBrowser...',
            'browser_not_running': '🔄 CloakBrowser is not running, launching automatically...',
            'browser_launch_failed': (
                '❌ Failed to launch CloakBrowser.\n\n'
                'Check logs (logs/app.log) for details.\n\n'
                '*Try manually:*\n'
                '1. `CloakBrowser.exe install`\n'
                '2. Restart the bot and try /login again'
            ),
            'browser_launched': '✅ CloakBrowser launched!',
            'browser_connecting': '🔗 Connecting to browser...',
            'browser_checking_auth': '🤖 Checking authorization status...',
            'browser_already_logged_in': '✅ You are already logged in to Threads! You can send /post <topic>',
            'browser_auth_active': '✅ Authorization is active. Send /post <topic> to publish.',
            'browser_opening_login': '🤖 Opening login page...',
            'browser_login_page_failed': '❌ Failed to open login page. Try /login again.',
            'browser_enter_username': '📝 Enter username (email or username):',
            'browser_login_page_caption': '🤖 Login page opened. Ready to fill the form.',

          
            'login_entering_username': '🤖 Entering username...',
            'login_enter_password': '🔐 Enter password:',
            'login_username_field_not_found': '❌ Could not find username field. Try /login again.',
            'login_entering_password': '🤖 Entering password and submitting...',
            'login_password_field_not_found': '❌ Could not find password field.',
            'login_success_caption': '✅ Successful Threads authorization!',
            'login_success_msg': '✅ Authorized! You can send /post <topic> to publish.',
            'login_2fa_required': '🔐 Two-factor authentication code required.',
            'login_2fa_caption': '🔐 Two-factor authentication code required.',
            'login_enter_2fa': '🔢 Send the 6-digit code:',
            'login_2fa_invalid': '⚠️ Code must contain 6 digits. Try again:',
            'login_entering_2fa': '🤖 Entering 2FA code...',
            'login_2fa_error': '❌ 2FA error: {}',
            'login_2fa_wrong': '❌ Wrong code. Send /login to try again.',
            'login_error_caption': '❌ Login error: {}',
            'login_wrong_credentials': '❌ Wrong login or password. Send /login to try again.',
            'login_unknown_status': '⚠️ Status: {}',
            'login_unknown_status_msg': '⚠️ Could not determine result. Check the screenshot and try /login again.',
            'login_cancelled': '✅ Authorization process cancelled.',
            'login_no_active': 'ℹ️ No active authorization process.',
            'login_error': '❌ Error: {}',

       
            'post_enter_topic': '📝 Enter post topic:\n\n💡 You can also attach an image!',
            'post_generating': '🤖 Generating post on topic: {}...',
            'post_image_received': '📸 Image received, saving...',
            'post_generation_failed': '❌ Failed to generate post. Check logs.',
            'post_preview': '📝 *Generated post:*',
            'post_image_attached': '\n\n🖼️ Image attached',
            'post_approve': '✅ Publish',
            'post_edit': '✏️ Edit',
            'post_cancel': '❌ Cancel',
            'post_generation_error': '❌ Generation error: {}',
            'post_not_found': '❌ Post not found or time expired.',
            'post_publishing': '🚀 Publishing post to Threads...',
            'post_published': '✅ Post successfully published to Threads!',
            'post_publish_failed': (
                '❌ Failed to publish post.\n\n'
                'Possible reasons:\n'
                '• Not authorized in Threads (send /login)\n'
                '• CloakBrowser is not running\n'
                '• Threads interface has changed'
            ),
            'post_publish_error': '❌ Publishing error: {}',
            'post_edit_prompt': '✏️ Send new post text:\n\n(Or /cancel to cancel)',
            'post_edited_preview': '📝 *Edited post:*',
            'post_cancelled': '❌ Post cancelled.',


            'schedule_enter_topic': '📝 Enter post topic:',
            'schedule_enter_time': '⏰ Enter publish time (HH:MM):',
            'schedule_generating': '🤖 Generating post on topic: {}...',
            'schedule_success': '✅ Post scheduled for {}\nID: {}\n\nContent is already generated and will be published at the specified time.',
            'schedule_failed': (
                '❌ Failed to generate post.\n\n'
                'Possible reasons:\n'
                '• AI service is unavailable\n'
                '• Incorrect AI settings (AI_BASE_URL, AI_API_KEY, AI_MODEL)\n\n'
                'Check settings via /settings'
            ),
            'schedule_time_error': '⚠️ Invalid time format. Use HH:MM (e.g., 15:30)',
            'schedule_error': '❌ Error: {}',


            'addtopic_enter_name': '📝 Enter topic name:',
            'addtopic_success': '✅ Topic added: {} (ID: {})',
            'addtopic_failed': '❌ Failed to add topic.',

            'queue_scheduled': ' (scheduled: {})',

            'stats_title': '*📊 Statistics:*',
            'stats_total': 'Total:',
            'stats_published': 'Published:',
            'stats_pending': 'Pending:',
            'stats_failed': 'Failed:',
            'stats_success_rate': 'Success rate:',
            'stats_today': 'Today:',
            'stats_yesterday_label': 'Yesterday:',
            'stats_yesterday_trend': ' ({trend} {diff:+d} vs yesterday)',
            'stats_activity': 'Activity for 7 days:',

            'settings_header': '⚙️ *Current settings:*',
            'settings_ai_url': 'AI URL:',
            'settings_model': 'Model:',
            'settings_method': 'Method:',
            'settings_posts_per_day': 'Posts/day:',
            'settings_times': 'Times:',


            'persona_not_found': '❌ Persona file not found. Create `config/prompts/persona.md`',
            'persona_truncated': '\n\n...(truncated)',
            'persona_current': '🎭 *Current Persona:*',
            'persona_edit': '✏️ Edit',
            'persona_edit_prompt': '✏️ Send new persona text:\n\n(Or /cancel to cancel)',
            'persona_saved': '✅ Persona saved',


            'skills_dir_not_found': '❌ Skills directory not found.',
            'skills_empty': '📭 No skills available.',
            'skills_header': '🎯 *Available skills:*',
            'skills_hint': '\n💡 Use `/post <topic>` and AI will automatically select the appropriate skill!',
        },
        'cli': {
            'main_menu': 'Main Menu:',
            'settings': 'Settings',
            'run_bot': 'Run Bot',
            'exit': 'Exit',
            'language_select': 'Select language / Выберите язык:',
            'settings_menu': 'Settings:',
            'telegram_bot': 'Telegram Bot',
            'threads_api': 'Threads API',
            'ai_config': 'AI Configuration',
            'ai_persona': 'AI Personalization',
            'scheduler': 'Scheduler',
            'system': 'System',
            'save_exit': 'Save & Exit',
            'back': 'Back',
            'persona_description': (
                '=== AI Personalization ===\n\n'
                'Persona is a file with instructions for AI, defining writing style and character.\n'
                'File: config/prompts/persona.md\n\n'
                'Here you can:\n'
                '- View current persona\n'
                '- Edit AI writing style\n\n'
            ),
            'skills_description': (
                '=== Content Skills ===\n\n'
                'Skills are templates for different content types.\n'
                'Files: config/skills/*.md\n\n'
                'Each skill defines:\n'
                '- When to use (e.g., for tutorials)\n'
                '- Writing instructions\n\n'
                'AI automatically selects the appropriate skill based on the post topic.\n\n'
            ),
            'edit_persona': 'Edit Persona',
            'view_skills': 'View Skills',
            'no_env': 'No .env file found. Let\'s set up your configuration.',
            'error_token': 'Error: TELEGRAM_BOT_TOKEN is required!',
            'error_admin_ids': 'Error: TELEGRAM_ADMIN_IDS is required!',
            'error_meta_app_id': 'Error: META_APP_ID is required!',
            'error_meta_app_secret': 'Error: META_APP_SECRET is required!',
            'run_setup_hint': 'Run with --setup flag to configure: python main.py --setup',
            'telegram_settings': 'Telegram Bot',
            'threads_settings': 'Threads API',
            'ai_settings': 'AI Configuration',
            'persona_settings': 'AI Personalization',
            'scheduler_settings': 'Scheduler',
            'system_settings': 'System',
            'save_confirm': 'Save configuration?',
            'save_success': 'Configuration saved successfully!',
            'telegram_instructions': (
                '=== Telegram Bot Setup ===\n\n'
                '• Bot Token - get from @BotFather in Telegram\n'
                '• Admin IDs - comma-separated user IDs who can control the bot\n\n'
            ),
            'bot_token_prompt': 'Bot Token (from @BotFather)',
            'admin_ids_prompt': 'Admin IDs (comma-separated)',
            'threads_instructions': (
                '=== Threads API Setup ===\n\n'
                '• Meta App ID and Secret - from Meta Developer Console\n'
                '• API method - official, with limits (~250 posts/day)\n'
                '• Browser method - via CloakBrowser, no API limits\n\n'
            ),
            'meta_app_id_prompt': 'Meta App ID',
            'meta_app_secret_prompt': 'Meta App Secret',
            'publish_method_prompt': 'Publishing method:',
            'method_api': 'API (Official Threads API)',
            'method_browser': 'Browser (CloakBrowser)',
            'cdp_url_prompt': 'CloakBrowser CDP URL',
            'ai_instructions': (
                '=== AI Configuration ===\n\n'
                'Supports any OpenAI-compatible API:\n'
                '• Ollama (local): http://localhost:11434/v1\n'
                '• OpenAI: https://api.openai.com/v1\n'
                '• Any compatible server\n\n'
            ),
            'ai_base_url_prompt': 'AI Base URL (OpenAI-compatible)',
            'ai_api_key_prompt': 'AI API Key',
            'ai_model_prompt': 'AI Model',
            'scheduler_instructions': (
                '=== Scheduler Setup ===\n\n'
                '• Posts per day - how many posts per day\n'
                '• Post times - publication times comma-separated (HH:MM)\n\n'
            ),
            'posts_per_day_prompt': 'Posts per day',
            'post_times_prompt': 'Post times (comma-separated, HH:MM)',
            'system_instructions': (
                '=== System Settings ===\n\n'
                'Log level: DEBUG shows everything, INFO shows main events.\n\n'
            ),
            'log_level_prompt': 'Log level:',
            'persona_instructions': (
                '💡 AI Personalization Configuration\n\n'
                'Persona is a file with instructions for AI, defining writing style and character.\n'
                'File: config/prompts/persona.md\n\n'
                'Here you can:\n'
                '• View current persona\n'
                '• Edit AI writing style\n\n'
                'Tip: A good persona includes tone, style, and key characteristics.'
            ),
            'ai_settings_menu': 'AI Settings:',
            'edit_persona_instructions': (
                '=== Edit AI Persona ===\n\n'
                'Persona defines how AI writes posts.\n'
                'You can describe character, tone, style, and rules.\n\n'
            ),
            'current_persona_label': 'Current persona:',
            'edit_persona_confirm': 'Edit persona?',
            'enter_persona_prompt': 'Enter new persona (Ctrl+D or Ctrl+Z when done):',
            'persona_updated': 'Persona updated!',
            'cancelled': 'Cancelled',
            'no_persona_found': 'Persona file not found.',
            'create_default_persona': 'Create default persona?',
            'persona_created': 'Default persona created!',
            'skills_instructions': (
                '💡 Content Skills\n\n'
                'Skills are templates for different content types.\n'
                'Files: config/skills/*.md\n\n'
                'Each skill defines:\n'
                '• When to use (e.g., for tutorials)\n'
                '• Writing instructions\n\n'
                'AI automatically selects the appropriate skill based on the post topic.\n\n'
            ),
            'no_skills_found': 'No skills found.',
            'skills_dir_not_found': 'Skills directory not found.',
            'ai_provider_prompt': 'AI provider:',
            'provider_openai': 'OpenAI (compatible API)',
            'provider_anthropic': 'Anthropic (Claude)',
            'ai_change_provider': 'Change provider',
            'ai_configure_current': 'Configure current',
            'ai_current_settings': 'Current provider: {} | Model: {}',
            'ai_provider_changed': 'Provider changed to {}',
            'ai_openai_settings': '=== Configure OpenAI (compatible API) ===',
            'ai_anthropic_settings': '=== Configure Anthropic ===',
            'mcp_settings': '🔌 MCP servers',
            'mcp_instructions': (
                '=== MCP (Model Context Protocol) ===\n\n'
                'MCP servers allow AI to use external tools:\n'
                '• Web search\n'
                '• Databases\n'
                '• API integrations\n\n'
                'Configuration: config/mcp_servers.json\n\n'
            ),
            'mcp_settings_menu': 'MCP Settings:',
            'mcp_add_server': '➕ Add server',
            'mcp_remove_server': '➖ Remove server',
            'mcp_add_instructions': (
                '=== Adding MCP server ===\n\n'
                'Command format:\n'
                '• Python: python -m mcp_server_name\n'
                '• Node: npx @org/mcp-server\n'
                '• Executable: ./path/to/server\n\n'
            ),
            'mcp_name_prompt': 'Server name (e.g., web-search)',
            'mcp_command_prompt': 'Launch command (python/node/npx)',
            'mcp_args_prompt': 'Arguments (space-separated)',
            'mcp_server_added': '✅ MCP server "{}" added!',
            'mcp_select_remove': 'Select server to remove:',
            'mcp_confirm_remove': 'Remove MCP server "{}"?',
            'mcp_server_removed': '✅ MCP server "{}" removed',
            'mcp_no_servers': 'No configured MCP servers',
            'mcp_server_details': 'MCP server details: {}',
        }
    }
}

currentLang = 'ru'

def setLang(lang: str):
    global currentLang
    currentLang = lang

def getLang():
    return currentLang

def t(section: str, key: str, *args, **kwargs):
    text = translations.get(currentLang, translations['ru']).get(section, {}).get(key, key)
    if args or kwargs:
        return text.format(*args, **kwargs)
    return text

set_lang = setLang
get_lang = getLang
