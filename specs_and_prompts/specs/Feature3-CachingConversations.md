# Feature 3: Redis Conversation History Storage

## Overview
Implement conversation history persistence using Azure Managed Redis to store all chat messages and conversation threads. This feature will enable the Travel Chat Agent to maintain conversation continuity across sessions and provide context-aware responses based on previous interactions.

## Requirements

### 1. Redis Conversation Storage
- **Redis Key**: Use `cool-vibes-agent:Conversations` as the namespace for storing conversation data
- Store conversation threads with their associated chat message history
- Implement using Agent Framework's Redis conversation patterns as demonstrated in the reference sample
- Reference: https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_conversation.py

### 2. Message Storage Structure
- Store each conversation as a separate thread
- Each thread should contain:
  - Thread ID (unique identifier)
  - User identifier
  - Timestamp of conversation start
  - List of messages with:
    - Message content
    - Role (user/assistant/system)
    - Timestamp
    - Agent name (if applicable)

### 3. Conversation Continuity
- Enable users to resume previous conversations
- Maintain context across multiple sessions
- Support concurrent conversations for different users
- Preserve conversation history for analysis and debugging

### 4. Integration with Agent Framework
- Use Agent Framework's ChatMessageStore backed by Redis
- Implement Thread management for organizing conversations
- Ensure compatibility with DevUI for conversation viewing
- Follow Agent Framework patterns for context providers

### 5. Redis Key Organization
- Primary namespace: `cool-vibes-agent:Conversations`
- Thread keys: `cool-vibes-agent:Conversations:thread:{thread_id}`
- Message keys: `cool-vibes-agent:Conversations:thread:{thread_id}:messages`
- User conversation index: `cool-vibes-agent:Conversations:user:{user_name}:threads`

### 6. Data Persistence Requirements
- All messages must be persisted to Redis immediately after being sent/received
- Conversations should persist across application restarts
- Support for retrieving conversation history by thread ID
- Support for retrieving all conversations for a specific user

## Implementation Considerations

### Agent Framework Integration
- Follow the patterns from `redis_conversation.py` sample
- Use the Agent Framework's built-in Redis context provider
- Implement ChatMessageStore with Redis backend
- Use Thread objects to organize conversations

### Configuration
- Redis connection should use the existing `REDIS_URL` from `.env`
- Conversation storage should be initialized on application startup
- No additional configuration needed beyond existing Redis setup

### Message Format
Store messages in a structured format:
```json
{
  "thread_id": "unique-thread-id",
  "user_name": "Mark",
  "created_at": "2025-11-11T10:30:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Hi, I'm Mark. Can you help me plan a trip?",
      "timestamp": "2025-11-11T10:30:05Z"
    },
    {
      "role": "assistant",
      "content": "Hello Mark! I'd be happy to help...",
      "timestamp": "2025-11-11T10:30:08Z",
      "agent": "travel-agent"
    }
  ]
}
```

### Thread Management
- Create a new thread for each conversation session
- Support thread retrieval by ID
- Support listing all threads for a user
- Enable thread continuation (resume conversation)

## Success Criteria

1. ✅ Conversations are stored in Redis under `cool-vibes-agent:Conversations` namespace
2. ✅ All messages persist across application restarts
3. ✅ Users can resume previous conversations
4. ✅ Multiple concurrent users can have separate conversation threads
5. ✅ Conversation history is visible in Redis Insight under the correct key structure
6. ✅ Integration with Agent Framework's context provider system
7. ✅ DevUI displays conversation history correctly
8. ✅ No data loss during conversation flow

## Usage Example

### First Conversation
```
User: "Hi, I'm Mark. I want to plan a trip to New York."
Agent: [Creates new thread, stores message in Redis]
       [Retrieves Mark's preferences from cool-vibes-agent:Preferences]
       "Hello Mark! I see you enjoy boutique hotels and professional sports..."
       [Stores agent response in Redis]
```

### Resuming Conversation (Same Session)
```
User: "What's the weather like there?"
Agent: [Continues same thread, stores message]
       [Has full conversation context from Redis]
       "Let me check the weather for New York..."
       [Stores response]
```

### New Session (Later)
```
User: "Show me my previous conversations"
Agent: [Retrieves threads for user from Redis]
       "You have 3 previous conversations:
        1. Trip to New York (2025-11-11)
        2. Chicago sports events (2025-11-10)
        3. Miami vacation planning (2025-11-08)"
```

## Error Handling
- Gracefully handle Redis connection failures
- Provide fallback to in-memory storage if Redis is unavailable
- Log all conversation storage errors
- Ensure message delivery even if storage temporarily fails

## Verification in Redis Insight
After implementing this feature, developers should be able to:
1. Open Redis Insight
2. Navigate to the Redis instance
3. See keys under `cool-vibes-agent:Conversations` namespace
4. Inspect individual conversation threads
5. View message history in structured format
6. Verify thread metadata (user, timestamps, etc.)

## Performance Considerations
- Use Redis pipelining for batch message writes
- Implement message pagination for long conversations
- Consider TTL (Time To Live) for old conversations if needed
- Optimize thread list queries for users with many conversations

## Security Considerations
- Ensure conversation data is properly isolated per user
- Do not expose other users' conversations
- Consider encryption for sensitive conversation content
- Follow Redis security best practices (authentication, SSL/TLS)

## Related Files
- `main.py` - Initialize conversation storage on startup
- Agent Framework Redis samples - Reference implementation patterns
- `.env` - Redis connection configuration (already configured)

## Notes
- This feature focuses on conversation persistence, not real-time synchronization
- The implementation should be simple and follow Agent Framework patterns
- Use the Agent Framework's built-in context provider system rather than custom implementation
- This is a demonstration feature showcasing Redis conversation storage capabilities
- In production, consider implementing conversation search and analytics features
