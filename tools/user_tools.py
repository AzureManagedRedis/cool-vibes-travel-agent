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
_current_user = None  # Track current user for the agent

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


def set_current_user(user_name: str):
    """Set the current user context for tools."""
    global _current_user
    _current_user = user_name


# user_preferences() removed - RedisProvider now automatically injects preferences
# No need for explicit tool call since context is always available


def create_remember_preference_for_user(user_name: str):
    """Create a remember_preference function bound to a specific user."""
    async def remember_preference(
        preference: Annotated[str, "The preference to remember for this user"]
    ) -> str:
        """
        Store a new preference for the current user directly into RedisProvider's context store.
        This allows the agent to learn new preferences during conversations.
        Stored preferences will be automatically injected in future conversations.
        
        Args:
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
            # Format: user_name_key_id embedded in doc_id
            key_id = str(uuid.uuid4())[:8]
            doc_id = f"{user_name}_{key_id}"
            key = f"cool-vibes-agent-vnext:Context:{doc_id}"
            
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
    
    # Set function name and annotations for the agent framework
    remember_preference.__name__ = "remember_preference"
    return remember_preference


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



