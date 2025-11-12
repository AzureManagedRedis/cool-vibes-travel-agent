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


def user_preferences(user_name: Annotated[str, "The name of the user to retrieve preferences for"]) -> str:
    """
    Retrieve user preferences from long-term Redis memory.
    
    Args:
        user_name: The name of the user
        
    Returns:
        A formatted string of user preferences
    """
    if not _redis_client:
        return "User preferences service is not available."
    
    insights = get_user_preferences(_redis_client, user_name)
    
    if not insights:
        return f"No stored preferences found for {user_name}. This might be a new user."
    
    # Format insights into a readable string
    preferences_list = [insight.get('insight', '') for insight in insights if 'insight' in insight]
    
    if preferences_list:
        return f"User {user_name}'s preferences:\n" + "\n".join(f"- {pref}" for pref in preferences_list)
    else:
        return f"No specific preferences found for {user_name}."


async def remember_preference(
    user_name: Annotated[str, "The name of the user"],
    preference: Annotated[str, "The preference to remember for this user"]
) -> str:
    """
    Store a new preference for a user with semantic search capabilities.
    This allows the agent to learn new preferences during conversations.
    
    Args:
        user_name: The name of the user
        preference: The preference text to remember
        
    Returns:
        Confirmation message
    """
    if not _search_index or not _vectorizer:
        return "❌ Preference storage service is not available."
    
    try:
        from context_provider import store_preference
        
        # Store preference with vector embedding
        await store_preference(
            index=_search_index,
            vectorizer=_vectorizer,
            user_name=user_name,
            preference_text=preference,
            source="learned"
        )
        
        logger.info(f"Stored new preference for {user_name}: {preference}")
        return f"✅ I'll remember that {user_name} {preference}"
        
    except Exception as e:
        logger.error(f"Failed to store preference: {e}")
        return f"❌ Sorry, I couldn't store that preference: {str(e)}"


async def get_semantic_preferences(
    user_name: Annotated[str, "The name of the user"],
    query: Annotated[Optional[str], "Optional query to find relevant preferences"] = None
) -> str:
    """
    Retrieve user preferences using semantic search.
    If query is provided, returns preferences most relevant to the query.
    
    Args:
        user_name: The name of the user
        query: Optional semantic query to filter preferences
        
    Returns:
        Formatted string of user preferences
    """
    if not _search_index or not _vectorizer:
        # Fallback to static preferences
        return user_preferences(user_name)
    
    try:
        from context_provider import retrieve_preferences
        
        results = await retrieve_preferences(
            index=_search_index,
            vectorizer=_vectorizer,
            user_name=user_name,
            query_text=query,
            top_k=5
        )
        
        if not results:
            return f"No preferences found for {user_name}."
        
        # Format results
        prefs = []
        for doc in results:
            pref_text = doc.get('preference_text', '')
            source = doc.get('source', 'unknown')
            if pref_text:
                prefs.append(f"- {pref_text} (from {source})")
        
        if query:
            header = f"User {user_name}'s preferences relevant to '{query}':\n"
        else:
            header = f"User {user_name}'s preferences:\n"
        
        return header + "\n".join(prefs)
        
    except Exception as e:
        logger.error(f"Failed to retrieve semantic preferences: {e}")
        # Fallback to static preferences
        return user_preferences(user_name)


async def reseed_user_preferences() -> str:
    """
    Delete all existing vectorized user preferences from Redis and re-seed from seed.json.
    This will reset all preferences to the initial seed data.
    
    Returns:
        Confirmation message
    """
    try:
        if not _redis_client:
            return "❌ Cannot reseed - Redis client not available"
        
        logger.info("Starting reseed operation...")
        
        # Delete all preference keys
        pattern = "cool-vibes-agent:UserPref:*"
        keys = _redis_client.keys(pattern)
        if keys:
            _redis_client.delete(*keys)
            logger.info(f"Deleted {len(keys)} preference keys")
        
        # Try to drop the RediSearch index
        try:
            _redis_client.execute_command('FT.DROPINDEX', 'user_preferences_idx', 'DD')
            logger.info("Dropped RediSearch index")
        except Exception as e:
            logger.warning(f"Could not drop index (may not exist): {e}")
        
        # Re-seed with vectors
        import os
        from seeding import seed_user_preferences_with_vectors
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return "❌ REDIS_URL environment variable not set"
        
        success = await seed_user_preferences_with_vectors(
            redis_url=redis_url,
            vectorizer=_vectorizer
        )
        
        if success:
            return "✅ Successfully reset and re-seeded all user preferences from seed.json with vector embeddings"
        else:
            return "⚠️ Reseed completed with warnings - check logs"
            
    except Exception as e:
        logger.error(f"Error during reseed: {e}", exc_info=True)
        return f"❌ Failed to reseed preferences: {str(e)}"
