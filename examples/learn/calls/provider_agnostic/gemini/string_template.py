from mirascope.core import prompt_template
from mirascope import llm


@llm.call(provider="gemini", model="gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
