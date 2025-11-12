# Feature 4: Dynamic Context Learning with Redis (Simplified - No Mem0)

## Overview
Implement semantic preference retrieval using Agent Framework's `RedisProvider` to enable the Travel Chat Agent to retrieve user preferences with vector similarity search. This feature demonstrates Redis with RediSearch capabilities **without requiring Mem0 dependency**.

## Simplified Approach (vs Original Spec)
- **No Mem0 dependency** - Use RedisProvider directly with manual seeding
- **Semantic retrieval only** - Agent retrieves preferences via vector search
- **Explicit learning** - Via new "remember_preference" tool (not automatic)
- **Demonstrates Redis RediSearch** - Vector similarity, HNSW, semantic search

## Current State
- **Static Preferences**: Loaded from `seed.json` at startup into `cool-vibes-agent:Preferences` hash
- **No Dynamic Learning**: Agents cannot learn new preferences from conversations
- **No Vector Search**: Preferences are stored as plain JSON without embeddings

## Requirements

### 1. Redis Context Provider Integration
- Use Agent Framework's `RedisProvider` from `agent-framework-redis` package
- Reference implementation: https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_threads.py
- Enable semantic context retrieval with vector embeddings
- Store learned context separately from conversation history

### 2. Vector Embeddings for Preferences
- **Vectorize initial preferences** from `seed.json` on seeding
- Use OpenAI embeddings: `text-embedding-3-small` or `text-embedding-ada-002`
- Store embeddings in Redis with RediSearch index
- Enable semantic similarity search for context retrieval

### 3. Updated Seeding Process
Modify `seeding.py` to:
- Create vector embeddings for each user preference insight
- Store preferences with embeddings in Redis
- Use `RedisProvider` pattern for storage
- Key structure: `cool-vibes-agent:Context:{user_name}:{uuid}`

### 4. Explicit Learning via Tool
- **New tool: `remember_preference(preference: str)`** - Agent calls this to store new preferences
- Preferences stored with embeddings via RedisProvider
- Context provider retrieves relevant preferences semantically during conversations
- Simpler than automatic extraction, showcases Redis capabilities

### 5. User Attribution
- Users identify themselves by stating their name in conversation (e.g., "Hi, I'm Mark")
- Extract user name from conversation context
- Associate learned preferences with the correct user
- No login system required (demo purposes)

### 6. New Tool: reseed_user_preferences
Create a new tool for demo purposes:
```python
def reseed_user_preferences() -> str:
    """
    Delete all existing user preferences and context from Redis, 
    then re-seed from seed.json.
    
    Returns:
        Confirmation message
    """
```

**Purpose**: 
- Allow resetting preferences during demos
- Delete all keys matching `cool-vibes-agent:Context:*`
- Delete RediSearch index
- Re-seed and re-vectorize from `seed.json`
- Available to both agents

## Implementation Details

### RedisProvider Configuration

```python
from agent_framework_redis._provider import RedisProvider
from redisvl.utils.vectorize import OpenAITextVectorizer

# Create vectorizer using existing OpenAI deployment
vectorizer = OpenAITextVectorizer(
    model="text-embedding-3-small",  # or text-embedding-ada-002
    api_config={
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_type": "azure",
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION")
    }
)

# Create provider per user (dynamic based on conversation)
provider = RedisProvider(
    redis_url=os.getenv("REDIS_URL"),
    index_name="user_context",
    prefix="cool-vibes-agent:Context",
    application_id="cool-vibes-travel-agent",
    agent_id="travel-agent",
    user_id=user_name,  # Dynamic from conversation
    redis_vectorizer=vectorizer,
    vector_field_name="embedding",
    vector_algorithm="hnsw",
    vector_distance_metric="cosine",
    thread_id=thread_id
)
```

### Seeding with Vectors

Update `seeding.py`:
```python
def seed_user_preferences_with_vectors(redis_client, vectorizer):
    """Seed preferences with vector embeddings."""
    # Read seed.json
    # For each user and each insight:
    #   - Generate embedding for insight text
    #   - Store in Redis with RedisProvider pattern
    #   - Key: cool-vibes-agent:Context:{user_name}:{uuid}
    #   - Store: text, embedding, metadata (user, timestamp)
```

