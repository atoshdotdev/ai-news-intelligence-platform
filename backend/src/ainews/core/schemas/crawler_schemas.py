from pydantic import BaseModel


class ArticleLinkItem(BaseModel):
    link_url: str
