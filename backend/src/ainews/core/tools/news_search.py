from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel


class NewsSearchArguments(BaseModel):
    query: str


NEWS_SEARCH_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "search_news",
        "description": (
            "Search the news database only when the user's request requires "
            "news information, such as current events, recent developments, "
            "specific news events, or recent information about people, "
            "organizations, places, or topics. "
            "Do not use this tool for greetings, small talk, casual "
            "conversation, thanks, goodbyes, or questions that do not require "
            "news information. "
            "For follow-up questions that require news retrieval, formulate "
            "a concise, self-contained search query using the conversation "
            "history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A concise, self-contained query containing only the "
                        "news information needed to answer the user's request."
                    ),
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