### Agent Integration

Modify agent creation in `main.py`:
```python
# Create provider
provider = create_context_provider(user_name, thread_id, redis_url)

# Create agent with context provider
travel_agent = responses_client.create_agent(
    name=TRAVEL_AGENT_NAME,
    description=TRAVEL_AGENT_DESCRIPTION,
    instructions=TRAVEL_AGENT_INSTRUCTIONS,
    tools=travel_tools,
    context_providers=provider,  # ← Enables dynamic learning
    chat_message_store_factory=chat_message_store_factory
)
```

### Context Storage Format

```
cool-vibes-agent:Context:Mark:abc123 (Hash)
├── text: "Likes to stay boutique hotels"
├── embedding: [0.123, 0.456, 0.789, ...]  # 1536-dim vector
├── metadata: {"user": "Mark", "timestamp": "2025-11-11T10:30:00Z", "source": "seed"}

cool-vibes-agent:Context:Mark:def456 (Hash)
├── text: "Prefers window seats on flights"
├── embedding: [0.234, 0.567, 0.890, ...]
├── metadata: {"user": "Mark", "timestamp": "2025-11-11T11:45:00Z", "source": "learned"}
```

### RediSearch Index

The provider automatically creates a RediSearch index:
```
Index: user_context
Prefix: cool-vibes-agent:Context:
Fields:
  - text (TEXT)
  - embedding (VECTOR - HNSW, cosine, 1536 dims)
  - metadata (TAG)
```

## User Name Extraction

Since users don't login, extract name from conversation:
1. User says: "Hi, I'm Mark" or "My name is Shruti"
2. Agent extracts user name from message
3. Agent associates context provider with that user
4. All subsequent learned context tagged with user name

**Implementation approach**:
- Add user name extraction logic in main conversation loop
- Update provider's `user_id` when user identifies themselves
- Store mapping: `thread_id → user_name` in memory or Redis

## Environment Variables

