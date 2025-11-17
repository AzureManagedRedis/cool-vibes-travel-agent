# Migration Plan: From Custom redisvl to RedisProvider

## Overview
Migrate the current custom redisvl implementation to use `RedisProvider` from `agent-framework-redis` for automatic context injection and better integration with the Agent Framework.

## Reference Implementation
- **Sample Code**: https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_conversation.py
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
- **Built-in vectorization**: Uses `OpenAITextVectorizer` from redisvl with caching
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

## Implementation Plan

### Phase 1: Core Infrastructure Changes

#### Step 1: Create RedisProvider Module
**File**: Create new `redis_provider.py`

**Requirements**:
Create a new module that provides factory functions for creating RedisProvider instances and vectorizers.

**Implementation Instructions**:
1. **Import necessary components**:
   - Import `RedisProvider` from `agent_framework_redis._provider`
   - Import `OpenAITextVectorizer` from `redisvl.utils.vectorize`
   - Import `EmbeddingsCache` from `redisvl.extensions.cache.embeddings`
   - Import standard libraries: os, logging

2. **Create main factory function**: `create_redis_provider(user_name, thread_id, redis_url)`
   - Takes user identifier, thread identifier, and Redis connection URL as parameters
   - Returns configured RedisProvider instance
   - Should create vectorizer internally using helper function
   - Configure RedisProvider with these settings:
     - Index name: "user_preferences_ctx"
     - Prefix: "cool-vibes-agent:Context"
     - Application ID: "cool-vibes-travel-agent"
     - Agent ID: "travel-agent"
     - User ID: from parameter
     - Vector field name: "embedding"
     - Vector algorithm: "hnsw"
     - Distance metric: "cosine"
     - Thread ID: from parameter

3. **Create vectorizer factory function**: `create_vectorizer()`
   - Returns OpenAITextVectorizer configured for Azure OpenAI
   - Read embedding model from environment variable `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`
   - Default to "text-embedding-3-small" if not set
   - Configure API settings for Azure:
     - API key from `AZURE_OPENAI_API_KEY`
     - API base/endpoint from `AZURE_OPENAI_ENDPOINT`
     - API type: "azure"
     - API version from `AZURE_OPENAI_EMBEDDING_API_VERSION` (default: "2024-02-15-preview")
   - Optionally add EmbeddingsCache for performance:
     - Cache name: "openai_embeddings_cache"
     - Redis URL from environment

4. **Add logging**:
   - Log when provider is created
   - Log vectorizer configuration details
   - Use module-level logger

**Validation Point**: After creating this file, validate:
- [ ] File imports successfully without errors
- [ ] Can create provider instance with test parameters
- [ ] Vectorizer initializes correctly with Azure OpenAI config
- [ ] Provider connects to Redis successfully
- **User Review Required**: Review the module structure before proceeding

---

#### Step 2: Update Vectorizer Usage (Keep Backward Compatibility)
**File**: Keep existing `context_provider.py`

**Decision**: Keep the old file for backward compatibility during transition

**Instructions**:
1. **Do NOT delete** the existing `context_provider.py` file
2. **Do NOT modify** the existing `AzureOpenAIVectorizer` class
3. **Do NOT change** existing `store_preference()` and `retrieve_preferences()` functions
4. These will remain as fallback during migration and for explicit tool usage
5. Mark file with comment indicating it's being phased out but kept for compatibility

**Rationale**: This allows incremental migration without breaking existing functionality

---

#### Step 3: Update Seeding Logic
**File**: `seeding.py`

**Current Behavior**:
- Uses `store_preference()` from `context_provider.py`
- Creates embeddings and stores in SearchIndex
- Key format: `cool-vibes-agent:UserPref:{user_name}:{uuid}`

**Target Behavior**:
- Use RedisProvider to store preferences
- Provider handles embedding and storage automatically
- Change key prefix to match provider pattern
- Maintain user attribution

**Implementation Instructions**:
1. **Add new import** for redis_provider module
   - Import `create_redis_provider` and `create_vectorizer` from new module

