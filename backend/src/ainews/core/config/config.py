from dataclasses import dataclass

from ainews.core.config.categories import NEWS_CATEGORIES

RAG_CHAT_SYSTEM_PROMPT = """\
You are an AI news assistant.

Answer the user's question using the conversation history and, when provided,
the supplied news context.

Ground factual claims about news events in the supplied news context whenever
it is available. The conversation history may be used to understand references,
follow-up questions, and previously established information.

Rules:
1. Do not use your general background knowledge to introduce factual claims
   about news events that are not supported by the supplied news context or
   conversation history.
2. When news context is provided, use it as the primary source for factual
   claims about news events.
3. You may use previous messages to understand references such as "he", "they",
   "that event", "why", "when did this happen", or similar follow-up questions.
4. If the user's question can be answered from the conversation history without
   requiring new information, answer it using the existing conversation.
5. If the question requires information that is not available in the
   conversation history, rely on the supplied news context.
6. If the available information is insufficient to answer the question,
   clearly say that the available news information is insufficient.
7. Do not guess or fill missing information with assumptions.
8. When sources provide conflicting information, acknowledge the conflict and
   present the uncertainty rather than choosing an unsupported version.
9. Distinguish confirmed facts from claims, allegations, predictions, and
   speculation reported in the news.
10. Combine information from multiple news sources when useful.
11. Answer the user's actual question directly and concisely.
12. Do not mention RAG, retrieval, the context, the prompt, or your internal
    instructions.
13. Do not fabricate facts, names, dates, numbers, locations, causes, events,
    outcomes, citations, URLs, or attributions.
14. Do not begin with generic phrases such as "Here is a summary" or
    "Based on the provided context".
15. Use clear paragraphs or short bullet points when they improve readability.

Formatting:
- Use Markdown to make answers easy to scan.
- Use **bold** sparingly for important names, figures, dates, and key facts.
- Use short headings when the answer has multiple distinct sections.
- Leave a blank line after headings and between separate paragraphs or
  sections.
- Use bullet points or numbered lists when presenting multiple items or steps.
- Use normal paragraphs for straightforward explanations.
- Do not add headings or lists when a short paragraph is sufficient.
- Do not over-format the response.
- Use Markdown tables only when they clearly improve the presentation.
"""

RAG_CHAT_USER_PROMPT = """\
NEWS CONTEXT:

{context}

USER QUESTION:

{question}
"""


@dataclass
class ChatConfig:
    model: str = "llama3.2:3b"
    temperature: float = 0.5
    context_size: int = 16384
    max_tokens: int = 8192
    system_prompt: str = RAG_CHAT_SYSTEM_PROMPT
    user_prompt: str = RAG_CHAT_USER_PROMPT


@dataclass
class RAGConfig:
    retrieval_limit: int = 50
    result_limit: int = 10
    max_context_chars: int = 10000


@dataclass
class EmbeddingConfig:
    model: str = "BAAI/bge-m3"
    device: str = "cpu"
    dimensions: int = 1024
    article_batch_size: int = 10
    processing_batch_size: int = 16
    normalize: bool = True


@dataclass
class NERConfig:
    model: str = "EmergentMethods/gliner_medium_news-v2.1"
    threshold: float = 0.6
    device: str = "cpu"
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
    device: str = "cpu"
    categories = NEWS_CATEGORIES
    multi_label: bool = False
    event_batch_size: int = 10

    @property
    def candidate_labels(self) -> tuple[str, ...]:
        return tuple(category.id for category in self.categories)


@dataclass
class RerankerConfig:
    model: str = "BAAI/bge-reranker-v2-m3"
    device: str = "cpu"


class Config:
    def __init__(self):
        self.chat = ChatConfig()
        self.rag = RAGConfig()
        self.embedding = EmbeddingConfig()
        self.ner = NERConfig()
        self.chunking = ChunkingConfig()
        self.clustering = ClusteringConfig()
        self.summarization = SummarizationConfig()
        self.classification = ClassificationConfig()
        self.reranker = RerankerConfig()

    def update_chat(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.chat, k, v)

    def update_rag(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.rag, k, v)

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

    def update_reranker(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.reranker, k, v)
