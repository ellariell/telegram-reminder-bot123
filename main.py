import telebot
import json
import os
import threading
import time
import re
import logging
from datetime import datetime, timedelta
from telebot import types

# ============ Настройки ============
TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
OWNER_ID = 1130771677
REMINDER_FILE = "reminders.json"

bot = telebot.TeleBot(TOKEN)

# 🛠️ Удаляем вебхук, чтобы не было конфликта с polling
bot.remove_webhook()


# ============ Сохранение / Загрузка ============
def load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_reminders():
    with open(REMINDER_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

# ============ Распознавание фраз "через 10 минут" ============
def parse_relative_time(text):
    text = text.lower()
    now = datetime.now()

    if "через полчаса" in text:
        return now + timedelta(minutes=30)

    m3 = re.search(r"через\s+(\d+)\s+час(?:а|ов)?\s+(\d+)\s+мин", text)
    m2 = re.search(r"через\s+(\d+)\s+час", text)
    m1 = re.search(r"через\s+(\d+)\s+мин", text)

    if m3:
        h, m = int(m3.group(1)), int(m3.group(2))
        return now + timedelta(hours=h, minutes=m)
    elif m2:
        return now + timedelta(hours=int(m2.group(1)))
    elif m1:
        return now + timedelta(minutes=int(m1.group(1)))

    return None

# ============ Разбор текста ============
def parse_repeat(text):
    text = text.lower()
    if "каждый день" in text or "ежедневно" in text:
        return "daily"
    if "будни" in text or "по будням" in text:
        return "weekdays"
    days_map = {
        "пн": "mo", "вт": "tu", "ср": "we",
        "чт": "th", "пт": "fr", "сб": "sa", "вс": "su"
    }
    picks = [days_map[d] for d in days_map if re.search(rf"\b{d}\b", text)]
    return picks if picks else None

def parse_reminder(text):
    relative = parse_relative_time(text)
    if relative:
        # Удаляем "напомни" и "через X минут/часов", остальное — сообщение
        msg_match = re.search(r"через\s+\d+\s+\w+\s+(.*)", text)
        msg = msg_match.group(1).strip() if msg_match else ""
        return {"time": relative.isoformat(), "message": msg, "repeat": None}

    # Абсолютное время
    m = re.search(r"в\s+(\d{1,2}[:\-]\d{2})\s+(.+)", text)
    if not m:
        return None
    time_part, msg = m.groups()
    hour, minute = map(int, time_part.replace("-", ":").split(":"))
    now = datetime.now()
    dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if dt <= now:
        dt += timedelta(days=1)
    repeat = parse_repeat(text)
    return {"time": dt.isoformat(), "message": msg.strip(), "repeat": repeat}

# ============ Расчёт следующей даты ============
def get_next_repeat_time(current_str, repeat):
    cur = datetime.fromisoformat(current_str)
    if repeat == "daily":
        return cur + timedelta(days=1)
    if repeat == "weekdays":
        nxt = cur + timedelta(days=1)
        while nxt.weekday() > 4:
            nxt += timedelta(days=1)
        return nxt
    if isinstance(repeat, list):
        dow = cur.weekday()
        names = ["mo", "tu", "we", "th", "fr", "sa", "su"]
        days_ahead = [(names.index(d) - dow) % 7 or 7 for d in repeat]
        return cur + timedelta(days=min(days_ahead))
    return None

# ============ Напоминалка ============
def reminder_checker():
    while True:
        now = datetime.now()
        for idx, r in enumerate(reminders[:]):
            rt = datetime.fromisoformat(r["time"])

            if rt <= now:
                if r.get("seen"):
                    continue  # ✅ Уже подтверждено

                user_id = r.get("user_id", OWNER_ID)

                # Кнопки: напомнить позже / подтвердить
                kb = types.InlineKeyboardMarkup()
                kb.add(
                    types.InlineKeyboardButton("🔁 Напомнить позже", callback_data=f"later|{idx}"),
                    types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm|{idx}")
                )
                bot.send_message(
                    user_id,
                    f"🔔 Напоминание: {r['message']}",
                    reply_markup=kb,
                    disable_notification=False  # 🔊 включаем звук уведомления
                )

                # 🔁 Повторяющееся — переносим на следующее время
                if r.get("repeat"):
                    nxt = get_next_repeat_time(r["time"], r["repeat"])
                    if nxt:
                        r["time"] = nxt.isoformat()
                    else:
                        reminders.remove(r)
                else:
                    # Одноразовое: если не подтвердит — вернёмся через 2 мин
                    r["time"] = (now + timedelta(minutes=2)).isoformat()

                save_reminders()
        time.sleep(30)


# ============ Команды ============
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "🤖 *Приветствую, великий повелитель напоминаний!*\n\n"
        "Я твой личный секретарь, хранитель дедлайнов и защитник от забывчивости.\n\n"
        "📌 Примеры:\n"
        "`напомни каждый день в 09:00 выпить кофе ☕️`\n"
        "`напомни через 15 минут позвонить бабушке ❤️`\n\n"
        "💡 Я понимаю такие штуки:\n"
        "- `каждый день`, `по будням`\n"
        "- `пн`, `вт`, `ср`, `чт`, `пт`, `сб`, `вс`\n"
        "- `через 10 минут`, `через 1 час`, `через полчаса`\n\n"
        "_Надо лишь сказать, и я напомню!_",
        parse_mode="Markdown"
    )
    show_menu(message)

