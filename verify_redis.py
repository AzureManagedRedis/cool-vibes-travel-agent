"""Utility script to verify conversation storage in Redis."""
import os
import redis
from dotenv import load_dotenv
import json

def verify_conversation_storage():
    """Verify that conversations are being stored in Redis."""
    load_dotenv()
    redis_url = os.getenv('REDIS_URL')
    
    if not redis_url:
        print("❌ REDIS_URL not found in environment")
        return
    
    try:
        # Connect to Redis
        client = redis.from_url(redis_url, decode_responses=True)
        client.ping()
        print("✅ Connected to Redis successfully\n")
        
        # Search for conversation keys
        print("🔍 Searching for conversation keys...")
        print("=" * 60)
        
        # Pattern to match conversation keys
        pattern = "cool-vibes-agent:Conversations:*"
        keys = client.keys(pattern)
        
        if not keys:
            print(f"⚠️  No conversation keys found matching pattern: {pattern}")
            print("\nTo generate conversations:")
            print("1. Run the application: python main.py")
            print("2. Open http://localhost:8000 in your browser")
            print("3. Start a conversation with the agent")
            print("4. Run this script again to see stored conversations")
        else:
            print(f"✅ Found {len(keys)} conversation-related keys:\n")
            
            for key in sorted(keys):
                print(f"📝 Key: {key}")
                
                # Get key type and show sample data
                key_type = client.type(key)
                print(f"   Type: {key_type}")
                
                if key_type == 'string':
                    value = client.get(key)
                    try:
                        parsed = json.loads(value)
                        print(f"   Content (JSON): {json.dumps(parsed, indent=2)[:200]}...")
                    except:
                        print(f"   Content: {value[:100]}...")
                elif key_type == 'list':
                    length = client.llen(key)
                    print(f"   List length: {length}")
                    if length > 0:
                        first_item = client.lindex(key, 0)
                        print(f"   First item: {first_item[:100]}...")
                elif key_type == 'hash':
                    fields = client.hkeys(key)
                    print(f"   Hash fields: {len(fields)} - {fields[:5]}")
                elif key_type == 'zset':
                    count = client.zcard(key)
                    print(f"   Sorted set size: {count}")
                
                print()
        
        # Also check for user preferences
        print("\n" + "=" * 60)
        print("📋 User Preferences Key:")
        print("=" * 60)
        
        prefs_key = "cool-vibes-agent:Preferences"
        if client.exists(prefs_key):
            users = client.hkeys(prefs_key)
            print(f"✅ Found preferences for {len(users)} users: {users}")
            for user in users:
                prefs_json = client.hget(prefs_key, user)
                prefs = json.loads(prefs_json)
                print(f"\n👤 {user}:")
                for pref in prefs:
                    print(f"   • {pref.get('insight', 'N/A')}")
        else:
            print(f"⚠️  Preferences key not found: {prefs_key}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_conversation_storage()
