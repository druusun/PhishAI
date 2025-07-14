
class ScamDetector:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler

    def is_scam(self, message: str) -> bool:
        return self.llm_handler.is_scam(message) 