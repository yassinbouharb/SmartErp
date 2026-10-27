from dataclasses import dataclass, field


@dataclass
class ConversationContext:

    history: list = field(default_factory=list)

    catalogue: dict = field(default_factory=dict)

    current_client: dict | None = None

    current_invoice = None

    current_bl = None

    current_products: list = field(default_factory=list)

    language: str = "fr"

    metadata: dict = field(default_factory=dict)

    def add_user_message(self, message: str):
        self.history.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message):
        self.history.append({
            "role": "assistant",
            "content": str(message)
        })