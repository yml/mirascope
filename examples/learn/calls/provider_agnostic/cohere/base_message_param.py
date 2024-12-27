from mirascope.core import BaseMessageParam
from mirascope import llm


@llm.call(provider="cohere", model="command-r-plus")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response = recommend_book("fantasy")
print(response.content)
