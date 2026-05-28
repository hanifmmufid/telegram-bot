# Plan: Telegram Bot dengan Aiogram 3.x

## Overview
- **Framework**: Aiogram 3.x (asynchronous, Python 3.10+)
- **Arsitektur**: Modular dengan Router per feature
- **Struktur**: Python package project

---

## 1. Setup Project

### Install Dependencies
```bash
cd /home/ubuntu/MYFILE/upwork/bot-telegram

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install aiogram
pip install aiogram[fastapi]  # dengan fastapi untuk webhooks
# atau
pip install "aiogram~=3.0"    # versi stabil
```

### Pyproject.toml (modern approach dengan uv)
```toml
[project]
name = "telegram-bot"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "aiogram>=3.0",
    "python-dotenv>=1.0.0",
]

[tool.uv]
dev-dependencies = [
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]
```

---

## 2. Struktur Project

```
bot-telegram/
├── app/
│   ├── __init__.py
│   ├── config.py          # Konfigurasi (BOT_TOKEN, etc)
│   ├── bot.py             # Inisialisasi Bot & Dispatcher
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── user.py        # Handler untuk user commands
│   │   └── admin.py       # Handler untuk admin commands
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py      # Inline keyboard builders
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── throttling.py  # Rate limiting middleware
│   └── filters/
│       ├── __init__.py
│       └── is_admin.py    # Custom filter untuk admin check
├── .env                   # Environment variables
├── .env.example
├── pyproject.toml
└── main.py                # Entry point
```

---

## 3. Komponen Inti

### 3.1 Konfigurasi (.env & config.py)
```python
# .env
BOT_TOKEN=123456789:ABCDefGhIJKlmNoPQRsTUVwxYZ1234567890

# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    BOT_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 3.2 Bot Initialization (bot.py)
```python
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import get_settings

settings = get_settings()

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
```

### 3.3 Router & Handler Pattern

```python
# handlers/user.py
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Halo! Saya bot Anda.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Daftar command:\n/start - Mulai\n/help - Bantuan")
```

### 3.4 Inline Keyboard

```python
# keyboards/inline.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class MenuCallback(CallbackData, prefix="menu"):
    action: str  # "show", "back", "exit"
    page: int = 0

def get_main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Menu", callback_data=MenuCallback(action="show", page=1))
    builder.button(text="⚙️ Settings", callback_data=MenuCallback(action="settings"))
    builder.button(text="❌ Exit", callback_data=MenuCallback(action="exit"))
    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup()
```

### 3.5 Callback Query Handler

```python
# handlers/callbacks.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import MenuCallback

router = Router()

@router.callback_query(MenuCallback.filter(F.action == "show"))
async def show_menu(callback: CallbackQuery, callback_data: MenuCallback):
    await callback.answer()
    await callback.message.edit_text(
        "Menu:",
        reply_markup=get_main_menu_kb()
    )
```

### 3.6 FSM (Finite State Machine) - untuk conversation flow

```python
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class OrderForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

@router.message(StateFilter(None), Command("order"))
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderForm.waiting_for_name)
    await message.answer("Siapa nama Anda?")

@router.message(OrderForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.waiting_for_phone)
    await message.answer("Nomor telepon?")

@router.message(OrderForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderForm.waiting_for_address)
    await message.answer("Alamat pengiriman?")

@router.message(OrderForm.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Order diterima untuk {data['name']}")
```

---

## 4. Entry Point (main.py)

```python
import asyncio
import logging
from aiogram import executor
from bot import bot, dp
from handlers import user, admin, callbacks
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routers():
    dp.include_routers(
        user.router,
        admin.router,
        callbacks.router,
    )

def main():
    register_routers()
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Fitur-fitur Umum

### 5.1 Throttling / Rate Limiting
```python
# middlewares/throttling.py
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import current_handler
from aiogram.types import Message
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=0.5):
        self.rate_limit = rate_limit
        self.throttled = {}

    async def on_pre_process_message(self, message: Message, data: dict):
        handler = current_handler.get()
        if not handler:
            return

        key = f"{handler.__name__}:{message.from_user.id}"
        now = time.time()

        if key in self.throttled:
            last = self.throttled[key]
            if now - last < self.rate_limit:
                await message.answer("⏳ Tolong tunggu sebentar...")
                raise CancelHandler()

        self.throttled[key] = now
```

### 5.2 Admin Filter
```python
# filters/is_admin.py
from aiogram.dispatcher.filters import BoundFilter
from config import get_settings

ADMIN_IDS = [12345678, 87654321]  # dari config/database

class IsAdminFilter(BoundFilter):
    key = "is_admin"

    async def check(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS
```

---

## 6. Deployment

### 6.1 Systemd Service (Linux)
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MYFILE/upwork/bot-telegram
ExecStart=/home/ubuntu/MYFILE/upwork/bot-telegram/.venv/bin/python main.py
Restart=on failure

[Install]
WantedBy=multi-user.target
```

### 6.2 Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "main.py"]
```

---

## 7. Testing

```bash
# Install pytest
pip install pytest pytest-asyncio

# Contoh test
# tests/test_handlers.py
import pytest
from aiogram.types import Message
from aiogram.filters import CommandStart

@pytest.mark.asyncio
async def test_start_command():
    # test handler responses
    pass
```

---

## 8. Checklist Implementasi

| Step | Task | Status |
|------|------|--------|
| 1 | Setup project structure | [ ] |
| 2 | Install dependencies | [ ] |
| 3 | Buat config.py & .env | [ ] |
| 4 | Buat bot.py (inisialisasi) | [ ] |
| 5 | Buat router untuk handlers | [ ] |
| 6 | Implementasi inline keyboards | [ ] |
| 7 | Implementasi FSM untuk conversation | [ ] |
| 8 | Tambah middleware (throttling) | [ ] |
| 9 | Setup logging | [ ] |
| 10 | Buat systemd service | [ ] |
| 11 | Testing & deployment | [ ] |

---

## Referensi
- Aiogram Docs: https://docs.aiogram.dev/
- Aiogram 3 Guide: https://github.com/mastergroosha/aiogram-3-guide
- Telegram Bot API: https://core.telegram.org/bots/api