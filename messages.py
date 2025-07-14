import sqlite3
import os
import time
import json

CACHE_PATH = 'cache.json'
CHAT_DB_PATH = os.path.expanduser('~/Library/Messages/chat.db')

def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {"replied_message_ids": [], "scammer_ids": []}
    try:
        with open(CACHE_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {"replied_message_ids": [], "scammer_ids": []}

def save_cache(cache):
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)


def poll_new_messages(last_checked=None):
    if last_checked is None:
        last_checked = int(time.time()) - 300  
    db_path = CHAT_DB_PATH
    messages = []
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message.guid, message.text, handle.id, message.date, chat.chat_identifier
            FROM message
            JOIN chat_message_join ON chat_message_join.message_id = message.ROWID
            JOIN chat ON chat.ROWID = chat_message_join.chat_id
            JOIN handle ON message.handle_id = handle.ROWID
            WHERE message.is_from_me = 0
            AND message.date > ?
            ORDER BY message.date ASC
        ''', (last_checked,))
        for guid, text, sender, date, chat_id in cursor.fetchall():
            if not text or not isinstance(text, str) or text.strip() == "":
                continue
            #Apple time
            if date > 1000000000:
                unix_time = int(date / 1000000000) + 978307200
            else:
                unix_time = date
            messages.append({
                "guid": guid,
                "text": text,
                "sender": sender,
                "date": unix_time,
                "chat_id": chat_id
            })
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return messages

def mark_message_replied(message_id):
    if not message_id or not isinstance(message_id, str) or not message_id.strip():
        return
    cache = load_cache()
    if message_id not in cache["replied_message_ids"]:
        cache["replied_message_ids"].append(message_id)
        save_cache(cache)


def is_message_replied(message_id):
    cache = load_cache()
    return message_id in cache["replied_message_ids"]

    
def add_scammer(sender_id):
    if not sender_id or not isinstance(sender_id, str) or not sender_id.strip():
        return
    cache = load_cache()
    if sender_id not in cache["scammer_ids"]:
        cache["scammer_ids"].append(sender_id)
        save_cache(cache)

def is_scammer(sender_id):
    cache = load_cache()
    return sender_id in cache["scammer_ids"]

def get_chat_history(chat_id, limit=3):
    db_path = CHAT_DB_PATH
    history = []
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message.text, message.is_from_me
            FROM message
            JOIN chat_message_join ON chat_message_join.message_id = message.ROWID
            JOIN chat ON chat.ROWID = chat_message_join.chat_id
            WHERE chat.chat_identifier = ?
            ORDER BY message.date DESC
            LIMIT ?
        ''', (chat_id, limit))
        rows = cursor.fetchall()
        for text, is_from_me in reversed(rows):
            if not text or not isinstance(text, str) or text.strip() == "":
                continue
            role = "assistant" if is_from_me == 1 else "user"
            history.append({"role": role, "content": text.strip()})
    except sqlite3.Error as e:
        print(f"Database error in get_chat_history: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return history