"""Redis memory seeding for user preferences."""
import json
import logging
from pathlib import Path
from typing import Dict, Any
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
        
        # Store in Redis under "Preferences" key as a hash
        # Each user is a field in the hash with their insights as JSON
        preferences_key = "Preferences"
        
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
    Retrieve user preferences from Redis.
    
    Args:
        redis_client: Redis client instance
        user_name: Name of the user
        
    Returns:
        List of user insights/preferences
    """
    try:
        preferences_key = "Preferences"
        insights_json = redis_client.hget(preferences_key, user_name)
        
        if insights_json:
            return json.loads(insights_json.decode('utf-8'))
        else:
            logger.debug(f"No preferences found for user: {user_name}")
            return []
            
    except redis.RedisError as e:
        logger.error(f"Redis error retrieving preferences for {user_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving preferences for {user_name}: {e}")
        return []
