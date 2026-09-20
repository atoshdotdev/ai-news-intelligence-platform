from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel


class NewsSearchArguments(BaseModel):
    query: str


NEWS_SEARCH_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "search_news",
        "description": (
            "Search the news database for information relevant to the user's "
            "request. Use this tool when the user asks about news, current "
            "events, recent developments, people, organizations, places, "
            "events, or information that may be contained in the news database. "
            "For follow-up questions, formulate a self-contained search query "
            "using the conversation history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A concise, self-contained search query for the news database."
                    ),
                },
            },
            "required": ["query"],
        },
    },
}
