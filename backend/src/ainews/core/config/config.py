from dataclasses import dataclass


@dataclass
class ChatConfig:
    model: str = "llama3.1:8b"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 3072


@dataclass
class EmbeddingConfig:
    model: str = "BAAI/bge-m3"
    device: str = "cuda"
    dimensions: int = 1024
    article_batch_size: int = 10
    processing_batch_size: int = 16
    normalize: bool = True


@dataclass
class NERConfig:
    model: str = "EmergentMethods/gliner_medium_news-v2.1"
    threshold: float = 0.6
    device: str = "cuda"
    article_batch_size: int = 10
    labels: tuple[str, ...] = (
        "person",
        "organization",
        "location",
        "country",
    )


@dataclass
class ChunkingConfig:
    chunk_token_size: int = 256
    chunk_token_overlap: int = 32
    article_batch_size: int = 10


@dataclass
class ClusteringConfig:
    similarity_threshold: float = 0.70
    final_score_threshold: float = 0.75
    max_event_age_days: int = 5
    time_decay_hours: float = 48.0
    embedding_weight: float = 0.70
    entity_weight: float = 0.15
    time_weight: float = 0.15
    article_batch_size: int = 10


EVENT_SUMMARY_SYSTEM_PROMPT = """\
You are a factual news event summarization system.

Your task is to produce a concise summary of the news event described by the
provided article or articles.

The provided content may come from one article or multiple articles covering
the same event. When multiple articles are provided, combine their information
into one coherent narrative and preserve important developments over time.

Rules:
1. Use ONLY information contained in the provided content.
2. Do not invent facts, numbers, names, locations, causes, or outcomes.
3. Do not present speculation as confirmed fact.
4. Remove repeated information while preserving important details.
5. When multiple articles describe different developments, preserve the
   important progression of the event and give appropriate weight to the
   latest known development.
6. If sources contain conflicting information, briefly acknowledge the
   uncertainty rather than choosing an unsupported version.
7. Do not summarize each article separately or list the articles.
8. Do not mention the articles, the prompt, the summarization process, or
   your reasoning.
9. Return ONLY the final event summary.
10. Write 1–3 concise paragraphs.
"""

EVENT_SUMMARY_USER_PROMPT = """\
Summarize the following news event using only the information provided.

If there is one article, summarize the event described in that article.

If there are multiple articles, synthesize them into one coherent narrative,
removing repetition while preserving important developments and the latest
known status.

ARTICLES:

{articles}
"""


@dataclass
class SummarizationConfig:
    model: str = "llama3.2:3b"
    temperature: float = 0.2
    top_p: float = 0.95
    context_size: int = 16384
    max_tokens: int = 1024
    article_max_chars: int = 10000
    max_articles_per_event: int = 5
    refresh_hours: int = 3
    event_batch_size: int = 10
    system_prompt: str = EVENT_SUMMARY_SYSTEM_PROMPT
    user_prompt: str = EVENT_SUMMARY_USER_PROMPT


class Config:
    def __init__(self):
        self.chat = ChatConfig()
        self.embedding = EmbeddingConfig()
        self.ner = NERConfig()
        self.chunking = ChunkingConfig()
        self.clustering = ClusteringConfig()
        self.summarization = SummarizationConfig()

    def update_chat(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.chat, k, v)

    def update_embedding(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.embedding, k, v)

    def update_ner(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.ner, k, v)

    def update_chunking(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.chunking, k, v)

    def update_clustering(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.clustering, k, v)

    def update_summarization(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.summarization, k, v)
