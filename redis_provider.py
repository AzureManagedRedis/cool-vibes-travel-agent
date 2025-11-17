"""Redis Context Provider configuration using agent-framework-redis."""
import os
import logging
from agent_framework_redis._provider import RedisProvider
from redisvl.utils.vectorize import OpenAITextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


def create_vectorizer() -> OpenAITextVectorizer:
    """
    Create OpenAI text vectorizer configured for Azure OpenAI.
    
    Returns:
        Configured OpenAITextVectorizer instance with Azure client
    """
    embedding_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-small')
    
    # Create Azure OpenAI client
    azure_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-15-preview")
    )
    
    # Optional: Add caching for performance
    cache = None
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            cache = EmbeddingsCache(
                name="openai_embeddings_cache",
                redis_url=redis_url
            )
            logger.info("✓ Embeddings cache enabled")
        except Exception as e:
            logger.warning(f"⚠ Could not enable embeddings cache: {e}")
    
    # Create vectorizer with Azure client
    vectorizer = OpenAITextVectorizer(
        model=embedding_deployment,
        client=azure_client,
        cache=cache
    )
    
    logger.info(f"✓ Created vectorizer with Azure OpenAI model: {embedding_deployment}")
    return vectorizer


def create_redis_provider(user_name: str, thread_id: str, redis_url: str) -> RedisProvider:
    """
    Create RedisProvider instance for automatic context injection.
    
    Args:
        user_name: User identifier (e.g., "Mark", "Shruti")
        thread_id: Conversation thread identifier
        redis_url: Redis connection URL
        
    Returns:
        Configured RedisProvider instance
    """
    # Create vectorizer
    vectorizer = create_vectorizer()
    
    # Create and configure provider
    provider = RedisProvider(
        redis_url=redis_url,
        index_name="user_preferences_ctx",
        prefix="cool-vibes-agent:Context",
        application_id="cool-vibes-travel-agent",
        agent_id="travel-agent",
        user_id=user_name,
        redis_vectorizer=vectorizer,
        vector_field_name="embedding",
        vector_algorithm="hnsw",
        vector_distance_metric="cosine",
        thread_id=thread_id
    )
    
    logger.info(f"✓ Created RedisProvider for user: {user_name}, thread: {thread_id}")
    return provider
