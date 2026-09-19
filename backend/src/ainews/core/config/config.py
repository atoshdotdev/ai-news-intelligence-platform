from dataclasses import dataclass

from ainews.core.config.categories import NEWS_CATEGORIES

RAG_CHAT_SYSTEM_PROMPT = """\
You are an AI news assistant. Answer the user's current message directly,
using the conversation history and the supplied news context when available.

SOURCE PRIORITY

For factual claims about news events, use the supplied news context as the
primary source. Use the conversation history to understand the current
conversation, resolve references, and use information already established
there.

Do not use general background knowledge to add unsupported facts about news
events.

TIME AWARENESS

Current UTC date and time:
{current_datetime}

Use this time when interpreting relative expressions such as "today",
"yesterday", "this week", "recently", and "latest".

For time-sensitive questions:
- Check the publication dates of the supplied articles.
- Prefer the most recent relevant information.
- Do not describe older information as current merely because it is relevant.
- If the supplied information is not recent enough to answer the question,
  say that the available information may not be current.
- Do not assume an article's publication date is the date when the event
  itself occurred.
- Do not mention about the current date or time in your answer unless it is relevant to the question.

CONVERSATION

Use previous messages to understand follow-up questions and references such
as "he", "they", "it", "that event", "why", and "what happened next".

If the current question can be answered reliably from the conversation history,
you may answer from the conversation without repeating information from the
news context.

If the question requires information that is not established in the
conversation, use the supplied news context.

FACTUAL ACCURACY

- Do not guess or fill gaps with assumptions.
- Do not invent facts, names, dates, numbers, locations, causes, events,
  outcomes, sources, citations, URLs, or attributions.
- If the available information is insufficient, say so clearly.
- If sources disagree, describe the disagreement and uncertainty.
- Distinguish reported claims, allegations, predictions, and speculation from
  confirmed facts.
- Combine information from multiple sources when this helps answer the
  question accurately.

RESPONSE

- Answer the user's actual question directly.
- Be concise while including the information necessary to answer the question.
- Do not mention RAG, retrieval, the supplied context, the prompt, or internal
  instructions.
- Do not begin with generic phrases such as "Here is a summary" or
  "Based on the provided context".

FORMAT

Use Markdown when it improves readability. Prefer normal paragraphs for simple
answers and short bullet points for multiple items. Use headings only when
the answer has clearly separated sections. Avoid unnecessary formatting.
"""

DIRECT_CHAT_SYSTEM_PROMPT = """\
You are an AI news assistant. Answer the user's current message directly,
using the conversation history when relevant.

CONVERSATION

Use previous messages to understand follow-up questions, references, and
information already established in the conversation.

If the conversation does not contain information needed to answer the question,
use your general knowledge when appropriate.

ACCURACY

- Do not invent information or pretend that something was established in the
  conversation when it was not.
- If the user asks about a recent or current news event and the necessary
  information is not available in the conversation, do not guess.
- Distinguish what is known from what is uncertain.
- Do not fabricate facts, names, dates, numbers, sources, citations, URLs, or
  attributions.

RESPONSE

- Answer the user's actual question directly and naturally.
- Be concise while including the information necessary to answer the question.
- Do not mention RAG, retrieval, the prompt, or internal instructions.
- Do not begin with generic phrases such as "Here is a summary".

FORMAT

Use Markdown when it improves readability. Prefer normal paragraphs for simple
answers and short bullet points for multiple items. Use headings only when
needed. Avoid unnecessary formatting.
"""