Add to `.env`:
```
# For Azure OpenAI Embeddings (reuse existing endpoint)
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

## Dependencies

Ensure these are in `requirements.txt`:
- `agent-framework-redis` (already installed)
- `redisvl` (new - required for vectorizer and context provider)

## Redis Requirements

**Verify Azure Managed Redis has**:
- RediSearch module enabled (required for vector search)
- Redis Stack or Enterprise with RediSearch support
- If not available, feature cannot be implemented

## Tools Update

### Modified Tools
1. **user_preferences** - Now queries `RedisProvider` instead of direct Redis
2. **reseed_user_preferences** (NEW) - Deletes and re-seeds vectorized preferences

### Tool List
Add `reseed_user_preferences` to both agents' tool lists for demo purposes.

## Success Criteria

1. ✅ Initial preferences from `seed.json` are vectorized and stored in Redis
2. ✅ RediSearch index created successfully for `cool-vibes-agent:Context` prefix
3. ✅ Agent learns new preferences from conversations automatically
4. ✅ Context provider retrieves relevant preferences using semantic search
5. ✅ Learned preferences correctly attributed to the right user
6. ✅ `reseed_user_preferences` tool deletes all context and re-seeds from file
7. ✅ Embeddings visible in Redis with proper key structure
8. ✅ DevUI shows agent using learned context in responses
9. ✅ Works with existing conversation persistence (Feature 3)
10. ✅ User can state their name and context is attributed correctly

## Testing Scenarios

### Scenario 1: Initial Seed with Vectors
```
1. Start application
2. Seeding vectorizes all preferences from seed.json
3. Check Redis: keys matching cool-vibes-agent:Context:Mark:*
4. Verify RediSearch index exists: FT.INFO user_context
5. Each preference has text + embedding fields
```

### Scenario 2: Learning from Conversation
```
User: "Hi, I'm Mark. I'm planning a trip to New York"
Agent: [Retrieves Mark's seeded preferences from context provider]
User: "I also prefer aisle seats on flights"
Agent: [Context provider automatically stores this as new preference with embedding]
User: "What are my travel preferences?"
Agent: [Retrieves both seeded and learned preferences via semantic search]
```

### Scenario 3: User Attribution
```
User: "Hi, I'm Shruti. I want to go to Chicago"
Agent: [Extracts user_name="Shruti", loads her context]
User: "I prefer early morning flights"
Agent: [Stores preference under Shruti's context]
```

### Scenario 4: Reseeding
```
1. User: "Please reseed user preferences"
2. Agent calls reseed_user_preferences tool
3. All cool-vibes-agent:Context:* keys deleted
4. RediSearch index dropped and recreated
5. Preferences re-loaded from seed.json with new embeddings
6. Confirmation message shown
```

## Verification in Redis Insight

After implementation:
1. Browse keys: `cool-vibes-agent:Context:*`
2. Each key is a hash with: text, embedding (binary), metadata
3. Run: `FT.SEARCH user_context "*"` to see indexed entries
4. Run: `FT.INFO user_context` to see index details
5. Verify embedding dimension = 1536 (or 1536 for text-embedding-3-small)

## Migration from Current Implementation

**Old (Feature 2)**:
```
cool-vibes-agent:Preferences (Hash)
├── Mark: [{"insight": "..."}, {"insight": "..."}]
```

**New (Feature 4)**:
```
cool-vibes-agent:Context:Mark:uuid1 (Hash)
├── text: "Likes to stay boutique hotels"
├── embedding: [...]
├── metadata: {"user": "Mark", ...}

cool-vibes-agent:Context:Mark:uuid2 (Hash)
├── text: "Likes to explore professional sports"
├── embedding: [...]
├── metadata: {"user": "Mark", ...}
```

**Migration strategy**:
- Keep old structure during development
- Switch to new structure on successful implementation
- Use reseed tool to migrate existing users

## Performance Considerations

- **Seeding time**: ~1-2 seconds per user (embedding API calls)
- **Query latency**: ~50-100ms for vector similarity search
- **Storage**: ~6KB per preference (1536-dim float32 vector)
- **Cost**: Embedding API calls (minimal - only during seeding and learning)

## Error Handling

- Gracefully handle missing RediSearch module (log error, disable feature)
- Handle embedding API failures (retry logic)
- Handle user name extraction failures (prompt user for name)
- Handle provider creation errors (fallback to no context)

## Related Files

- `seeding.py` - Update to vectorize preferences
- `main.py` - Add context provider to agent creation
- `tools/user_tools.py` - Add reseed_user_preferences tool
- `requirements.txt` - Add redisvl
- `.env` - Add embedding deployment name

## Notes

- This feature requires RediSearch module in Azure Managed Redis
- Vector embeddings enable semantic "I like cozy hotels" matches "boutique hotels"
- Context provider automatically persists learned information
- Agent Framework handles the heavy lifting - minimal code needed
- User attribution relies on conversation parsing (acceptable for demo)
- Reseeding tool is for demo convenience, not production use

## Implementation Principles

1. **Use Agent Framework patterns** - Follow redis_threads.py example
2. **Minimal code changes** - Leverage existing framework capabilities
3. **Maintain simplicity** - Keep the demo/sample nature of the application
4. **Demonstrate Redis features** - Showcase RediSearch and vector search
5. **Preserve existing features** - Don't break Features 1-3

## Expected Code Impact

- `seeding.py`: +40 lines (vectorization logic)
- `main.py`: +30 lines (provider setup)
- `tools/user_tools.py`: +25 lines (reseed tool)
- `requirements.txt`: +1 line (redisvl)
- New file `context_provider.py`: ~50 lines (provider factory)
- Total: ~145 new lines

## Why This Showcases Redis Better Than Simple Storage

**Redis + RediSearch Features Demonstrated**:
1. ✅ **Vector similarity search** - Find semantically similar preferences
2. ✅ **RediSearch indexing** - Full-text and vector search capabilities
3. ✅ **HNSW algorithm** - Approximate nearest neighbor search at scale
4. ✅ **Hybrid search** - Combine text and vector queries
5. ✅ **Real-time updates** - Index updates as preferences are learned
6. ✅ **Efficient storage** - Optimized binary vector storage

**vs. File Storage**: Cannot do semantic search, no indexing, no real-time queries, no multi-user concurrent access, no vector similarity, no scalability.

This demonstrates why Redis is chosen for AI/ML workloads with context retrieval.
