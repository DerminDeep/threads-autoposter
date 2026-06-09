# Threads AutoPoster

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-blue)](https://docs.aiogram.dev/)

Automated posting system for [Threads](https://www.threads.net) (Meta) with AI-generated content and Telegram bot control.

**[Русская версия](README.ru.md)**

## Features

- AI content generation via any OpenAI-compatible API (Ollama, vLLM, OpenAI, etc.)
- **AI Personalization** - customize AI writing style and personality
- **Skills System** - specialized content templates (tutorials, stories, tips)
- Web search integration (MCP) for up-to-date context in posts
- Post approval flow (preview before publishing)
- Image attachment support
- Flexible scheduling with APScheduler
- **Interactive CLI Setup** - configure everything without editing .env files
- Telegram bot management interface (aiogram 3.x)
- Two publishing methods:
  - **Official Threads API** - stable, verified, rate-limited
  - **CloakBrowser** - anti-detect browser automation, no API limits
- SQLite database for post storage

## Quick Start

### Option 1: Interactive CLI Setup (Recommended)

```bash
git clone <repository-url>
cd threads-autoposter
pip install -r requirements.txt
python main.py
```

On first run, the interactive setup wizard will guide you through all configuration:
- Telegram bot token and admin IDs
- Meta API credentials or CloakBrowser setup
- AI provider settings (Ollama, OpenAI, etc.)
- **AI Persona** - customize how AI writes (tone, style, personality)
- **Skills** - specialized content templates (tutorials, stories, tips, etc.)
- Scheduler settings

Navigate with arrow keys and Enter. No need to edit .env files manually!

### Option 2: Manual Configuration

```bash
git clone <repository-url>
cd threads-autoposter
pip install -r requirements.txt
cp .env.example .env
# edit .env with your credentials
python main.py
```

You can also run setup manually anytime with:
```bash
python main.py --setup
```

## Project Structure

```
threads-autoposter/
├── bot/
│   ├── handlers.py       # Telegram command handlers (aiogram 3.x)
│   └── tgbot.py          # Telegram bot initialization and menu
├── config/
│   └── settings.py       # Configuration from .env
├── core/
│   ├── ai.py             # AI provider (OpenAI-compatible)
│   ├── generator.py      # Content generation with MCP web search
│   ├── mcp_client.py     # MCP web search client
│   ├── browser_launcher.py  # CloakBrowser auto-launch and management
│   ├── scheduler.py      # APScheduler for scheduled posts
│   ├── threads.py        # Threads API publisher + CloakBrowser publisher
│   ├── threadsLogin.py   # AI agent for Threads login via browser
│   └── threadsPublish.py # AI agent for Threads publishing via browser
├── database/
│   └── models.py         # SQLite models and migrations
├── utils/
│   └── logger.py         # Loguru configuration
├── data/                 # SQLite DB and images
├── logs/                 # Application logs
├── main.py               # Entry point
├── .env.example          # Environment template
└── requirements.txt
```

---

## Publishing Methods

### Method 1: Official Threads API (Recommended)

Uses Meta Graph API. Stable and reliable, requires a Meta Developer App.

**Rate limits:** ~250 posts per 24 hours per user.

#### Setup

##### 1. Create a Meta Developer App

1. Go to [developers.facebook.com](https://developers.facebook.com/) and sign in
2. Click **My Apps** > **Create App**
3. Select type: **Business** (or **Consumer**)
4. Fill in **App name** and **App contact email**, click **Create App**
5. Find **Threads** product and click **Set up**

##### 2. Get App Credentials

In your App Dashboard, find **App ID** and **App Secret** (Settings > Basic). Add them to `.env`:

```env
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
PUBLISH_METHOD=api
```

##### 3. Authorize via Bot

Run `/login` in Telegram bot, select **OAuth** - the bot will handle everything automatically:
- Opens browser with Meta authorization page
- Receives the callback code via local server
- Exchanges code for short-lived token, then for long-lived token (60 days)
- Fetches your Threads User ID
- Saves all tokens to database

No manual token management needed.

#### How Publishing Works via API

```
1. POST /{user-id}/threads        -> Creates a media container
2. POST /{user-id}/threads_publish -> Publishes the container
```

---

### Method 2: CloakBrowser (Anti-Detect Browser)

Automates the Threads web interface through CloakBrowser. No API verification needed, but carries a risk of account restrictions.

#### What is CloakBrowser?

[CloakBrowser](https://github.com/nicepkg/CloakBrowser) is an anti-detect browser based on Chromium. It creates unique browser fingerprints to avoid detection. This project connects to it via Chrome DevTools Protocol (CDP).

#### Step-by-Step Setup

##### 1. Install CloakBrowser

The bot will attempt to auto-install CloakBrowser CLI and the browser itself on first `/login`. If auto-install fails:

```bash
pip install cloakbrowser
cloakbrowser install
```

The browser will be installed to `~/.cloakbrowser/`.

##### 2. Configure CDP URL

Default CDP endpoint is `http://localhost:9222`. Set in `.env`:
```env
PUBLISH_METHOD=browser
CLOAKBROWSER_CDP_URL=http://localhost:9222
```

##### 3. How It Works

1. Bot launches CloakBrowser with `--remote-debugging-port=9222`
2. Playwright connects to CloakBrowser via CDP
3. AI agent navigates to `threads.net`
4. Agent finds the "Create" button, opens the post modal
5. Agent fills in the text and (optionally) uploads an image
6. Agent clicks "Post" and verifies the modal closes
7. Screenshots are sent to the Telegram chat at each step

##### 4. Important Notes

- **Account ban risk**: Threads may detect automated behavior. Use at your own risk.
- **UI changes**: Threads frequently updates their interface. Selectors may break and require code updates.
- **CloakBrowser must stay running** while publishing. The bot auto-launches it, but you can also start it manually.
- **One session at a time**: Don't use CloakBrowser for other tasks while the bot is publishing.
- **Anti-detect**: CloakBrowser provides fingerprint randomization, but this is not a guarantee against detection.

##### 5. Troubleshooting

| Problem | Solution |
|---|---|
| "Cannot connect to CloakBrowser" | Check if CDP port 9222 is available. Kill other Chrome instances. |
| "Create button not found" | Threads UI may have changed. Check screenshots in Telegram. |
| "Modal did not close" | Post button click may have failed. Check logs. |
| Browser crashes | Increase system resources or restart CloakBrowser. |
| Login session lost | Run `/login` again. Sessions persist in CloakBrowser profile. |

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_ADMIN_IDS` | Yes | - | Comma-separated Telegram user IDs with access |
| `PUBLISH_METHOD` | No | `api` | `api` or `browser` |
| `META_APP_ID` | OAuth only | - | Your Meta App ID (real value from Meta Developer Console) |
| `META_APP_SECRET` | OAuth only | - | Your Meta App Secret (real value from Meta Developer Console) |
| `THREADS_USER_ID` | Auto | - | Obtained automatically via `/login` |
| `THREADS_ACCESS_TOKEN` | Auto | - | Obtained automatically via `/login` |
| `CLOAKBROWSER_CDP_URL` | Browser only | `http://localhost:9222` | CloakBrowser CDP endpoint |
| `AI_BASE_URL` | No | `http://localhost:11434/v1` | OpenAI-compatible API endpoint |
| `AI_API_KEY` | No | `""` | API key for AI provider |
| `AI_MODEL` | No | `llama3` | Model name |
| `DEFAULT_POSTS_PER_DAY` | No | `3` | Default post frequency |
| `DEFAULT_POST_TIMES` | No | `10:00,15:00,20:00` | Default posting times |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### AI Provider

The bot uses any OpenAI-compatible API endpoint. Examples:

- **Ollama** (local, free): `AI_BASE_URL=http://localhost:11434/v1`
- **OpenAI**: `AI_BASE_URL=https://api.openai.com/v1` + `AI_API_KEY=sk-...`
- **vLLM / llama.cpp**: Any server that implements the OpenAI chat completions API
- **Custom endpoint**: Any compatible proxy

### MCP Web Search

The bot integrates with an MCP (Model Context Protocol) web search server to fetch real-time information for post generation. Point `mcp_client.py` to your MCP server path.

### AI Personalization

Customize how the AI writes posts by editing `config/prompts/persona.md`:

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

**Via CLI**: Settings → AI Personalization & Skills → Edit Persona

**Via Telegram**: `/persona` command

### Skills System

Skills are specialized content templates that guide AI for specific content types. Located in `config/skills/`:

**Built-in Skills:**
- `tutorial.md` - How-to guides and step-by-step instructions
- `story.md` - Personal stories and case studies
- `tips.md` - Tips, lifehacks, and useful lists

**Example skill (tutorial.md):**
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

**Creating custom skills:**
1. Create `.md` file in `config/skills/`
2. Describe when to use and instructions
3. AI will automatically use it based on content type

**Via CLI**: Settings → AI Personalization & Skills → Create New Skill

**Via Telegram**: `/skills` command

---

## Telegram Commands

| Command | Description |
|---|---|
| `/start` | Welcome message with menu |
| `/post [topic]` | Generate post on topic. Without args, prompts for topic |
| `/schedule <topic> <HH:MM>` | Schedule a post for a specific time |
| `/topics` | List all saved topics |
| `/addtopic <name>` | Add a new topic |
| `/queue` | Show pending posts |
| `/stats` | Show publishing statistics |
| `/settings` | View current configuration |
| `/persona` | View current AI persona configuration |
| `/skills` | List available content skills |
| `/login` | Authorize in Threads (choose OAuth or Browser method) |
| `/cancel` | Cancel current action |
| `/help` | Show help |

### Post Approval Flow

1. Send `/post <topic>` (or `/post` and then the topic)
2. Optionally attach an image
3. AI generates post content (with web search context)
4. Preview is shown with 3 buttons: **Approve**, **Edit**, **Cancel**
5. On approve, the post is published immediately

---

## Running

```bash
python main.py
```

The bot starts:
1. SQLite database initialization
2. APScheduler for scheduled posts
3. Telegram bot polling
4. CloakBrowser auto-launch (on first publish, browser method only)

---

## License

MIT