@bot.message_handler(commands=["меню", "menu"])
def show_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📋 Список", "🔔 Все Напоминания")
    markup.row("❌ Удалить", "➕ Добавить")
    
    if message.chat.id == OWNER_ID:
        markup.row("🧠 Информация")

    bot.send_message(
        message.chat.id,
        "📲 *Чего изволите, мой повелитель?*\nВыбирайте, не стесняйтесь 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, "📲 Выберите:", reply_markup=markup)


INFO_LABEL = "🧠 Информация"

@bot.message_handler(func=lambda m: m.text in [
    "📋 Список", "🔔 Все Напоминания", "❌ Удалить", "➕ Добавить", INFO_LABEL
])
def handle_menu(message):
    if message.text == "📋 Список":
        list_active(message)
    elif message.text == "🔔 Все Напоминания":
        list_all(message)
    elif message.text == "❌ Удалить":
        show_delete_menu(message)
    elif message.text == "➕ Добавить":
        bot.send_message(message.chat.id, "✍️ Напиши: напомни завтра в 14:00 позвонить маме")
    elif message.text == INFO_LABEL and message.chat.id == OWNER_ID:
        list_users(message)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("напомни"))
def handle_reminder(message):
    r = parse_reminder(message.text.lower())
    if not r:
        bot.send_message(
            message.chat.id,
            "⚠️ Я не совсем понял, что ты хочешь...\n"
            "_Попробуй так:_ `напомни через 10 минут сделать 37-й глоток воды 💧`",
            parse_mode="Markdown"
        )
        return

    r["message"] = r["message"].strip() or "Без текста"
    r["user_id"] = message.chat.id
    r["user_name"] = message.from_user.first_name
    r["seen"] = False

    reminders.append(r)
    save_reminders()

    rt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
    rep = f", 🔁 повтор: *{r['repeat']}*" if r["repeat"] else ""

    bot.send_message(
        message.chat.id,
        f"📝 Записал в свой древний свиток!\n\n"
        f"📅 *Когда:* {rt}{rep}\n"
        f"📌 *Что:* {r['message']}",
        parse_mode="Markdown"
    )

