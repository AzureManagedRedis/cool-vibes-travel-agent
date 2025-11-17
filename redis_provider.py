"""Redis Context Provider configuration using agent-framework-redis with Azure OpenAI."""
import os
import logging
from typing import Any
from agent_framework_redis import RedisProvider
from redisvl.utils.vectorize import BaseVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from openai import AzureOpenAI
from pydantic import Field, PrivateAttr

logger = logging.getLogger(__name__)


class AzureOpenAIVectorizer(BaseVectorizer):
    """Custom vectorizer for Azure OpenAI embeddings compatible with redisvl."""
    
    model: str
    dims: int = 1536  # text-embedding-3-small dimensions
    _client: Any = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize Azure OpenAI client after Pydantic initialization."""
        self._client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-15-preview")
        )
        
    def embed(self, text: str, **kwargs):
        """Generate embedding for a single text."""
        response = self._client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_many(self, texts: list[str], **kwargs):
        """Generate embeddings for multiple texts."""
        response = self._client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    async def aembed(self, text: str, **kwargs):
        """Async embedding generation - falls back to sync for Azure OpenAI."""
        return self.embed(text, **kwargs)
    
    async def aembed_many(self, texts: list[str], batch_size: int = 10, **kwargs):
        """Async embedding generation - falls back to sync for Azure OpenAI."""
        return self.embed_many(texts, **kwargs)


def create_vectorizer() -> AzureOpenAIVectorizer:
    """
    Create Azure OpenAI text vectorizer for embeddings.
    
    Returns:
        Configured AzureOpenAIVectorizer instance
    """
    embedding_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-small')
    
    vectorizer = AzureOpenAIVectorizer(model=embedding_deployment)
    
    logger.info(f"✓ Created vectorizer with Azure OpenAI model: {embedding_deployment}")
    return vectorizer


def create_redis_provider(user_name: str, redis_url: str, vectorizer: AzureOpenAIVectorizer, overwrite_index: bool = False) -> RedisProvider:
    """
    Create RedisProvider instance for automatic context injection.
    
    Args:
        user_name: User identifier (e.g., "Mark", "Shruti")
        redis_url: Redis connection URL
        vectorizer: Shared vectorizer instance to ensure consistency
        overwrite_index: Whether to overwrite existing index (only True for first provider)
        
    Returns:
        Configured RedisProvider instance
    """
    # Use shared vectorizer passed as parameter
    
    # Create and configure provider with proper index management
    provider = RedisProvider(
        redis_url=redis_url,
        index_name="user_preferences_ctx_vnext",
        prefix="cool-vibes-agent-vnext:Context:",
        application_id="cool-vibes-travel-agent-vnext",
        agent_id=f"agent_{user_name.lower()}",
        user_id=user_name,
        redis_vectorizer=vectorizer,
        vector_field_name="embedding",
        vector_algorithm="hnsw",
        vector_distance_metric="cosine",
        scope_to_per_operation_thread_id=True,  # Enable per-conversation thread isolation
        overwrite_index=overwrite_index  # Only overwrite for first provider
    )
    
    # Ensure the index exists by accessing redis_index property
    # This triggers index creation if it doesn't exist
    try:
        _ = provider.redis_index
        logger.info(f"✓ Created RedisProvider for user: {user_name} with index initialized")
    except Exception as e:
        logger.warning(f"Index initialization warning for {user_name}: {e}")
    
    return provider
