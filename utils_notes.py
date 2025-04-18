from datetime import datetime, timedelta
import json
import re

NOTES_FILE = "user_notes.json"

def parse_note(text: str):
    # Простой парсинг: ищем время и текст
    match = re.search(r"(завтра|сегодня)?\s*в\s*(\d{1,2}[:\.]\d{2})\s*(.+)", text.lower())
    if not match:
        return None
    day_word, time_str, note_text = match.groups()

    now = datetime.now()
    hour, minute = map(int, time_str.replace('.', ':').split(":"))
    target_day = now.date()

    if day_word == "завтра":
        target_day += timedelta(days=1)

    target_datetime = datetime.combine(target_day, datetime.min.time()) + timedelta(hours=hour, minutes=minute)

    return {"time": target_datetime.strftime("%Y-%m-%d %H:%M"), "text": note_text.strip()}

def save_note(user_id: int, note: dict):
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    if str(user_id) not in data:
        data[str(user_id)] = []

    data[str(user_id)].append(note)

    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_due_notes(user_id: int):
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_notes = data.get(str(user_id), [])
    due = [note for note in user_notes if note["time"] == now]
    return due