# ============ Списки ============
def list_active(message):
    now = datetime.now()
    user_id = message.chat.id

    active = [
        r for r in reminders
        if r.get("user_id") == user_id and
           not r.get("repeat") and
           not r.get("seen") and
           datetime.fromisoformat(r["time"]) > now
    ]

    if active:
        txt = "📚 *Твои ожидающие напоминания:*\n\n"
        for i, r in enumerate(active, 1):
            dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
            txt += f"*{i}.* 🗓 {dt}\n🔔 {r['message']}\n\n"
        bot.send_message(user_id, txt, parse_mode="Markdown")
    else:
        bot.send_message(
            user_id,
            "🧘‍♂️ Покой и тишина... У тебя нет ни одного активного напоминания.\n"
            "_Может, самое время придумать себе план на вечер? 🍷_",
            parse_mode="Markdown"
        )



def list_all(message):
    now = datetime.now()
    user_id = message.chat.id
    upcoming = []
    confirmed = []

    for r in reminders:
        if r.get("user_id") != user_id or r.get("repeat"):
            continue
        rt = datetime.fromisoformat(r["time"])
        if r.get("seen"):
            confirmed.append(r)
        elif rt >= now:
            upcoming.append(r)
        else:
            confirmed.append(r)

    reply = ""

    if upcoming:
        reply += "🕰 *Те, кто ждут своего часа:*\n\n"
        for i, r in enumerate(upcoming, 1):
            dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
            time_str = f"📅 {dt} 🕓"
            reply += f"*{i}.* 🔔 {r['message']}\n⏳ {time_str}\n\n"

    if confirmed:
        reply += "\n✅ *То, что ты уже подтвердил:* (или забыл, но я не обижен)\n\n"
        for i, r in enumerate(confirmed, 1):
            dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
            time_str = f"📅 {dt} 🕓"
            reply += f"*{i}.* 🧾 {r['message']}\n📌 {time_str}\n\n"

    if not reply:
        reply = "🦗 Ни одной напоминалки. Тишина... Но это, кстати, подозрительно 🤨"

    bot.send_message(user_id, reply, parse_mode="Markdown")




def list_all(message):
    now = datetime.now()
    user_id = message.chat.id
    upcoming = []
    confirmed = []

    for r in reminders:
        if r.get("user_id") != user_id or r.get("repeat"):
            continue
        rt = datetime.fromisoformat(r["time"])
        if r.get("seen"):
            confirmed.append(r)
        elif rt >= now:
            upcoming.append(r)
        else:
            confirmed.append(r)

    reply = ""

    if upcoming:
        reply += "🕰 *Те, кто ждут своего часа:*\n\n"
        for i, r in enumerate(upcoming, 1):
            dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
            time_str = f"📅 {dt} 🕓"
            reply += f"*{i}.* 🔔 {r['message']}\n⏳ {time_str}\n\n"

    if confirmed:
        reply += "\n✅ *То, что ты уже подтвердил:* (или забыл, но я не обижен)\n\n"
        for i, r in enumerate(confirmed, 1):
            dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
            time_str = f"📅 {dt} 🕓"
            reply += f"*{i}.* 🧾 {r['message']}\n📌 {time_str}\n\n"

    if not reply:
        reply = "🦗 Ни одной напоминалки. Тишина... Но это, кстати, подозрительно 🤨"

    bot.send_message(user_id, reply, parse_mode="Markdown")

# ============ Удаление ============
from telebot import types
from datetime import datetime

marked_for_deletion = {}  # user_id -> set of reminder ids

def show_delete_menu(message):
    user_id = message.chat.id
    marked_for_deletion[user_id] = set()  # обнуляем выделенные
    markup = generate_delete_keyboard(user_id, marked_for_deletion[user_id])

    bot.send_message(
        user_id,
        "🧹 *Выбери, что удалить:*\n_Можно выбирать несколько!_\n\nНажми на напоминания, которые хочешь стереть.\nКогда закончишь — нажми «🗑 Удалить выбранные».",
        reply_markup=markup,
        parse_mode="Markdown"
    )

