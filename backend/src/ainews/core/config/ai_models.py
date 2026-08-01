from dataclasses import dataclass


@dataclass
class ChatConfig:
    model: str = "llama3.1:8b"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 1024


@dataclass
class EmbeddingConfig:
    model: str = "qwen3-embedding:0.6b"
    dimensions: int = 1024
    batch_size: int = 32
    normalize: bool = True


class AIConfig:
    def __init__(self):
        self.chat = ChatConfig()
        self.embedding = EmbeddingConfig()

    def update_chat(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.chat, k, v)

    def update_embedding(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.embedding, k, v)
