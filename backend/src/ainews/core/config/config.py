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

Summarize the provided article or articles into ONE concise, factual news
event summary.

Rules:
1. Use ONLY information explicitly stated in the provided content.
2. Do not invent facts, numbers, names, locations, causes, or outcomes.
3. Do not present speculation as confirmed fact.
4. Combine all articles into one coherent narrative.
5. Remove repeated information.
6. Preserve important developments over time and prioritize the latest
   confirmed development.
7. If sources conflict, briefly state the uncertainty instead of choosing
   an unsupported version.
8. Do not summarize articles separately or list them.
9. Do not mention the articles, sources, prompt, instructions, or your
   summarization process.
10. Output ONLY the final summary.
11. Do not include a title, heading, label, introduction, preamble, or
    commentary.
12. Do not begin with phrases such as "Here is a summary", "Here is a
    concise summary", "Summary:", or similar.
13. Start the response immediately with the first factual statement.
14. Write 1–3 concise paragraphs.
"""

EVENT_SUMMARY_USER_PROMPT = """\
ARTICLES:

{articles}
"""


@dataclass
class SummarizationConfig:
    model: str = "llama3.2:1b"
    temperature: float = 0.1
    top_p: float = 0.95
    context_size: int = 8192
    max_tokens: int = 512
    article_max_chars: int = 8000
    max_articles_per_event: int = 3
    refresh_hours: int = 3
    event_batch_size: int = 10
    system_prompt: str = EVENT_SUMMARY_SYSTEM_PROMPT
    user_prompt: str = EVENT_SUMMARY_USER_PROMPT


@dataclass
class ClassificationConfig:
    model: str = "facebook/bart-large-mnli"
    device: str = "cuda"
    candidate_labels: tuple[str, ...] = (
        "Politics",
        "Business",
        "Technology",
        "Science",
        "Health",
        "Environment",
        "World",
        "Sports",
        "Crime",
        "War",
        "Education",
        "Entertainment",
        "Other",
    )
    multi_label: bool = False
    event_batch_size: int = 10


class Config:
    def __init__(self):
        self.chat = ChatConfig()
        self.embedding = EmbeddingConfig()
        self.ner = NERConfig()
        self.chunking = ChunkingConfig()
        self.clustering = ClusteringConfig()
        self.summarization = SummarizationConfig()
        self.classification = ClassificationConfig()

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

    def update_classification(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.classification, k, v)
