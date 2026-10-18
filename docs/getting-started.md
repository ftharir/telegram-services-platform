# Getting started

## Requirements

* Python 3.12 or newer
* Docker (for PostgreSQL 16 and Redis 7)
* A Telegram bot token from [@BotFather](https://t.me/BotFather)
* *(optional)* a RapidSeen API key for real order submission

## 1 · Install

```bash
git clone https://github.com/ftharir/telegram-services-platform.git
cd telegram-services-platform
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2 · Configure

```bash
cp .env.example .env               # Windows: copy .env.example .env
```

Fill in `.env`. **Never commit this file** — it is in `.gitignore`.

| Variable | Meaning | Default / example |
|---|---|---|
| `BOT_TOKEN` | token from BotFather (required) | — |
| `REQUIRED_CHANNELS`, `REQUIRED_CHANNEL_IDS` | channel(s) a user must join (comma separated) | empty |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | database credentials | `postgres`, —, `telegram_platform_db` |
| `POSTGRES_HOST`, `POSTGRES_PORT` | database address | `127.0.0.1`, `5434` |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_DB` | Redis connection | `127.0.0.1`, `6379`, empty, `0` |
| `API_HOST`, `API_PORT` | web server | `0.0.0.0`, `8000` |
| `RAPIDSEEN_API_KEY`, `RAPIDSEEN_API_URL` | RapidSeen SMM API v2 | empty, `https://rapidseen.com/api/v2` |

`docker-compose.yml` ships with a **development-only** database password. Change it (and the matching `POSTGRES_PASSWORD` in `.env`) before using the stack anywhere other than your own machine.

## 3 · Start the services and create the tables

```bash
docker compose up -d               # PostgreSQL on 5434, Redis on 6379
alembic upgrade head               # users, wallets, wallet_transactions, orders
```

## 4 · Run

```bash
python -m app.run                  # bot (long polling) + web server together
```

The web server answers on `http://localhost:8000`:

| URL | Purpose |
|---|---|
| `/` | status message |
| `/health`, `/health/liveness` | liveness |
| `/health/readiness` | readiness (checks the database and Redis) |
| `/docs`, `/redoc` | interactive API documentation |

## Tests

```bash
python test_phase2_suite.py        # mock-based Phase 2 suite, no database needed
pytest                             # tests/ — three of them need the PostgreSQL container running
```

See [`known-issues-and-roadmap.md`](known-issues-and-roadmap.md) for the current state of the test suite.

## Network note

`app/main.py` creates the bot session with a local SOCKS5 proxy (`socks5://127.0.0.1:10808`, the author's VPN). If you do not use a proxy on that address, the bot cannot reach Telegram; see the known issues.
