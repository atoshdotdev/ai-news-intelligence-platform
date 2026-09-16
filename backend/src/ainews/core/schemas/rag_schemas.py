from pydantic import BaseModel


class RAGDecision(BaseModel):
    requires_rag: bool