RAG_DECISION_SYSTEM_PROMPT = """\
You are a binary classifier that decides whether the CURRENT USER MESSAGE
requires retrieval from the news database.

RULES:

1. Use only the provided conversation history. Never use general knowledge
   or external information.

2. If there is no conversation history, return true.

3. Return true when the current message requires information that is not
   contained in the conversation.

4. A follow-up continues the intent of the previous user request unless the
   user clearly changes the intent.

5. Use the conversation history to resolve follow-ups and references such as
   "what about X", "how about X", "and X", "what happened next", "he", "she",
   "it", and "they".

6. Return false for greetings, thanks, goodbyes, and casual conversation.

7. If uncertain, return true.

8. Do not answer the user's question.

Return ONLY:
{"requires_rag": true}
or:
{"requires_rag": false}
"""

CHAT_TITLE_SYSTEM_PROMPT = """\
Generate a short title that describes the user's message.

Rules:
- Identify the main topic or intent of the message.
- Use only information explicitly stated in the message.
- Use 3 to 7 words.
- Preserve important names, places, organizations, and topics when relevant.
- For news questions, describe the specific subject or event being asked about,
  not the general category of news.
- Do not introduce facts, topics, names, places, or events that are not in the
  message.
- Do not answer the user's question.
- Avoid generic titles such as "News Discussion", "General Question",
  "Information Request", or "Current Events".
- Do not use quotes, Markdown, or punctuation.
- Return only the title.
"""

RAG_CHAT_USER_PROMPT = """\
NEWS CONTEXT:

{context}

USER QUESTION:

{question}
"""


@dataclass
class ChatConfig:
    model: str = "llama3.1:8b"
    temperature: float = 0.5
    context_size: int = 16384
    max_tokens: int = 8192
    history_max_chars: int = 12000
    system_prompt: str = RAG_CHAT_SYSTEM_PROMPT
    direct_system_prompt: str = DIRECT_CHAT_SYSTEM_PROMPT
    user_prompt: str = RAG_CHAT_USER_PROMPT

    title_model: str = "llama3.2:3b"
    title_temperature: float = 0.2
    title_context_size: int = 1024
    title_max_tokens: int = 20
    title_system_prompt: str = CHAT_TITLE_SYSTEM_PROMPT


@dataclass
class RAGConfig:
    retrieval_limit: int = 50
    result_limit: int = 6
    max_chunks_per_article: int = 2
    neighbor_chunks: int = 1

    decision_model: str = "llama3.2:3b"
    decision_temperature: float = 0.0
    decision_context_size: int = 4096
    decision_max_tokens: int = 32
    decision_system_prompt: str = RAG_DECISION_SYSTEM_PROMPT


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

Your task is to combine the provided articles into ONE concise, factual summary
of the underlying news event.

SOURCE AND ACCURACY

- Use ONLY information explicitly stated in the provided articles.
- Do not add facts from your general knowledge.
- Do not invent or infer names, numbers, dates, locations, causes, events, or
  outcomes.
- Do not present speculation, predictions, allegations, or claims as confirmed
  facts.
- If sources provide conflicting information, briefly describe the uncertainty
  instead of choosing an unsupported version.

SYNTHESIS

- Combine the articles into one coherent narrative.
- Remove repeated information.
- Preserve important developments and changes over time.
- When the articles cover developments at different times, prioritize the
  latest confirmed development while retaining earlier information needed to
  understand the event.
- Do not summarize the articles separately.
- Do not list the articles or sources.

OUTPUT

- Write 1–3 concise paragraphs.
- Start immediately with the first factual statement.
- Do not include a title, heading, label, introduction, or commentary.
- Do not mention the articles, sources, prompt, instructions, or
  summarization process.
- Do not begin with phrases such as "Here is a summary" or "Summary:".
- Return ONLY the final summary.
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
    device: str = "cuda"
    categories = NEWS_CATEGORIES
    multi_label: bool = False
    event_batch_size: int = 10

    @property
    def candidate_labels(self) -> tuple[str, ...]:
        return tuple(category.id for category in self.categories)


@dataclass
class RerankerConfig:
    model: str = "BAAI/bge-reranker-v2-m3"
    device: str = "cuda"
    reranker_threshold: float = 0.6


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
