"""Redis conversation storage configuration for Agent Framework."""
import os
import logging
from agent_framework_redis._chat_message_store import RedisChatMessageStore

logger = logging.getLogger(__name__)


def create_chat_message_store(thread_id: str, redis_url: str = None):
    """
    Create a Redis-backed ChatMessageStore for conversation persistence.
    
    Args:
        thread_id: Unique identifier for the conversation thread
        redis_url: Redis connection URL (defaults to env variable)
        
    Returns:
        RedisChatMessageStore instance configured for the thread
    """
    if redis_url is None:
        redis_url = os.getenv('REDIS_URL')
    
    try:
        # AMR/AF: Create and return the RedisChatMessageStore instance
        # Ignite Code Location
        store = RedisChatMessageStore(
            redis_url=redis_url,
            thread_id=thread_id,
            key_prefix="cool-vibes-agent-vnext:Conversations",
            max_messages=1000,  # Keep up to 1000 messages per thread
        )
        logger.info(f"Created ChatMessageStore for thread: {thread_id}")
        return store
    except Exception as e:
        logger.error(f"Failed to create ChatMessageStore: {e}")
        raise


def create_chat_message_store_factory(redis_url: str = None):
    """
    Create a factory function for chat message stores.
    
    This factory allows the Agent Framework to create stores for new threads dynamically.
    
    Args:
        redis_url: Redis connection URL (defaults to env variable)
        
    Returns:
        Factory function that creates RedisChatMessageStore instances
    """
    if redis_url is None:
        redis_url = os.getenv('REDIS_URL')
    
    def factory(thread_id: str = None):
        """Create a ChatMessageStore for a given thread."""
        if thread_id is None:
            import uuid
            thread_id = str(uuid.uuid4())
            logger.info(f"Generated new thread_id: {thread_id}")
        
        return create_chat_message_store(thread_id, redis_url)
    
    return factory
