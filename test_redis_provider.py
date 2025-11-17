"""Test script for RedisProvider seeding and retrieval."""
import asyncio
import os
from dotenv import load_dotenv
from seeding import seed_preferences_for_redis_provider
from redis_provider import create_redis_provider, create_vectorizer

async def test_redis_provider():
    """Test the Redis-native seeding and RedisProvider integration."""
    
    # Load environment
    load_dotenv()
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    print("=" * 60)
    print("Testing Redis-Native Seeding & RedisProvider")
    print("=" * 60)
    
    # Step 1: Seed preferences
    print("\n[1/3] Seeding preferences...")
    success = await seed_preferences_for_redis_provider(redis_url)
    
    if not success:
        print("❌ Seeding failed")
        return
    
    print("✅ Seeding completed")
    
    # Step 2: Create RedisProvider
    print("\n[2/3] Creating RedisProvider...")
    provider = create_redis_provider(
        user_name="Tyler",
        thread_id="test-thread",
        redis_url=redis_url
    )
    print(f"✅ RedisProvider created: {type(provider).__name__}")
    
    # Step 3: Test search (manual query to verify data is accessible)
    print("\n[3/3] Testing semantic search...")
    from redisvl.index import SearchIndex
    from redisvl.query import VectorQuery
    
    try:
        vectorizer = create_vectorizer()
        
        # Create a query index
        schema = {
            "index": {
                "name": "cool-vibes-context",
                "prefix": "cool-vibes-agent:Context"
            },
            "fields": [
                {"name": "content", "type": "text"},
                {"name": "user_name", "type": "tag"},
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
        }
        
        from redisvl.schema import IndexSchema
        search_index = SearchIndex(IndexSchema.from_dict(schema), redis_url=redis_url)
        search_index.set_vectorizer(vectorizer)
        
        # Search for Tyler's preferences
        query_text = "travel preferences flights hotels"
        query = VectorQuery(
            vector=vectorizer.embed(query_text),
            vector_field_name="content_vector",
            return_fields=["content", "user_name", "source"],
            num_results=3,
            filter_expression="@user_name:{Tyler}"
        )
        
        results = search_index.query(query)
        
        print(f"\n🔍 Search results for query: '{query_text}'")
        print(f"   Filter: user_name=Tyler")
        print(f"   Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.get('content', 'N/A')[:80]}...")
            print(f"      User: {result.get('user_name')}, Source: {result.get('source')}")
        
        print("\n✅ Semantic search working!")
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_redis_provider())
