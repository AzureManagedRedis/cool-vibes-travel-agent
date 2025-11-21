# Migration Plan: From Custom redisvl to RedisProvider

## Overview
Migrate the current custom redisvl implementation to use `RedisProvider` from `agent-framework-redis` for automatic context injection and better integration with the Agent Framework.

## Reference Implementation
- **Sample Code**: https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_conversation.py

and 

https://github.com/AzureManagedRedis/agent-framework-travel-assistant 

Make sure to use the NATIVE Redis approach, not mem0 and make sure to use Azure Open AI.


- **Package**: `agent-framework-redis`

## Current vs Target State

### Current Implementation (Custom redisvl)
- **Custom vectorizer**: `AzureOpenAIVectorizer` extending `BaseVectorizer`
- **Manual index management**: Using `SearchIndex` from redisvl
- **Manual CRUD operations**: `store_preference()` and `retrieve_preferences()` functions
- **Tool-based retrieval**: `get_semantic_preferences()` tool that agents explicitly call
- **No automatic context injection**: Agent must call tools to get preferences
- **Storage format**: Hash keys with manual embedding serialization
- **File**: `context_provider.py` (193 lines)

### Target Implementation (RedisProvider)
- **Integrated provider**: `RedisProvider` from `agent_framework_redis`
- **Automatic context injection**: Provider automatically adds relevant context to agent prompts
- **Built-in vectorization**: Uses `OpenAITextVectorizer` from redisvl with caching - could it use Azure Open AI too?
- **Seamless integration**: Passed to `create_agent()` as `context_providers` parameter
- **Dual retrieval modes**: Both automatic context injection AND explicit tool-based search
- **New file**: `redis_provider.py`

## Key Architectural Differences

| Aspect | Current (redisvl) | Target (RedisProvider) |
|--------|-------------------|------------------------|
| **Abstraction Level** | Low-level, manual | High-level, automatic |
| **Context Retrieval** | Explicit tool calls only | Automatic + explicit tool option |
| **Integration Point** | Tools in agent | `context_providers` param + tools |
| **Vectorizer** | Custom Azure implementation | redisvl's OpenAITextVectorizer |
| **Storage Pattern** | Custom hash structure | Provider-managed format |
| **Agent Awareness** | Must call tools | Transparent automatic + tool search |

## Benefits of Migration

✅ **Automatic Context**: Relevant preferences injected automatically into prompts  
✅ **Explicit Search Option**: Keep `get_semantic_preferences()` for targeted queries  
✅ **Better Integration**: Uses framework's intended patterns  
✅ **Cleaner Code**: Less manual index management  
✅ **Consistent**: Matches agent-framework examples  
✅ **Maintained**: Leverages framework updates  
✅ **Flexible**: Best of both worlds - automatic + on-demand retrieval