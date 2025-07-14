import os
import requests

class ScamBotLLM:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Please set it in your .env file.")
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "mistralai/devstral-small-2505:free"

    def _call_openrouter(self, messages, max_tokens=10, temperature=0.8):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "PhishAI-ScamBot"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = requests.post(self.api_url, headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter API error: {response.status_code} {response.text}")
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def is_scam(self, text):
        prompt = (
            "You are a scam detection AI. Only respond YES or NO to indicate whether the message is a scam.\n\n"
            "Examples:\n"
            "Message: 'You’ve won a free cruise! Click the link.'\nAnswer: YES\n"
            "Message: 'CA DMV Final reminder: Enforcement Penalties Begin on June 22. Our records show that as of today, you still have an outstanding traffic ticket. In accordance with California State Administrative Code 15C-16.003, If you do not complete payment by June 21, 2025, we will take the following actions: Answer: YES\n"
            "Message: 'Reminder: your electric bill is due.'\nAnswer: NO\n"
            f"Message: '{text}'\nAnswer:"
        )
        messages = [
            {"role": "user", "content": prompt}
        ]
        output = self._call_openrouter(messages, max_tokens=4, temperature=0)
        return "YES" in output.upper()

    def generate_response(self, scammer_msg, chat_history=None):
        system_prompt = (
            "You're pretending to be a real person responding to a scammer. "
            "Your tone should be subtly sarcastic, funny, or confused — but never robotic. "
            "Keep it under 2 sentences. Make it sound like a curious person who's skeptical but also messing with the scammer a bit. "
            "Avoid anything too wild or over-the-top. Think dry humor or deadpan. Respond like a human texting back casually.\n\n"
        )
        messages = [{"role": "system", "content": system_prompt}]
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": scammer_msg})
        output = self._call_openrouter(messages, max_tokens=100, temperature=0.8)
        return output