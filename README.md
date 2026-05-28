# Telegram Bot with Aiogram 3.x

A simple Telegram bot built with [Aiogram](https://github.com/aiogram/aiogram) - a modern, fully asynchronous framework for Telegram Bot API.

## Features

- Echo functionality - bot replies with the same message
- `/start` and `/help` commands
- Modular structure with Router pattern
- FSM (Finite State Machine) ready for complex flows

## Project Structure

```
bot-telegram/
├── app/
│   ├── __init__.py
│   ├── bot.py              # Bot & Dispatcher initialization
│   ├── config.py           # Configuration (env vars)
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── user.py         # User command handlers
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py       # Inline keyboard builders
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── throttling.py   # Rate limiting
│   └── filters/
│       ├── __init__.py
│       └── is_admin.py     # Admin filter
├── main.py                 # Entry point
├── pyproject.toml          # Dependencies
├── .env                    # Environment variables (not committed)
├── .env.example            # Example env file
└── .gitignore
```

## Requirements

- Python 3.10+
- aiogram 3.x
- python-dotenv
- pydantic-settings

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/hanifmmufid/telegram-bot.git
cd telegram-bot
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# or
pip install aiogram python-dotenv pydantic-settings
```

### 4. Setup environment

```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN from @BotFather
```

### 5. Get your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow instructions to create a bot
4. Copy the token and paste it in `.env`

```env
BOT_TOKEN=123456789:ABCDefGhIJKlmNoPQRsTUVwxYZ1234567890
```

## Usage

### Run locally

```bash
python main.py
```

### Run with PM2 (production)

```bash
pm2 start .venv/bin/python --name telegaiogrambot -- main.py
```

### PM2 Commands

```bash
pm2 status telegaiogrambot       # Check status
pm2 logs telegaiogrambot         # View logs
pm2 restart telegaiogrambot     # Restart
pm2 stop telegaiogrambot         # Stop
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help |
| *(any)* | Echo the message |

## Development

### Add new handler

Create a new file in `app/handlers/`:

```python
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/custom")
async def custom_command(message: Message):
    await message.answer("Custom command!")
```

Register in `main.py`:

```python
from app.handlers.user import router as user_router
from app.handlers.custom import router as custom_router

def register_routers():
    dp.include_routers(user_router, custom_router)
```

### Add inline keyboard

```python
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.button(text="Click me", callback_data="click")
builder.adjust(1)
await message.answer("Text", reply_markup=builder.as_markup())
```

## Deploy

### Systemd Service

Create `/etc/systemd/system/telegaiogrambot.service`:

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/telegram-bot
ExecStart=/path/to/telegram-bot/.venv/bin/python main.py
Restart=on failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegaiogrambot
sudo systemctl start telegaiogrambot
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "main.py"]
```

## Resources

- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Aiogram 3 Guide](https://github.com/mastergroosha/aiogram-3-guide)

## License

MIT