2. **Keep existing function** `seed_user_preferences_with_vectors()` but modify implementation:
   - Load seed data from `seed.json` file
   - For each user in the seed data:
     - Create a RedisProvider instance for that user
     - Use thread_id pattern: `seed_{user_name}`
     - For each insight/preference in user's data:
       - Use provider's method to add context (verify exact API method name from RedisProvider documentation)
       - Pass insight text as content
       - Include metadata: user name, source="seed", timestamp
   - Log progress for each user

3. **Note**: Research the exact API method for adding context to RedisProvider
   - Check if it's `add_context()`, `store()`, or another method
   - Refer to agent-framework-redis documentation
   - May need to await if method is async

4. **Maintain existing error handling**:
   - Wrap in try-except blocks
   - Log errors clearly
   - Continue seeding other users if one fails

**Validation Point**: After updating seeding:
- [ ] Run seeding script and verify no errors
- [ ] Check Redis using redis-cli or Redis Insight
- [ ] Verify keys exist with pattern: `cool-vibes-agent:Context:*`
- [ ] Check vector index was created properly
- [ ] Confirm data structure matches provider format
- **User Review Required**: Test seeding with sample data before proceeding

---

### Phase 2: Agent Integration

#### Step 4: Integrate RedisProvider in main.py
**File**: `main.py`

**Current State** (around lines 180-195):
Agent is created without context_providers parameter

**Target State**:
Agent is created WITH context_providers parameter, enabling automatic context injection

**Implementation Instructions**:
1. **Add import** at top of file:
   - Import `create_redis_provider` from redis_provider module

2. **Create provider instance** before agent creation:
   - Add section with logging: "Creating Redis context provider..."
   - Wrap in try-except for graceful degradation
   - For now, use a default/placeholder user: "default_user"
   - Generate or use thread_id: "main_thread" (or generate unique ID)
   - Pass redis_url from configuration
   - Log success or warning if fails
   - Set provider to None if exception occurs

3. **Modify agent creation call**:
   - Locate the `responses_client.create_agent()` call
   - Add parameter: `context_providers=context_provider`
   - This enables automatic context injection

4. **Add comment/TODO** about user context:
   - Note that using default user for now
   - Document that proper multi-user support needs user extraction from conversation
   - Reference the three approaches documented in this plan

**Challenge: User Context Management**
The provider is created per user, but users identify themselves during conversation.

**Approach Options**:
- **Option A (Implement This)**: Default User Approach
  - Create single provider with "default_user"
  - All preferences stored under this user
  - Simplest for demo purposes
  - Accept that multi-user isolation won't work perfectly
  - Document limitation in comments

- **Option B (Future Enhancement)**: Dynamic Provider Switching
  - Extract user name from conversation history
  - Recreate provider when user changes detected
  - More complex but proper isolation

- **Option C (Future Enhancement)**: Thread-based User Detection
  - Use middleware/hooks to detect user name
  - Create new provider instance per user
  - Store provider in session/thread context

**Decision**: Start with Option A, document B and C as future enhancements

**Validation Point**: After integration:
- [ ] Application starts without errors
- [ ] DevUI loads successfully
- [ ] Can send test message to agent
- [ ] Check logs confirm context provider initialized
- [ ] No exceptions during agent creation
- **User Review Required**: Test agent creation before proceeding to tool changes

---

#### Step 5: Update user_tools.py
**File**: `tools/user_tools.py`

**Changes Required**:

**A. KEEP get_semantic_preferences() tool**
- **Do NOT remove** this tool
- Tool provides explicit search capability when agent needs targeted preference lookup
- Works alongside automatic context injection
- Complements rather than replaces automatic context

**Update Instructions**:
- Keep function signature and decorator unchanged
- Keep function description
- May optionally update implementation to use provider's search API
- Alternative: Keep current implementation using SearchIndex
- Add comment explaining it works alongside automatic context

**B. Update remember_preference() tool**

**Current**: Uses `context_provider.store_preference()` from old module

**Target**: Use RedisProvider to store preferences

**Implementation Instructions**:
1. **Update function signature**:
   - Make function async (add `async def`)
   - Keep same parameters and return type

