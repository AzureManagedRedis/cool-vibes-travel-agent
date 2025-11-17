"""User preference tools."""
from typing import Annotated, Optional
import redis
import logging
import os
from seeding import get_user_preferences

# Global Redis client and search index (will be set by main.py)
_redis_client: redis.Redis = None
_search_index = None
_vectorizer = None

logger = logging.getLogger(__name__)


def set_redis_client(client: redis.Redis):
    """Set the global Redis client."""
    global _redis_client
    _redis_client = client


def set_search_index(index):
    """Set the global search index for vector operations."""
    global _search_index
    _search_index = index


def set_vectorizer(vectorizer):
    """Set the global vectorizer for embeddings."""
    global _vectorizer
    _vectorizer = vectorizer


# user_preferences() removed - RedisProvider now automatically injects preferences
# No need for explicit tool call since context is always available


async def remember_preference(
    user_name: Annotated[str, "The name of the user"],
    preference: Annotated[str, "The preference to remember for this user"]
) -> str:
    """
    Store a new preference for a user directly into RedisProvider's context store.
    This allows the agent to learn new preferences during conversations.
    Stored preferences will be automatically injected in future conversations.
    
    Args:
        user_name: The name of the user
        preference: The preference text to remember
        
    Returns:
        Confirmation message
    """
    if not _redis_client or not _vectorizer:
        return "❌ Preference storage service is not available."
    
    try:
        from datetime import datetime
        import uuid
        import numpy as np
        
        # Generate embedding for the preference
        embedding = _vectorizer.embed(preference)
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        
        # Create unique key in RedisProvider's Context namespace
        doc_id = str(uuid.uuid4())[:8]
        key = f"cool-vibes-agent-vnext:Context:{user_name}:{doc_id}"
        
        # Store in same format as RedisProvider expects
        _redis_client.hset(key, mapping={
            b"content": preference.encode('utf-8'),
            b"role": b"user",
            b"mime_type": b"text/plain",
            b"user_id": user_name.encode('utf-8'),
            b"application_id": b"cool-vibes-travel-agent-vnext",
            b"agent_id": f"agent_{user_name.lower()}".encode('utf-8'),
            b"embedding": embedding_bytes,
            b"timestamp": datetime.utcnow().isoformat().encode('utf-8'),
            b"source": b"learned"
        })
        
        logger.info(f"Stored new preference for {user_name} in Context store: {preference}")
        return f"✅ I'll remember that {user_name} {preference}"
        
    except Exception as e:
        logger.error(f"Failed to store preference: {e}", exc_info=True)
        return f"❌ Sorry, I couldn't store that preference: {str(e)}"


async def get_semantic_preferences(
    user_name: Annotated[str, "The name of the user"],
    query: Annotated[str, "Specific query to find relevant preferences for (e.g., 'hotels in Paris', 'food preferences')"]
) -> str:
    """
    Search user preferences using semantic search with a specific query.
    Use this when you need to find preferences relevant to a particular topic or context.
    Note: General preferences are automatically provided, use this only for targeted searches.
    
    Args:
        user_name: The name of the user
        query: Specific query to search preferences (required)
        
    Returns:
        Formatted string of relevant preferences
    """
    if not _redis_client or not _vectorizer:
        return "❌ Semantic search service is not available."
    
    try:
        import numpy as np
        
        # Generate embedding for the query
        query_embedding = _vectorizer.embed(query)
        
        # Search in Context namespace using Redis vector search
        # This searches the same data RedisProvider uses
        pattern = f"cool-vibes-agent-vnext:Context:{user_name}:*"
        keys = _redis_client.keys(pattern)
        
        if not keys:
            return f"No preferences found for {user_name}."
        
        # Calculate similarity scores
        results = []
        for key in keys:
            doc = _redis_client.hgetall(key)
            if b"embedding" in doc and b"content" in doc:
                # Decode embedding
                stored_embedding = np.frombuffer(doc[b"embedding"], dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                results.append({
                    "content": doc[b"content"].decode('utf-8'),
                    "source": doc.get(b"source", b"unknown").decode('utf-8'),
                    "similarity": similarity
                })
        
        # Sort by similarity and take top 5
        results.sort(key=lambda x: x["similarity"], reverse=True)
        top_results = results[:5]
        
        if not top_results:
            return f"No preferences found for {user_name} matching '{query}'."
        
        # Format results
        prefs = []
        for doc in top_results:
            content = doc['content']
            source = doc['source']
            score = doc['similarity']
            prefs.append(f"- {content} (from {source}, relevance: {score:.2f})")
        
        header = f"User {user_name}'s preferences relevant to '{query}':\n"
        return header + "\n".join(prefs)
        
    except Exception as e:
        logger.error(f"Failed to retrieve semantic preferences: {e}", exc_info=True)
        return f"❌ Error searching preferences: {str(e)}"


async def reseed_user_preferences() -> str:
    """
    Delete all existing context from RedisProvider and re-seed from seed.json.
    This will reset all preferences to the initial seed data.
    Note: This affects the same data RedisProvider uses for automatic context injection.
    
    Returns:
        Confirmation message
    """
    try:
        if not _redis_client:
            return "❌ Cannot reseed - Redis client not available"
        
        logger.info("Starting reseed operation for RedisProvider context...")
        
        # Delete all Context keys (what RedisProvider uses)
        pattern = "cool-vibes-agent-vnext:Context:*"
        keys = _redis_client.keys(pattern)
        if keys:
            _redis_client.delete(*keys)
            logger.info(f"Deleted {len(keys)} context keys")
        
        # Try to drop the RediSearch index used by RedisProvider
        try:
            _redis_client.execute_command('FT.DROPINDEX', 'user_preferences_ctx_vnext', 'DD')
            logger.info("Dropped RedisProvider index")
        except Exception as e:
            logger.warning(f"Could not drop index (may not exist): {e}")
        
        # Re-seed using RedisProvider's seeding method
        import os
        from seeding import seed_redis_providers_directly
        from redis_provider import create_redis_provider
        import json
        
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return "❌ REDIS_URL environment variable not set"
        
        # Load users from seed.json
        with open('seed.json', 'r') as f:
            seed_data = json.load(f)
            users = list(seed_data.get('user_memories', {}).keys())
        
        # Recreate RedisProviders and seed
        redis_providers = {}
        for user_name in users:
            provider = create_redis_provider(user_name, redis_url, _vectorizer)
            redis_providers[user_name] = provider
        
        success = await seed_redis_providers_directly(redis_providers, redis_url)
        
        if success:
            return "✅ Successfully reset and re-seeded all user context from seed.json into RedisProvider"
        else:
            return "⚠️ Reseed completed with warnings - check logs"
            
    except Exception as e:
        logger.error(f"Error during reseed: {e}", exc_info=True)
        return f"❌ Failed to reseed context: {str(e)}"