def generate_delete_keyboard(user_id, marked_ids):
    markup = types.InlineKeyboardMarkup()
    user_reminders = [r for r in reminders if r.get("user_id") == user_id]

    for i, r in enumerate(user_reminders):
        r_id = str(id(r))
        dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
        short_msg = r["message"][:30] + ("..." if len(r["message"]) > 30 else "")
        checked = "✅ " if r_id in marked_ids else "🔘 "
        markup.add(types.InlineKeyboardButton(
            f"{checked}{dt} — {short_msg}",
            callback_data=f"markdel|{r_id}"
        ))

    if marked_ids:
        markup.add(types.InlineKeyboardButton("🗑 Удалить выбранные", callback_data="del_selected"))

    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_del"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("markdel|"))
def mark_reminder_for_deletion(call):
    user_id = call.message.chat.id
    r_id = call.data.split("|")[1]

    if user_id not in marked_for_deletion:
        marked_for_deletion[user_id] = set()

    if r_id in marked_for_deletion[user_id]:
        marked_for_deletion[user_id].remove(r_id)
    else:
        marked_for_deletion[user_id].add(r_id)

    # Обновляем клавиатуру
    markup = generate_delete_keyboard(user_id, marked_for_deletion[user_id])
    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "del_selected")
def delete_selected_reminders(call):
    user_id = call.message.chat.id
    to_delete = marked_for_deletion.get(user_id, set())
    before = len(reminders)

    reminders[:] = [r for r in reminders if str(id(r)) not in to_delete]
    after = len(reminders)
    deleted_count = before - after

    marked_for_deletion[user_id] = set()

    bot.edit_message_text(
        f"🗑 Удалено {deleted_count} напоминание(й).",
        chat_id=user_id,
        message_id=call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data == "cancel_del")
def cancel_deletion(call):
    user_id = call.message.chat.id
    marked_for_deletion[user_id] = set()
    bot.edit_message_text("❌ Удаление отменено.", chat_id=user_id, message_id=call.message.message_id)
