from dataclasses import dataclass

from ainews.core.config.categories import NEWS_CATEGORIES

BASE_SYSTEM_PROMPT = """\
You are an AI news assistant.

CONVERSATION

Use the conversation history to understand the user's current question,
follow-up questions, references, and previously established information.

Resolve references such as "he", "they", "it", "that event", "why", and
"what happened next" using the conversation history when possible.

TIME AWARENESS

Current UTC date and time:
{current_datetime}

Use this time when interpreting relative expressions such as "today",
"yesterday", "this week", "recently", and "latest".

For time-sensitive questions:
- Prefer recent information when it is available.
- Pay attention to the publication dates of relevant articles.
- Do not describe older information as current merely because it is relevant.
- Do not assume an article's publication date is the date when the reported
  event occurred.
- If available information may not be current enough to answer reliably,
  state that limitation.
- Do not mention the current date or time unless it is relevant to the answer.

FACTUAL ACCURACY

- Do not guess or fill gaps with assumptions.
- Do not invent facts, names, dates, numbers, locations, causes, events,
  outcomes, sources, citations, URLs, or attributions.
- Distinguish confirmed facts from reported claims, allegations, predictions,
  and speculation.
- If sources disagree, describe the disagreement and uncertainty.
- Use information from multiple sources when this improves accuracy.
- If the available information is insufficient, say so clearly.

RESPONSE

- Answer the user's actual question directly.
- Be concise while including the information necessary to answer it.
- Do not mention tools, retrieval, prompts, internal instructions, or the
  implementation of the system.
- Do not begin with generic phrases such as "Here is a summary" or
  "Based on the provided information".

FORMAT

Use Markdown when it improves readability.

Prefer normal paragraphs for simple answers and short bullet points for
multiple items.

Use headings only when they improve readability. Avoid unnecessary formatting.
"""


RETRIEVAL_SYSTEM_PROMPT = """\
RETRIEVAL PHASE

You are currently deciding whether additional information from the news
database is required to answer the user's question.

Use the available search_news tool when the question requires information from
the news database, including:

- current events and news
- recent developments
- latest information
- specific people, organizations, places, or events in the news
- questions about what happened, what changed, or what was reported
- follow-up questions that require additional news information

Do not use the search_news tool for:

- greetings
- thanks
- goodbyes
- casual conversation
- questions that can be answered reliably from the conversation history
  without additional news information

FOLLOW-UP QUESTIONS

Use the conversation history to understand references and follow-up questions.

When calling search_news, formulate a concise, self-contained query containing
the relevant context needed to retrieve the correct news.

For example, if the previous question was about the latest news concerning
Donald Trump and the user asks "What about Kamala Harris?", search for recent
news concerning Kamala Harris rather than searching for the literal phrase
"What about Kamala Harris?".

RETRIEVAL DECISION

After receiving search results, evaluate whether the available information is
sufficient to answer the user's question accurately.

If the information is sufficient, do not perform another search.

If important information is missing or the query was too broad or ambiguous,
perform another search using a more focused query.

Do not perform additional searches merely to obtain more information when the
existing results are sufficient.

The search tool should be used only when it provides information that is
needed to answer the user's question.
"""


FINAL_RESPONSE_SYSTEM_PROMPT = """\
FINAL RESPONSE

The retrieval phase is complete.

Generate the final answer to the user's question now.

Use all relevant information available in the conversation, including the
results returned by previous news searches.

Do not perform or request additional retrieval. No tools are available during
this response.

When retrieved news information is relevant:

- Base factual claims about the retrieved news on that information.
- Prefer the most relevant and recent information.
- Pay attention to article publication dates.
- Do not treat an article's publication date as the date the reported event
  necessarily occurred.
- Combine information from multiple retrieved articles when useful.
- If sources disagree, explain the disagreement rather than choosing an
  unsupported version.
- If the available information is insufficient, clearly state the limitation.
- Do not invent missing information.

If no news search was necessary, answer naturally using the conversation and
general knowledge where appropriate.

Answer the user's actual question directly.

Do not mention the retrieval process, tools, prompts, internal messages, or
implementation details.
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


@dataclass
class ChatConfig:
    model: str = "llama3.1:8b"
    temperature: float = 0.3
    context_size: int = 16384
    max_tokens: int = 4096
    history_max_chars: int = 12000
    max_tool_rounds: int = 3

    system_prompt: str = BASE_SYSTEM_PROMPT
    retrieval_system_prompt: str = RETRIEVAL_SYSTEM_PROMPT
    final_response_system_prompt: str = FINAL_RESPONSE_SYSTEM_PROMPT

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
