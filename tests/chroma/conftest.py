"""Configuration for the Mirascope chroma module tests."""

import pytest

from mirascope.chroma.types import ChromaSettings
from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.rag import BaseEmbedder


class TestEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> list[str]:
        return input

    async def embed_async(self, input: list[str]) -> list[str]:
        return input

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]


@pytest.fixture
def fixture_persistent_client() -> ChromaVectorStore:
    """Fixture for a persistent ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        embedder = TestEmbedder()
        client_settings = ChromaSettings(mode="persistent")

    return VectorStore()


@pytest.fixture
def fixture_http_client() -> ChromaVectorStore:
    """Fixture for an HTTP ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        embedder = TestEmbedder()
        client_settings = ChromaSettings(mode="http")

    return VectorStore()


@pytest.fixture
def fixture_ephemeral_client() -> ChromaVectorStore:
    """Fixture for an ephemeral ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        client_settings = ChromaSettings(mode="ephemeral")
        embedder = TestEmbedder()

    return VectorStore()
