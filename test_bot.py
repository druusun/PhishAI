from dotenv import load_dotenv
load_dotenv()

import os
from llm_handler import ScamBotLLM
from scam_detector import ScamDetector
from scam_baiter import ScamBaiter

api_key = os.getenv("OPENROUTER_API_KEY")

llm = ScamBotLLM()
detector = ScamDetector(llm)
baiter = ScamBaiter(llm)

test_messages = [
    "Congratulations! You've won a free cruise. Click the link to claim.",
    "Reminder: Your electricity bill is due next week.",
    "You've won $1000! Claim at http://fake.com"
]

for msg in test_messages:
    print(f"\nMessage: {msg}")
    try:
        is_scam = detector.is_scam(msg)
        print("Is scam?", is_scam)
        if is_scam:
            reply = baiter.generate_reply(msg)
            print("Bot reply:", reply)
    except Exception as e:
        print("Error during LLM call:", e) 