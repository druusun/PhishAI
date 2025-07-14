import time
import subprocess
from dotenv import load_dotenv
from llm_handler import ScamBotLLM
from scam_detector import ScamDetector
from scam_baiter import ScamBaiter
from messages import (
    poll_new_messages, is_message_replied, mark_message_replied,
    is_scammer, add_scammer, get_chat_history
)

load_dotenv()

APPLE_EPOCH_OFFSET = 978307200 
def get_apple_time_now_ns():
    return int((time.time() - APPLE_EPOCH_OFFSET) * 1_000_000_000)

def send_imessage(recipient, message):
    safe_message = message.replace('"', '\\"')

    applescript = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{recipient}" of targetService
        send "{safe_message}" to targetBuddy
    end tell
    '''
    subprocess.run(['osascript', '-e', applescript])

def main():
    llm = ScamBotLLM()
    detector = ScamDetector(llm)
    baiter = ScamBaiter(llm)
    last_checked = get_apple_time_now_ns()
    print("[PhishAI] Scam-baiting bot started. Polling for new messages...")
    while True:
        new_msgs = poll_new_messages(last_checked)
        if new_msgs:
            max_msg_time = max(msg["date"] for msg in new_msgs)
            if max_msg_time > last_checked:
                last_checked = max_msg_time
        for msg in new_msgs:
            if is_message_replied(msg["guid"]):
                continue 
            if not msg["text"]:
                continue 
            print(f"[PhishAI] New message from {msg['sender']}: {msg['text']}")
            chat_history = get_chat_history(msg["chat_id"], limit=3)
            if is_scammer(msg["sender"]):
                print(f"[PhishAI] Known scammer. Auto-replying.")
                reply = baiter.generate_reply(msg["text"], chat_history=chat_history)
                send_imessage(msg["sender"], reply)
                print(f"[PhishAI] Sent reply: {reply}")
            else:
                if detector.is_scam(msg["text"]):
                    print(f"[PhishAI] Scam detected! Adding {msg['sender']} to scammer list.")
                    add_scammer(msg["sender"])
                    reply = baiter.generate_reply(msg["text"], chat_history=chat_history)
                    send_imessage(msg["sender"], reply)
                    print(f"[PhishAI] Sent reply: {reply}")
                else:
                    print(f"[PhishAI] Not a scam. No reply sent.")
            mark_message_replied(msg["guid"])
        time.sleep(10) 

if __name__ == "__main__":
    main()