"""Redis memory seeding for user preferences."""
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import redis
import hashlib

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
    **DEPRECATED** - Reads UserPref:* keys which are no longer populated.
    Use RedisProvider context injection instead.
    
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


# =============================================================================
# DEPRECATED FUNCTIONS - NO LONGER USED
# These functions create UserPref:* keys which are no longer read by any code.
# All preference data now uses Context:* namespace managed by RedisProvider.
# Use seed_redis_providers_directly() instead for all seeding operations.
# =============================================================================

async def seed_user_preferences_with_vectors(
    redis_url: str,
    vectorizer = None,
    seed_file: str = "seed.json"
) -> bool:
    """
    **DEPRECATED** - Creates UserPref:* keys which are no longer used.
    Use seed_redis_providers_directly() instead.
    
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
        
        # Connect to Redis and clean up old vnext keys only
        redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # Delete existing vnext user preference keys
        pattern = "cool-vibes-agent-vnext:UserPref:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"Deleted {len(existing_keys)} existing keys matching {pattern}")
        
        # Delete existing vnext context keys
        pattern = "cool-vibes-agent-vnext:Context:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"Deleted {len(existing_keys)} existing keys matching {pattern}")
        
        # Delete vnext conversation history
        conv_pattern = "cool-vibes-agent-vnext:Conversations:*"
        conv_keys = redis_client.keys(conv_pattern)
        if conv_keys:
            redis_client.delete(*conv_keys)
            logger.info(f"Deleted {len(conv_keys)} conversation keys matching {conv_pattern}")
        
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


async def seed_preferences_for_redis_provider(
    redis_url: str,
    seed_file: str = "seed.json"
) -> bool:
    """
    **DEPRECATED** - Use seed_redis_providers_directly() instead.
    
    Seed user preferences for RedisProvider using redisvl SearchIndex directly.
    
    This Redis-native approach:
    1. Creates a SearchIndex with vectorizer
    2. Loads seed data as documents with embeddings
    3. Index can be passed to RedisProvider for automatic context injection
    
    Args:
        redis_url: Redis connection URL
        seed_file: Path to seed.json
        
    Returns:
        True if successful
    """
    try:
        from redis_provider import create_vectorizer
        from redisvl.index import SearchIndex
        from redisvl.schema import IndexSchema
        import redis as redis_lib
        
        # Create vectorizer
        vectorizer = create_vectorizer()
        
        # Define schema matching RedisProvider's format
        schema = IndexSchema.from_dict({
            "index": {
                "name": "cool-vibes-context",
                "prefix": "cool-vibes-agent:Context",
                "storage_type": "hash"
            },
            "fields": [
                {"name": "content", "type": "text"},
                {"name": "user_name", "type": "tag"},
                {"name": "source", "type": "tag"},
                {"name": "timestamp", "type": "text"},
                {
                    "name": "content_vector",
                    "type": "vector",
                    "attrs": {
                        "dims": 1536,
                        "algorithm": "hnsw",
                        "distance_metric": "cosine"
                    }
                }
            ]
        })
        
        # Create index with vectorizer
        index = SearchIndex(schema, redis_url=redis_url)
        index.set_vectorizer(vectorizer)
        
        # Connect to Redis for cleanup
        redis_client = redis_lib.from_url(redis_url, decode_responses=False)
        
        # Clean up existing context
        pattern = "cool-vibes-agent:Context:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"Deleted {len(existing_keys)} existing Context keys")
        
        # Create/recreate index
        try:
            index.create(overwrite=True)
            logger.info("Created SearchIndex for RedisProvider context")
        except Exception as e:
            logger.warning(f"Index creation note: {e}")
        
        # Read seed data
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found")
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories in seed.json")
            return False
        
        # Prepare documents for batch loading
        documents = []
        keys = []
        timestamp = datetime.utcnow().isoformat()
        
        doc_id = 0
        for user_name, insights in user_memories.items():
            for insight_dict in insights:
                insight_text = insight_dict.get('insight', '')
                if insight_text:
                    # Create document with required fields
                    doc = {
                        "content": insight_text,
                        "user_name": user_name,
                        "source": "seed",
                        "timestamp": timestamp
                    }
                    documents.append(doc)
                    keys.append(f"cool-vibes-agent:Context:{user_name}:{doc_id}")
                    doc_id += 1
        
        # Load documents (redisvl will handle vectorization)
        if documents:
            loaded_keys = index.load(
                data=documents,
                keys=keys
            )
            logger.info(f"Seeded {len(loaded_keys)} preferences for RedisProvider across {len(user_memories)} users")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error seeding context for RedisProvider: {e}", exc_info=True)
        return False


async def seed_through_redis_provider(redis_providers: dict, seed_file: str = "seed.json") -> bool:
    """
    **DEPRECATED** - Use seed_redis_providers_directly() instead.
    
    Seed user preferences through RedisProvider instances.
    This ensures data is stored in the correct format that RedisProvider expects.
    
    Args:
        redis_providers: Dict mapping user_name to RedisProvider instance
        seed_file: Path to seed.json
        
    Returns:
        True if successful
    """
    try:
        # Read seed data
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found")
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories in seed.json")
            return False
        
        # Seed preferences for each user through their RedisProvider
        total_seeded = 0
        for user_name, provider in redis_providers.items():
            insights = user_memories.get(user_name, [])
            if not insights:
                logger.warning(f"No preferences found for {user_name} in seed.json")
                continue
            
            # Add each insight to the provider's index
            for insight_dict in insights:
                insight_text = insight_dict.get('insight', '')
                if insight_text:
                    try:
                        # Use provider's add method to store context
                        await provider.add(
                            content=insight_text,
                            metadata={
                                "source": "seed",
                                "user_name": user_name
                            }
                        )
                        total_seeded += 1
                    except Exception as e:
                        logger.error(f"Failed to add insight for {user_name}: {e}")
            
            logger.info(f"Seeded {len(insights)} preferences for {user_name} through RedisProvider")
        
        logger.info(f"Successfully seeded {total_seeded} total preferences through RedisProvider")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding through RedisProvider: {e}", exc_info=True)
        return False


async def seed_context_for_redis_provider(
    redis_url: str,
    vectorizer,
    seed_file: str = "seed.json"
) -> bool:
    """
    **DEPRECATED** - Use seed_redis_providers_directly() instead.
    
    Seed user context for RedisProvider matching the vnext schema.
    
    Args:
        redis_url: Redis connection URL
        vectorizer: Vectorizer instance for embeddings
        seed_file: Path to seed.json
        
    Returns:
        True if successful
    """
    try:
        import redis as redis_lib
        
        # Connect to Redis for cleanup and manual insertion
        redis_client = redis_lib.from_url(redis_url, decode_responses=False)
        
        # Clean up existing context
        pattern = "cool-vibes-agent-vnext:Context:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"Deleted {len(existing_keys)} existing Context keys")
        
        # Read seed data
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found")
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories in seed.json")
            return False
        
        # Manually insert documents with embeddings
        timestamp = datetime.utcnow().isoformat()
        total_seeded = 0
        
        for user_name, insights in user_memories.items():
            for idx, insight_dict in enumerate(insights):
                insight_text = insight_dict.get('insight', '')
                if insight_text:
                    # Generate embedding
                    embedding = vectorizer.embed(insight_text)
                    
                    # Convert to bytes for Redis
                    import numpy as np
                    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
                    
                    # Create Redis key
                    key = f"cool-vibes-agent-vnext:Context:{user_name}:{idx}"
                    
                    # Store as hash
                    redis_client.hset(key, mapping={
                        b"content": insight_text.encode('utf-8'),
                        b"user_name": user_name.encode('utf-8'),
                        b"source": b"seed",
                        b"timestamp": timestamp.encode('utf-8'),
                        b"embedding": embedding_bytes
                    })
                    total_seeded += 1
        
        logger.info(f"Seeded {total_seeded} context entries for RedisProvider across {len(user_memories)} users")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding context for RedisProvider: {e}", exc_info=True)
        return False


async def seed_redis_providers_directly(
    redis_providers: Dict[str, Any],
    redis_url: str,
    seed_file: str = "seed.json"
) -> bool:
    """
    Seed user preferences directly through RedisProvider._add() method.
    This is the correct way to populate RedisProvider's index.
    
    Args:
        redis_providers: Dict mapping user_name to RedisProvider instance
        redis_url: Redis connection URL for cleanup operations
        seed_file: Path to seed.json
        
    Returns:
        True if successful
    """
    try:
        # Clean up old Context:* keys before seeding
        logger.info("Cleaning up existing Context:* keys...")
        redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # Delete existing vnext context keys
        pattern = "cool-vibes-agent-vnext:Context:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"🗑️  Deleted {len(existing_keys)} existing Context:* keys")
        else:
            logger.info("No existing Context:* keys to delete")
        
        redis_client.close()
        
        # Read seed data
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found")
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories in seed.json")
            return False
        
        total_seeded = 0
        
        # Seed each user's RedisProvider with their preferences
        for user_name, provider in redis_providers.items():
            insights = user_memories.get(user_name, [])
            if not insights:
                logger.warning(f"No insights found for {user_name} in seed.json")
                continue
            
            # Prepare documents for this user
            documents = []
            for insight_dict in insights:
                insight_text = insight_dict.get('insight', '')
                if insight_text:
                    # Format document as RedisProvider expects
                    doc = {
                        "role": "user",  # Required field
                        "content": insight_text,  # Required field
                        "mime_type": "text/plain",
                    }
                    documents.append(doc)
            
            if documents:
                # Use provider's _add method to insert with proper vectorization
                await provider._add(data=documents)
                total_seeded += len(documents)
                logger.info(f"✓ Seeded {len(documents)} preferences for {user_name}")
        
        logger.info(f"✓ Successfully seeded {total_seeded} total preferences via RedisProvider")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding via RedisProvider._add(): {e}", exc_info=True)
        return False


def seed_to_redis_directly_sync(
    redis_url: str,
    vectorizer,
    seed_file: str = "seed.json"
) -> bool:
    """
    Seed user preferences directly to Redis using synchronous operations.
    This avoids event loop contamination by not using asyncio.run().
    
    Creates Context:* keys that RedisProvider will find when searching.
    RedisProviders should be created AFTER this completes.
    
    Args:
        redis_url: Redis connection URL
        vectorizer: AzureOpenAIVectorizer for generating embeddings
        seed_file: Path to seed.json
        
    Returns:
        True if successful
    """
    try:
        # Clean up old Context:* keys before seeding
        logger.info("Cleaning up existing Context:* keys...")
        redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # Delete existing vnext context keys
        pattern = b"cool-vibes-agent-vnext:Context:*"
        existing_keys = redis_client.keys(pattern)
        if existing_keys:
            redis_client.delete(*existing_keys)
            logger.info(f"🗑️  Deleted {len(existing_keys)} existing Context:* keys")
        else:
            logger.info("No existing Context:* keys to delete")
        
        # Read seed data
        seed_path = Path(seed_file)
        if not seed_path.exists():
            logger.warning(f"Seed file {seed_file} not found")
            redis_client.close()
            return False
            
        with open(seed_path, 'r') as f:
            seed_data = json.load(f)
        
        user_memories = seed_data.get('user_memories', {})
        if not user_memories:
            logger.warning("No user_memories in seed.json")
            redis_client.close()
            return False
        
        total_seeded = 0
        
        # Seed each user's preferences
        for user_name, insights in user_memories.items():
            if not insights:
                logger.warning(f"No insights found for {user_name} in seed.json")
                continue
            
            # Process each insight
            for insight_dict in insights:
                insight_text = insight_dict.get('insight', '')
                if not insight_text:
                    continue
                
                # Generate embedding synchronously
                embedding = vectorizer.embed(insight_text)
                
                # Convert embedding to bytes (matching RedisProvider format)
                import numpy as np
                embedding_bytes = np.asarray(embedding, dtype=np.float32).tobytes()
                
                # Create document in RedisProvider format
                # Generate unique ID based on content hash
                content_hash = hashlib.md5(insight_text.encode()).hexdigest()[:8]
                doc_id = f"{user_name}_{content_hash}"
                
                # Create key matching RedisProvider's pattern
                # Format: {prefix}:{doc_id} (the prefix already includes everything)
                key = f"cool-vibes-agent-vnext:Context:{doc_id}"
                
                # Store as Redis hash with ALL fields RedisProvider expects
                # CRITICAL: Must include partition fields (user_id, application_id, etc.)
                # RedisProvider filters by these fields, not by key path!
                redis_client.hset(
                    key,
                    mapping={
                        # Content fields
                        b"role": b"user",
                        b"content": insight_text.encode('utf-8'),
                        b"mime_type": b"text/plain",
                        b"embedding": embedding_bytes,
                        # Partition fields - REQUIRED for filtering!
                        b"user_id": user_name.encode('utf-8'),
                        b"application_id": b"cool-vibes-travel-agent-vnext",
                        b"agent_id": f"agent_{user_name.lower()}".encode('utf-8'),
                    }
                )
                total_seeded += 1
            
            logger.info(f"✓ Seeded {len(insights)} preferences for {user_name}")
        
        redis_client.close()
        logger.info(f"✓ Successfully seeded {total_seeded} total preferences directly to Redis")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding directly to Redis: {e}", exc_info=True)
        return False