2. **Update implementation logic**:
   - Check if global _provider is set
   - Return error message if not initialized
   - Use provider's method to add/store context
   - Pass preference text as content
   - Include metadata: user ID from provider, source="learned", timestamp
   - Handle exceptions and return user-friendly error messages
   - Log success with preference preview

3. **Research provider API**:
   - Verify exact method name for storing context
   - Check if async or sync
   - Confirm parameter structure

**C. Add set_provider() function**

**Instructions**:
- Add module-level variable: `_provider = None`
- Create setter function: `set_provider(provider)`
- Use global keyword to modify module variable
- Add docstring explaining purpose
- Follow pattern of existing `set_redis_client()`, `set_search_index()`, etc.

**D. Update module initialization section**:
- Add `_provider` to the module-level variables at top
- Initialize to None
- Document what it's used for

**Validation Point**: After tool updates:
- [ ] File compiles without syntax errors
- [ ] All imports resolve correctly
- [ ] Test `remember_preference()` with sample data
- [ ] Verify new preference stored in Redis
- [ ] Check Redis keys to confirm format
- [ ] Test that tool can be called from agent
- **User Review Required**: Test tool functionality before final changes

---

#### Step 6: Update Agent Instructions
**File**: `agents/travel_agent.py`

**Current Instructions**:
May reference `get_semantic_preferences` tool in instructions

**Target Instructions**:
Update to explain both automatic context AND explicit search tool

**Implementation Instructions**:
1. **Update capabilities section**:
   - Explain that relevant user preferences are AUTOMATICALLY provided in context
   - Note that agent should check this automatic context FIRST
   - Explain `get_semantic_preferences()` is available for TARGETED searches when needed
   - Keep `remember_preference()` for storing new preferences

2. **Add user context section**:
   - Explain preferences are automatically available
   - Note when to use explicit search (specific queries, need to search specific terms)
   - Clarify that explicit search is optional, not required
   - Explain automatic context is passive, tool search is active

3. **Update workflow guidance**:
   - Check automatic context first
   - Use `get_semantic_preferences()` for specific searches if needed
   - Use `remember_preference()` when users share new preferences
   - Personalize based on provided context

4. **Keep communication style guidance**:
   - Warm, enthusiastic, helpful
   - Personalize based on context
   - Ask clarifying questions

5. **Add note about user identification**:
   - Users identify themselves by stating name
   - Example: "Hi, I'm Mark"

**Key Message**: Agent has BOTH automatic context (always present) AND explicit search tool (use when needed)

**Validation Point**: After instruction updates:
- [ ] Agent understands dual retrieval model
- [ ] Test with query: "What do I like?" (should use automatic context)
- [ ] Test with query: "Search for my beach preferences" (might use tool)
- [ ] Verify agent personalizes responses
- [ ] Check that agent doesn't over-use explicit search tool
- **User Review Required**: Test agent behavior with updated instructions

---

### Phase 3: Testing & Validation

#### Step 7: Comprehensive Testing

**Test Suite**:

**Test 1: Seeding and Storage**
- **Action**: Run seeding script from command line or startup
- **Expected**: Preferences stored with vector embeddings using RedisProvider format
- **Validation**:
  - [ ] Use redis-cli or Redis Insight to check keys matching `cool-vibes-agent:Context:*`
  - [ ] Verify vector index exists (check index info)
  - [ ] Confirm data structure matches provider's expected format
  - [ ] Check that embeddings are present in stored data

**Test 2: Automatic Context Retrieval**
- **Query**: "Hi, I'm Mark. Where should I travel?"
- **Expected**: Agent mentions Mark's preferences (boutique hotels, beaches, water sports) without calling get_semantic_preferences tool
- **Validation**:
  - [ ] Response includes personalized recommendations
  - [ ] Check logs show NO call to get_semantic_preferences
  - [ ] Check logs show context was automatically injected
  - [ ] Response is relevant to Mark's seeded preferences

**Test 3: Explicit Tool Search**
- **Query**: "Search for any preferences I have about luxury accommodations"
- **Expected**: Agent calls get_semantic_preferences tool explicitly
- **Validation**:
  - [ ] Check logs confirm tool was called
  - [ ] Tool returns relevant preferences
  - [ ] Agent uses results in response
  - [ ] Both automatic and explicit context work together