@bot.callback_query_handler(func=lambda call: call.data.startswith("del|"))
def handle_delete_callback(call):
    parts = call.data.split("|")
    key = parts[1]
    user_id = int(parts[2])

    if call.message.chat.id != user_id:
        bot.answer_callback_query(call.id, "🙅‍♂️ Ты лезешь не в свои напоминания!")
        return

    user_reminders = [r for r in reminders if r.get("user_id") == user_id]

    if key == "all":
        count = len(user_reminders)
        for r in user_reminders:
            reminders.remove(r)
        save_reminders()
        bot.edit_message_text(
            f"🧨 *Уничтожено всё!* ({count} напоминаний отправились в мир иной 🪦)",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        return

    try:
        idx = int(key)
        if 0 <= idx < len(user_reminders):
            r = user_reminders[idx]
            reminders.remove(r)
            save_reminders()
            dt = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
            bot.edit_message_text(
                f"🗑 *Удалено:*\n_{dt}_ — {r['message']}\n\nПрощай, дорогая напоминалочка... 😢",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.answer_callback_query(call.id, "❌ Напоминание не найдено. Оно уже может быть удалено... или просто призрак 👻")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Что-то пошло не так при удалении.")
        print(f"Ошибка при удалении через del|: {e}")
@bot.callback_query_handler(func=lambda call: call.data == "del_selected")
def delete_selected(call):
    user_id = call.from_user.id
    marked = marked_for_deletion.get(user_id, set())

    if not marked:
        bot.answer_callback_query(call.id, "❌ Ничего не выбрано.")
        return

    # Сколько всего напоминаний до удаления
    before = len(reminders)

    # Удаление помеченных напоминаний (по id в виде строки)
    reminders[:] = [r for r in reminders if str(id(r)) not in marked]

    # Сколько осталось после
    after = len(reminders)

    # Сохраняем
    save_reminders()

    # Очищаем помеченные
    marked_for_deletion[user_id] = set()

    # Отправляем весёлое сообщение об удалении
    bot.edit_message_text(
        f"🧹 Удалено {before - after} напоминаний. "
        f"Покойтесь с миром, забытые дела... ⚰️",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

# ============ Запуск ============
# ============ Команда /у_кого — список пользователей ============

@bot.message_handler(commands=["у_кого"])
def list_users(message):
    if message.chat.id != OWNER_ID:
        return

    user_ids = sorted(set(r["user_id"] for r in reminders if "user_id" in r))
    markup = types.InlineKeyboardMarkup()
    for uid in user_ids:
        name = next((r.get("user_name", f"ID {uid}") for r in reminders if r.get("user_id") == uid), f"ID {uid}")
        markup.add(types.InlineKeyboardButton(f"{name}", callback_data=f"userlist|{uid}"))

    if not user_ids:
        bot.send_message(
            message.chat.id,
            "📭 Напоминаний ни у кого нет.",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            message.chat.id,
            "👥 У кого есть напоминания:",
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("userlist|"))
def handle_user_list(call):
    uid = int(call.data.split("|")[1])
    user_reminders = [r for r in reminders if r.get("user_id") == uid]

    if not user_reminders:
        bot.answer_callback_query(call.id, "❌ Напоминаний нет.")
        return

    name = user_reminders[0].get("user_name", f"ID {uid}")
    reply = f"📋 Напоминания пользователя {name}:\n\n"

    for i, r in enumerate(user_reminders, 1):
        time_str = datetime.fromisoformat(r["time"]).strftime("%d.%m.%Y %H:%M")
        status = "✅ подтверждено" if r.get("seen") else "⏳ ожидает"
        reply += f"{i}. 🕒 {time_str} — {r['message']} ({status})\n"

    bot.send_message(call.message.chat.id, reply)

@bot.callback_query_handler(func=lambda call: call.data.startswith("later|"))
def handle_later(call):
    idx = int(call.data.split("|")[1])
    if 0 <= idx < len(reminders):
        r = reminders[idx]
        if call.message.chat.id != r.get("user_id"):
            bot.answer_callback_query(call.id, "🙅‍♂️ Это не твоё напоминание, шифруйся!")
            return

        # Обновляем время текущего напоминания (через 2 минуты)
        new_dt = datetime.now() + timedelta(minutes=2)
        r["time"] = new_dt.isoformat()

        save_reminders()
        bot.answer_callback_query(
            call.id,
            "⏰ Отложено! Вернусь через 2 минуты — с кофе, пледом и твоим делом 🧣☕"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Напоминание не найдено. Оно что, ушло в отпуск?")


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm|"))
def handle_confirm(call):
    idx = int(call.data.split("|")[1])
    if 0 <= idx < len(reminders):
        r = reminders[idx]
        if call.message.chat.id != r.get("user_id"):
            bot.answer_callback_query(call.id, "❌ Это не ваше напоминание.")
            return

        reminders[idx]["seen"] = True
        save_reminders()
        bot.edit_message_text(
            "✅ Напоминание подтверждено",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ Напоминание не найдено.")

reminders = load_reminders()
delete_sessions = {}

# Проверим и дополним user_id и user_name
for r in reminders:
    if "user_id" not in r:
        r["user_id"] = OWNER_ID
    if "user_name" not in r:
        try:
            chat = bot.get_chat(r["user_id"])
            r["user_name"] = chat.first_name
        except:
            r["user_name"] = f"ID {r['user_id']}"
@bot.message_handler(commands=["обнови_имена"])
def update_names(message):
    if message.chat.id != OWNER_ID:
        return

    updated = 0
    for r in reminders:
        if not r.get("user_name"):
            try:
                chat = bot.get_chat(r["user_id"])
                r["user_name"] = chat.first_name
                updated += 1
            except:
                continue
    save_reminders()
    bot.send_message(OWNER_ID, f"🔄 Обновлено имён: {updated}")


threading.Thread(target=reminder_checker, daemon=True).start()
print("✅ Бот запущен.")
bot.infinity_polling()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
