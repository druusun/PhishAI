
class ScamBaiter:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler

    def generate_reply(self, scam_message: str, chat_history=None) -> str:
        return self.llm_handler.generate_response(scam_message, chat_history) 