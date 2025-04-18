# Telegram Reminder Bot

Бот с напоминаниями о приёме таблеток, еде, воде, тренировках и сне. Подтверждение выполнения, юмористические сообщения, история в JSON.

## Особенности
- Юмор и разнообразные напоминания
- Кнопка "Меню" всегда внизу
- История выполнения сохраняется в `history.json`
- Полная поддержка aiogram 3.7+ и webhook на Render

## Установка

1. Установи зависимости:

```
pip install -r requirements.txt
```

2. Создай `.env` файл:

```
BOT_TOKEN=твой_токен
USER_ID=твой_telegram_id
RENDER_EXTERNAL_URL=https://твое-приложение.onrender.com
WEBHOOK_SECRET=любой_секрет
```

3. Запуск локально:

```
python main.py
```

4. Для Render:
- Загрузи проект на GitHub
- Добавь переменные окружения: `BOT_TOKEN`, `USER_ID`, `WEBHOOK_SECRET`, `RENDER_EXTERNAL_URL`
- Установи `Start Command`: `python main.py`

## Контакты

Создан специально под кастомное расписание. Не забудь сказать "спасибо" 🤖