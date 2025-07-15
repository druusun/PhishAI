**PhishAI** is a lightweight, scam-baiting iMessage bot built for macOS. It detects potential scam messages, keeps track of known scammers, and sends humorous replies to waste their time—all powered by an LLM via the OpenRouter API.

## Features

- Scam Detection: Uses a language model to detect common scam indicators in incoming iMessages.
- Auto Response: Automatically replies to known scammers with creative, believable baiting messages.
- Message Tracking: Maintains a cache to avoid duplicate responses and remembers known scammers.
- macOS Native: Leverages AppleScript to read and send iMessages via the native Messages app.

## Prerequisites

- macOS (required for iMessage + AppleScript support)
- Python 3.7+
- iMessage enabled and active in the Messages app

## Installation

git clone https://github.com/your-username/PhishAI.git

cd PhishAI

pip install -r requirements.txt

Create .env file

OPENROUTER_API_KEY=sk-or-xxxxx... (Need to fill in your own)

python3 main.py

## How It Works
- The bot polls the local iMessage SQLite database every 30 seconds.
- If a new message arrives:
-   It checks if it's already been replied to.
- If the sender is a known scammer, it replies automatically.
- Otherwise, it uses an LLM to detect scam likelihood.
- If a scam is detected, it adds the sender to the cache and responds.
- All data is cached in cache.json.

## Limitations
- macOS only: Due to reliance on AppleScript and the local Messages DB.
- Must remain open: The script must stay running; it won't work if the machine sleeps or is closed.
- LLM limits: Free usage capped (~1000 daily requests) unless using your own OpenRouter key.

