"""Redis memory seeding for user preferences."""
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import redis

logger = logging.getLogger(__name__)


def seed_user_preferences(redis_client: redis.Redis, seed_file: str = "seed.json") -> bool:
    """
    Seed user preferences from seed.json into Redis.
    
    Args:
        redis_client: Redis client instance
        seed_file: Path to the seed data file
        
    Returns:
        True if seeding was successful, False otherwise
    """
    try:
        # Read seed.json
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found. Skipping seeding.")
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        # Extract user memories
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories found in seed.json")
            return False
        
        # Store in Redis under "cool-vibes-agent:Preferences" key as a hash
        # Each user is a field in the hash with their insights as JSON
        preferences_key = "cool-vibes-agent:Preferences"
        
        # Clear existing preferences
        redis_client.delete(preferences_key)
        logger.info(f"Cleared existing preferences from Redis key: {preferences_key}")
        
        # Seed each user's preferences
        for user_name, insights in user_memories.items():
            # Convert insights list to JSON string for storage
            insights_json = json.dumps(insights)
            redis_client.hset(preferences_key, user_name, insights_json)
            logger.info(f"Seeded preferences for user: {user_name}")
        
        # Verify the seeding
        stored_users = redis_client.hkeys(preferences_key)
        logger.info(f"Successfully seeded {len(stored_users)} users to Redis: {[u.decode('utf-8') for u in stored_users]}")
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in seed file: {e}")
        return False
    except redis.RedisError as e:
        logger.error(f"Redis error during seeding: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during seeding: {e}")
        return False


def get_user_preferences(redis_client: redis.Redis, user_name: str) -> list[Dict[str, Any]]:
    """
    Retrieve user preferences from Redis UserPref vector keys.
    
    Args:
        redis_client: Redis client instance
        user_name: Name of the user
        
    Returns:
        List of user insights/preferences
    """
    try:
        # Find all UserPref keys for this user
        pattern = f"cool-vibes-agent:UserPref:{user_name}:*"
        keys = redis_client.keys(pattern)
        
        if not keys:
            logger.debug(f"No preferences found for user: {user_name}")
            return []
        
        # Retrieve all preferences for this user
        preferences = []
        for key in keys:
            pref_data = redis_client.hgetall(key)
            if pref_data:
                # Decode and extract preference_text
                decoded_data = {k.decode('utf-8'): v.decode('utf-8') if isinstance(v, bytes) else v 
                               for k, v in pref_data.items() if k.decode('utf-8') != 'embedding'}
                
                # Format as insight for backward compatibility
                if 'preference_text' in decoded_data:
                    preferences.append({
                        'insight': decoded_data['preference_text'],
                        'source': decoded_data.get('source', 'unknown'),
                        'timestamp': decoded_data.get('timestamp', '')
                    })
        
        return preferences
            
    except redis.RedisError as e:
        logger.error(f"Redis error retrieving preferences for {user_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving preferences for {user_name}: {e}")
        return []


async def seed_user_preferences_with_vectors(
    redis_url: str,
    vectorizer = None,
    seed_file: str = "seed.json"
) -> bool:
    """
    Seed user preferences with vector embeddings using RedisVL SearchIndex.
    
    Args:
        redis_url: Redis connection URL string (e.g., "redis://host:port")
        vectorizer: AzureOpenAIVectorizer instance (creates new if None)
        seed_file: Path to the seed data file
        
    Returns:
        True if seeding was successful, False otherwise
    """
    try:
        from context_provider import create_vectorizer, create_search_index, store_preference
        import redis as redis_lib
        
        # Create vectorizer if not provided
        if vectorizer is None:
            vectorizer = create_vectorizer()
        
        # Create search index
        index = create_search_index(redis_url, vectorizer)
        
        # Connect to Redis to clean up old preferences
        redis_client = redis_lib.from_url(redis_url, decode_responses=False)
        
        # Delete all existing UserPref keys before seeding
        pattern = "cool-vibes-agent:UserPref:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"Deleted {len(existing_keys)} existing UserPref keys before seeding")
        
        # Delete all conversation history
        conv_pattern = "cool-vibes-agent:Conversations:*"
        conv_keys = redis_client.keys(conv_pattern)
        if conv_keys:
            redis_client.delete(*conv_keys)
            logger.info(f"Deleted {len(conv_keys)} existing conversation keys before seeding")
        else:
            logger.info("No existing conversations to delete")
        
        # Try to create the index (will skip if exists)
        try:
            index.create(overwrite=False)
            logger.info("Created RediSearch index for user preferences")
        except Exception as e:
            logger.info(f"Index may already exist: {e}")
        
        # Read seed.json
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found. Skipping vector seeding.")
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        # Extract user memories
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories found in seed.json")
            return False
        
        total_seeded = 0
        
        # Seed preferences for each user
        for user_name, insights in user_memories.items():
            try:
                # Store each insight with embedding
                for insight_dict in insights:
                    insight_text = insight_dict.get('insight', '')
                    if insight_text:
                        await store_preference(
                            index=index,
                            vectorizer=vectorizer,
                            user_name=user_name,
                            preference_text=insight_text,
                            source="seed"
                        )
                        total_seeded += 1
                
                logger.info(f"Seeded {len(insights)} vectorized preferences for {user_name}")
                
            except Exception as e:
                logger.error(f"Failed to seed preferences for {user_name}: {e}")
                continue
        
        logger.info(f"Successfully seeded {total_seeded} vectorized preferences across all users")
        return True
        
    except Exception as e:
        logger.error(f"Error during vector seeding: {e}", exc_info=True)
        return False
