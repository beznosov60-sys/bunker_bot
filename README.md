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

## Как получить URL для подключения Mini App в Telegram
Telegram Mini App открывается только по публичному `https` URL.  
Если фронтенд запущен локально (`http://localhost:5173`), нужно выдать его наружу через туннель.

### 1) Запусти frontend
```bash
cd project/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### 2) Подними публичный URL (например, через ngrok)
```bash
ngrok http 5173
```
ngrok покажет адрес вида:
`https://abcd-1234.ngrok-free.app`

### 3) Подставь URL в бота
Сейчас в обработчике `открыть mini app` стоит заглушка:
- `project/backend/app/bot/handlers/game.py` → `https://example.com`

Замени её на адрес из ngrok:
```python
await message.answer("Mini App: https://abcd-1234.ngrok-free.app")
```

### 4) Привяжи Mini App в BotFather (рекомендуется)
В `@BotFather`:
1. `/mybots` → выбери бота  
2. `Bot Settings` → `Menu Button` (или `Configure Mini App`)  
3. Укажи тот же `https` URL

После этого Mini App можно открывать из кнопки меню бота.

## Данные
- `project/backend/app/data/cards.json` — 175 реалистичных карточек по 7 категориям.
- `project/backend/app/data/scenarios.json` — 100 сценариев катастроф.