**Test 4: Learning New Preferences**
- **Query**: "Remember that I love Italian cuisine"
- **Expected**: remember_preference tool called, preference stored
- **Follow-up Query**: "What food should I try in Rome?"
- **Expected**: Agent mentions Italian cuisine preference
- **Validation**:
  - [ ] remember_preference executes without errors
  - [ ] Check Redis shows new key stored
  - [ ] Verify format matches provider pattern
  - [ ] Subsequent queries retrieve and use the learned preference

**Test 5: User Attribution (If Multi-User Implemented)**
- **Query 1**: "Hi, I'm Shruti. What's good for families?"
- **Expected**: Shruti's preferences (family-friendly, cultural)
- **Query 2**: "Hi, I'm Mark. Where should I go?"
- **Expected**: Mark's different preferences (beaches, water sports)
- **Validation**:
  - [ ] Correct user context loaded for each
  - [ ] Preferences don't cross-contaminate
  - [ ] Each user gets personalized results
  - **Note**: May not work perfectly with default_user approach

**Test 6: Reseed Functionality**
- **Action**: Call reseed_user_preferences tool
- **Expected**: Old data deleted, fresh seed loaded
- **Validation**:
  - [ ] Old keys removed from Redis
  - [ ] Index recreated properly
  - [ ] Fresh preferences loaded
  - [ ] Vector search works on new data

**Test 7: Edge Cases**
- **Scenario**: Unknown user (no seeded data)
  - **Expected**: Agent still responds, just without personalized context
- **Scenario**: Empty preferences
  - **Expected**: No errors, generic recommendations
- **Scenario**: Very long preference text
  - **Expected**: Handles gracefully, stores correctly
- **Scenario**: Special characters in preferences
  - **Expected**: No encoding issues, stores and retrieves correctly

**Validation Point**: After each test:
- **User Review Required**: Review test results before marking complete
- Document any issues, unexpected behavior, or failures
- Adjust implementation if tests fail
- Re-test after fixes

---

#### Step 8: Performance and Monitoring

**Metrics to Check**:
- [ ] Response time for queries WITH automatic context
- [ ] Response time for queries WITHOUT context (baseline)
- [ ] Redis memory usage (before and after seeding)
- [ ] Vector search latency (check provider logs if available)
- [ ] Cache hit rate (if using EmbeddingsCache)
- [ ] Number of preferences retrieved per query

**Logging to Add/Check**:
- [ ] Context retrieval events (when provider injects context)
- [ ] Preference storage events (when remember_preference called)
- [ ] Vector search queries (if explicit tool used)
- [ ] Errors and warnings related to provider
- [ ] Provider initialization success/failure

**Performance Targets**:
- Total response time: < 2 seconds
- Context injection overhead: < 500ms
- Memory usage: Reasonable for dataset size

**Validation Point**:
- **User Review Required**: Review performance metrics
- Identify any bottlenecks
- Optimize if needed:
  - Adjust top_k in provider settings
  - Enable/tune caching
  - Adjust distance thresholds
  - Reduce embedding dimensions if needed

---

### Phase 4: Cleanup and Documentation

#### Step 9: Code Cleanup

**Decisions to Make**:

**1. context_provider.py file**:
- **Recommendation**: Keep for now as backup and for explicit tool usage
- Mark with deprecation notice in comments
- Document that it's kept for backward compatibility
- May remove in future version after full validation
- **User Decision Required**: Confirm keeping or removing

**2. Old tool code**:
- **get_semantic_preferences()**: KEEP (still useful for explicit searches)
- **Old AzureOpenAIVectorizer class**: Keep in context_provider.py
- **store_preference() and retrieve_preferences()**: Keep for explicit tool
- **User Decision Required**: Confirm approach

**3. Environment variables**:
- No new variables required
- Uses same Azure OpenAI configuration
- Document that existing vars are sufficient
- Optionally add `.env.example` if doesn't exist

