from dataclasses import dataclass


@dataclass(frozen=True)
class NewsCategory:
    id: str
    name: str


NEWS_CATEGORIES: tuple[NewsCategory, ...] = (
    NewsCategory("politics", "Politics"),
    NewsCategory("business", "Business"),
    NewsCategory("technology", "Technology"),
    NewsCategory("science", "Science"),
    NewsCategory("health", "Health"),
    NewsCategory("environment", "Environment"),
    NewsCategory("world", "World"),
    NewsCategory("sports", "Sports"),
    NewsCategory("crime", "Crime"),
    NewsCategory("war", "War"),
    NewsCategory("education", "Education"),
    NewsCategory("entertainment", "Entertainment"),
    NewsCategory("other", "Other"),
)
