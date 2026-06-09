# Threads AutoPoster

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-blue)](https://docs.aiogram.dev/)

Автоматизированная система постинга в [Threads](https://www.threads.net) (Meta) с генерацией контента через ИИ и управлением через Telegram бота.

**[English version](README.md)**

## Возможности

- Генерация контента через любой OpenAI-compatible API (Ollama, vLLM, OpenAI и т.д.)
- **Персонализация ИИ** - настройте стиль письма и характер ИИ
- **Система скиллов** - специализированные шаблоны контента (туториалы, истории, советы)
- Интеграция веб-поиска (MCP) для актуального контекста в постах
- **Интерактивная CLI настройка** - настройте всё без редактирования .env файлов
- Процесс одобрения постов (превью перед публикацией)
- Поддержка прикрепления изображений
- Гибкое планирование через APScheduler
- Интерфейс управления через Telegram бота (aiogram 3.x)
- Два метода публикации:
  - **Официальное Threads API** - стабильно, верифицировано, с лимитами
  - **CloakBrowser** - антидетект браузер автоматизация, без API лимитов
- База данных SQLite для хранения постов

## Быстрый старт

### Вариант 1: Интерактивная настройка (Рекомендуется)

```bash
git clone https://github.com/DerminDeep/threads-autoposter.git
cd threads-autoposter
pip install -r requirements.txt
python main.py --setup
```

Интерактивный мастер проведёт вас через настройку:
- Telegram бот токен и ID администраторов
- Настройка Meta API или CloakBrowser
- Настройка AI провайдера
- Персонализация ИИ (стиль письма, тон, характер)
- Создание и управление скиллами контента
- Настройка расписания

### Вариант 2: Ручная настройка

```bash
git clone https://github.com/DerminDeep/threads-autoposter.git
cd threads-autoposter
pip install -r requirements.txt
cp .env.example .env
# отредактируйте .env с вашими данными
python main.py
```

## Структура проекта

```
threads-autoposter/
├── bot/
│   ├── handlers.py       # Обработчики команд Telegram (aiogram 3.x)
│   └── tgbot.py          # Инициализация Telegram бота и меню
├── config/
│   └── settings.py       # Конфигурация из .env
├── core/
│   ├── ai.py             # AI провайдер (OpenAI-compatible)
│   ├── generator.py      # Генерация контента с MCP веб-поиском
│   ├── mcp_client.py     # MCP клиент для веб-поиска
│   ├── browser_launcher.py  # Автозапуск и управление CloakBrowser
│   ├── scheduler.py      # APScheduler для запланированных постов
│   ├── threads.py        # Threads API publisher + CloakBrowser publisher
│   ├── threadsLogin.py   # AI агент для входа в Threads через браузер
│   └── threadsPublish.py # AI агент для публикации в Threads через браузер
├── database/
│   └── models.py         # SQLite модели и миграции
├── utils/
│   └── logger.py         # Конфигурация Loguru
├── data/                 # SQLite БД и изображения
├── logs/                 # Логи приложения
├── main.py               # Точка входа
├── .env.example          # Шаблон окружения
└── requirements.txt
```

---

## Методы публикации

### Метод 1: Официальное Threads API (Рекомендуется)

Использует Meta Graph API. Стабильно и надежно, требует Meta Developer App.

**Лимиты:** ~250 постов в 24 часа на пользователя.

#### Настройка

##### 1. Создайте Meta Developer App

1. Перейдите на [developers.facebook.com](https://developers.facebook.com/) и войдите
2. Нажмите **My Apps** > **Create App**
3. Выберите тип: **Business** (или **Consumer**)
4. Заполните **App name** и **App contact email**, нажмите **Create App**
5. Найдите продукт **Threads** и нажмите **Set up**

##### 2. Получите данные приложения

В App Dashboard найдите **App ID** и **App Secret** (Settings > Basic). Вы можете настроить их:

**Вариант A: Через CLI (Рекомендуется)**
Запустите `python main.py --setup`, выберите Threads Settings и введите Meta App ID и App Secret когда будет предложено.

**Вариант B: Ручное редактирование .env**
Добавьте их в `.env`:

```env
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
PUBLISH_METHOD=api
```

##### 3. Авторизуйтесь через бота

Отправьте `/login` в Telegram боте, выберите **OAuth** - бот сделает все автоматически:
- Откроет браузер со страницей авторизации Meta
- Получит callback код через локальный сервер
- Обменяет код на short-lived токен, затем на long-lived (60 дней)
- Получит ваш Threads User ID
- Сохранит все токены в базу данных

Ручное управление токенами не требуется.

#### Как работает публикация через API

```
1. POST /{user-id}/threads        -> Создает media container
2. POST /{user-id}/threads_publish -> Публикует container
```

---

### Метод 2: CloakBrowser (Антидетект браузер)

Автоматизирует веб-интерфейс Threads через CloakBrowser. Не требует верификации API, но несет риск ограничений аккаунта.

#### Что такое CloakBrowser?

[CloakBrowser](https://github.com/nicepkg/CloakBrowser) - антидетект браузер на базе Chromium. Создает уникальные отпечатки браузера для избежания обнаружения. Этот проект подключается к нему через Chrome DevTools Protocol (CDP).

#### Пошаговая настройка

##### 1. Установите CloakBrowser

Бот попытается автоматически установить CloakBrowser CLI и сам браузер при первом `/login`. Если автоустановка не удалась:

```bash
pip install cloakbrowser
cloakbrowser install
```

Браузер будет установлен в `~/.cloakbrowser/`.

##### 2. Настройте CDP URL

По умолчанию CDP endpoint - `http://localhost:9222`. Установите в `.env`:
```env
PUBLISH_METHOD=browser
CLOAKBROWSER_CDP_URL=http://localhost:9222
```

##### 3. Как это работает

1. Бот запускает CloakBrowser с `--remote-debugging-port=9222`
2. Playwright подключается к CloakBrowser через CDP
3. AI агент переходит на `threads.net`
4. Агент находит кнопку "Создать", открывает модальное окно поста
5. Агент заполняет текст и (опционально) загружает изображение
6. Агент нажимает "Опубликовать" и проверяет закрытие модального окна
7. Скриншоты отправляются в Telegram чат на каждом шаге

##### 4. Важные замечания

- **Риск бана аккаунта**: Threads может обнаружить автоматизированное поведение. Используйте на свой риск.
- **Изменения UI**: Threads часто обновляет интерфейс. Селекторы могут сломаться и потребовать обновления кода.
- **CloakBrowser должен работать** во время публикации. Бот автозапускает его, но вы можете запустить вручную.
- **Одна сессия за раз**: Не используйте CloakBrowser для других задач пока бот публикует.
- **Антидетект**: CloakBrowser предоставляет рандомизацию отпечатков, но это не гарантия от обнаружения.

##### 5. Устранение неполадок

| Проблема | Решение |
|---|---|
| "Cannot connect to CloakBrowser" | Проверьте доступность CDP порта 9222. Закройте другие экземпляры Chrome. |
| "Create button not found" | Threads UI мог измениться. Проверьте скриншоты в Telegram. |
| "Modal did not close" | Нажатие кнопки Post могло не сработать. Проверьте логи. |
| Браузер крашится | Увеличьте системные ресурсы или перезапустите CloakBrowser. |
| Сессия логина потеряна | Запустите `/login` снова. Сессии сохраняются в профиле CloakBrowser. |

---

## Конфигурация

### Переменные окружения

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Да | - | Токен бота от [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_ADMIN_IDS` | Да | - | Список Telegram user ID через запятую с доступом |
| `PUBLISH_METHOD` | Нет | `api` | `api` или `browser` |
| `META_APP_ID` | Только OAuth | - | Ваш Meta App ID (реальное значение из Meta Developer Console) |
| `META_APP_SECRET` | Только OAuth | - | Ваш Meta App Secret (реальное значение из Meta Developer Console) |
| `THREADS_USER_ID` | Автоматически | - | Получается автоматически через `/login` |
| `THREADS_ACCESS_TOKEN` | Автоматически | - | Получается автоматически через `/login` |
| `CLOAKBROWSER_CDP_URL` | Только Browser | `http://localhost:9222` | CloakBrowser CDP endpoint |
| `AI_BASE_URL` | Нет | `http://localhost:11434/v1` | OpenAI-compatible API endpoint |
| `AI_API_KEY` | Нет | `""` | API ключ для AI провайдера |
| `AI_MODEL` | Нет | `llama3` | Название модели |
| `DEFAULT_POSTS_PER_DAY` | Нет | `3` | Частота постов по умолчанию |
| `DEFAULT_POST_TIMES` | Нет | `10:00,15:00,20:00` | Время публикации по умолчанию |
| `LOG_LEVEL` | Нет | `INFO` | Уровень логирования |

### AI провайдер

Бот использует любой OpenAI-compatible API endpoint. Примеры:

- **Ollama** (локально, бесплатно): `AI_BASE_URL=http://localhost:11434/v1`
- **OpenAI**: `AI_BASE_URL=https://api.openai.com/v1` + `AI_API_KEY=sk-...`
- **vLLM / llama.cpp**: Любой сервер, реализующий OpenAI chat completions API
- **Кастомный endpoint**: Любой совместимый прокси

### MCP веб-поиск

Бот интегрируется с MCP (Model Context Protocol) сервером веб-поиска для получения актуальной информации при генерации постов. Укажите путь к вашему MCP серверу в `mcp_client.py`.

### Персонализация ИИ

Настройте стиль письма ИИ, отредактировав `config/prompts/persona.md`:

```markdown
# AI Persona

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
```

**Через CLI**: Settings → AI Personalization & Skills → Edit Persona

**Через Telegram**: команда `/persona`

### Система скиллов

Скиллы - это специализированные шаблоны контента, которые направляют ИИ для создания определённых типов контента. Расположены в `config/skills/`:

**Встроенные скиллы:**
- `tutorial.md` - How-to руководства и пошаговые инструкции
- `story.md` - Личные истории и кейсы
- `tips.md` - Советы, лайфхаки и полезные списки

**Пример скилла (tutorial.md):**
```markdown
# Skill: Tutorial

## When to use
For educational posts, instructions, how-to content.

## Instructions
- Start with the problem the tutorial solves
- Break into clear steps (1, 2, 3...)
- Use simple examples
- End with result or next step
- Add "Try it and let me know how it went!"
```

**Создание собственных скиллов:**
1. Создайте `.md` файл в `config/skills/`
2. Опишите, когда использовать, и инструкции
3. ИИ будет автоматически использовать его на основе типа контента

**Через CLI**: Settings → AI Personalization & Skills → Create New Skill

**Через Telegram**: команда `/skills`

---

## Команды Telegram

| Команда | Описание |
|---|---|
| `/start` | Приветственное сообщение с меню |
| `/post [тема]` | Генерация поста на тему. Без аргументов запрашивает тему |
| `/schedule <тема> <ЧЧ:ММ>` | Запланировать пост на определенное время |
| `/topics` | Список всех сохраненных тем |
| `/addtopic <название>` | Добавить новую тему |
| `/queue` | Показать посты в очереди |
| `/stats` | Показать статистику публикаций |
| `/settings` | Просмотр текущей конфигурации |
| `/login` | Авторизация в Threads (выбор OAuth или Browser) |
| `/cancel` | Отменить текущее действие |
| `/help` | Показать справку |

### Процесс одобрения поста

1. Отправьте `/post <тема>` (или `/post` и затем тему)
2. Опционально прикрепите изображение
3. AI генерирует контент поста (с контекстом веб-поиска)
4. Показывается превью с 3 кнопками: **Одобрить**, **Редактировать**, **Отменить**
5. При одобрении пост публикуется немедленно

---

## Запуск

```bash
python main.py
```

Бот запускает:
1. Инициализация SQLite базы данных
2. APScheduler для запланированных постов
3. Telegram bot polling
4. Автозапуск CloakBrowser (при первой публикации, только browser метод)

---

## Лицензия

MIT