**Cleanup Tasks**:
- [ ] Remove any unused imports
- [ ] Remove commented-out code
- [ ] Ensure all functions have docstrings
- [ ] Check for any dead code paths
- [ ] Format code consistently

**Validation Point**:
- [ ] No unused imports remaining
- [ ] No orphaned code
- [ ] All functions properly documented
- [ ] Code follows project style guidelines
- **User Review Required**: Final code review before merging

---

#### Step 10: Documentation Updates

**Files to Update**:

**A. README.md**
- **Update architecture section**:
  - Mention RedisProvider integration for automatic context
  - Explain dual retrieval: automatic + explicit tool
  - Add diagram or explanation of flow
  
- **Update features section**:
  - Highlight automatic preference injection
  - Note that agent doesn't need to explicitly request context
  - Explain when explicit search is useful

- **Update setup instructions if needed**:
  - Ensure all required packages listed
  - Verify environment variables documented
  - Add any new configuration steps

**B. Feature4-DynamicPreferences.md**
- **Mark status**: "Implemented with RedisProvider"
- **Document implementation approach**:
  - Automatic context injection via RedisProvider
  - Explicit search via get_semantic_preferences tool
  - Learning via remember_preference tool
  
- **Note differences from original spec**:
  - Added automatic context injection (improvement)
  - Kept explicit tool (hybrid approach)
  - Document why hybrid approach chosen

- **Add examples**:
  - Show automatic context in action
  - Show explicit tool usage
  - Show learning new preferences

**C. New Documentation**
Create `docs/RedisProvider-Integration.md` (or similar):
- **How RedisProvider works**:
  - Explain automatic context injection
  - Explain vector similarity search
  - Explain storage format and indexing

- **How context is automatically injected**:
  - Provider retrieves relevant preferences automatically
  - Adds to system prompt before agent processes query
  - Agent sees context without calling tools

- **When to use explicit search tool**:
  - Need very specific preference lookup
  - Want to search with particular keywords
  - Need to debug what preferences exist

- **How to add new preferences**:
  - Via remember_preference tool
  - Via seeding script
  - Directly in Redis (advanced)

- **Troubleshooting guide**:
  - Provider not initializing
  - Context not appearing in responses
  - Vector search not working
  - Performance issues

**D. Code Comments**
- **redis_provider.py**: Document each configuration parameter
- **main.py**: Explain why provider is created, what it does
- **user_tools.py**: Explain tool interaction with provider
- **seeding.py**: Document seeding process and format

**E. Optional: Add architectural diagram**
- Show flow: User query → Provider searches Redis → Injects context → Agent responds
- Show dual paths: Automatic + Explicit tool
- Show storage: remember_preference → Provider → Redis

**Validation Point**:
- [ ] All documentation is clear and accurate
- [ ] Examples work as documented
- [ ] New developers can understand architecture
- [ ] Troubleshooting guide covers common issues
- **User Review Required**: Review all documentation updates
- Ensure clarity for other developers who will maintain code

---

## Migration Checklist

### Pre-Migration
- [ ] Review this plan with stakeholders
- [ ] Backup current Redis data
- [ ] Test current functionality as baseline
- [ ] Set up test environment

### Phase 1: Infrastructure
- [ ] Create `redis_provider.py` module with factory functions
- [ ] Keep `context_provider.py` for backward compatibility
- [ ] Update `seeding.py` to use RedisProvider
- [ ] **VALIDATE with user before proceeding**

### Phase 2: Integration
- [ ] Update `main.py` to create and pass RedisProvider to agent
- [ ] Update `user_tools.py` remember_preference to use provider
- [ ] Keep `get_semantic_preferences()` tool for explicit searches
- [ ] Update agent instructions to explain dual retrieval model
- [ ] **VALIDATE with user before proceeding**

### Phase 3: Testing
- [ ] Run all test scenarios documented above
- [ ] Verify both automatic and explicit retrieval work
- [ ] Check performance metrics
- [ ] **VALIDATE with user before proceeding**

### Phase 4: Finalization
- [ ] Clean up code (if approved by user)
- [ ] Update all documentation
- [ ] Final review
- [ ] **GET user sign-off**

---

## Rollback Plan

If issues arise during or after migration:

