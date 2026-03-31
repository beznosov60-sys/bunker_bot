# Bunker Telegram Mini App

Новый проект создан с нуля в каталоге `project/`.

## Структура
- `project/backend` — FastAPI + aiogram + SQLite + SQLAlchemy
- `project/frontend` — React + Vite + Tailwind + Zustand

## Быстрый старт backend
```bash
cd project/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Основные API
- `POST /game/create`
- `POST /game/join`
- `POST /game/start`
- `GET /player/cards`
- `POST /player/reveal`
- `POST /game/vote`
- `GET /game/state`
- `GET /game/result`
- `GET /game/survival`

## Telegram Bot
```bash
cd project/backend
export BOT_TOKEN=<token>
python -m app.bot.main
```

## Данные
- `project/backend/app/data/cards.json` — 175 реалистичных карточек по 7 категориям.
- `project/backend/app/data/scenarios.json` — 100 сценариев катастроф.