1. **Quick Rollback**: 
   - Revert `main.py` to NOT pass context_providers parameter
   - Agent continues using old explicit tool-only approach
   - Old `context_provider.py` still works

2. **Data Rollback**: 
   - Restore Redis backup
   - Re-run old seeding if needed

3. **Tool Rollback**: 
   - Revert `user_tools.py` changes
   - Tools continue using old implementations

**Strategy**: Keep all old code in git history for easy reversion

---

## Success Criteria

✅ Agent automatically retrieves relevant preferences without explicit tool calls  
✅ Explicit search tool (`get_semantic_preferences`) still works for targeted queries  
✅ New preferences can be learned via `remember_preference()` tool  
✅ Seeding creates proper vector embeddings using RedisProvider  
✅ Multiple users maintain isolated preferences (if implemented)  
✅ Performance is acceptable (< 2s response time including context injection)  
✅ Code is cleaner and follows framework patterns  
✅ Documentation is complete and accurate  
✅ Both automatic and explicit context retrieval work harmoniously  

---

## Open Questions / Decisions Needed

**Before Starting Implementation, Decide:**

1. **User Context Management**: Which approach?
   - **Option A (Recommended)**: Default user approach - simple, limited isolation
   - **Option B**: Dynamic provider switching - complex, proper isolation
   - **Option C**: Thread-based user detection - middleware approach
   - **Decision**: _____________________

2. **get_semantic_preferences() Tool**: Keep or remove?
   - **Recommendation**: KEEP for explicit search capability
   - **Decision**: KEEP ✓

3. **context_provider.py File**: Keep or remove?
   - **Option A**: Keep for backward compatibility during transition
   - **Option B**: Remove entirely after migration
   - **Recommendation**: Keep during Phase 1-3, decide in Phase 4
   - **Decision**: _____________________

4. **Testing Environment**: Production or separate?
   - Use production Redis instance?
   - Set up separate test Redis?
   - **Decision**: _____________________

5. **Migration Timing**: All at once or incremental?
   - **Option A**: Complete all phases in one session
   - **Option B**: Phase-by-phase with validation between each
   - **Recommendation**: Option B for safer migration
   - **Decision**: _____________________

---

## Implementation Notes

### Key Differences from Original Spec
- **Hybrid Approach**: Combines automatic context injection WITH explicit search tool
- **Simpler Than Expected**: RedisProvider handles most complexity
- **Backward Compatible**: Keeps old tools and patterns during transition

### Critical Success Factors
- RedisProvider API must be researched and correctly used
- Provider configuration must match Azure OpenAI setup
- Testing must verify BOTH automatic and explicit retrieval
- User must validate at each phase before proceeding

### Potential Challenges
- **Provider API Discovery**: Exact method names may differ from assumptions
- **User Context**: Default user approach limits multi-user isolation
- **Performance**: Context injection adds latency - must measure
- **Debugging**: Automatic context less visible than explicit tool calls

### Mitigation Strategies
- Research RedisProvider API documentation thoroughly before implementing
- Add extensive logging to track automatic context injection
- Keep old code as fallback during transition
- Test each component independently before integration

---

## Next Steps

**Immediate Actions**:
1. Review this plan thoroughly
2. Answer all open questions above
3. Get stakeholder approval
4. Backup current Redis data
5. Begin Phase 1: Create `redis_provider.py` module

**Communication**:
- Notify team of migration plan
- Schedule validation sessions after each phase
- Document any deviations from plan
- Report blockers or issues immediately

**Success Tracking**:
- Mark checklist items as complete
- Document test results
- Track performance metrics
- Update this document with lessons learned

---

## Reference Links

- **Agent Framework Redis Package**: https://github.com/microsoft/agent-framework/tree/main/python/packages/agent-framework-redis
- **Sample Implementation**: https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_conversation.py
- **RedisVL Documentation**: https://redisvl.com/
- **Azure OpenAI Embeddings**: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/understand-embeddings

---

**End of Migration Plan**

**Last Updated**: November 16, 2025  
**Status**: Ready for Implementation  
**Approved By**: _____________________ (Awaiting approval)
