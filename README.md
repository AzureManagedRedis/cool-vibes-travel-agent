# Travel Chat Agent with Azure Managed Redis

A sample Travel Chat Agent built with Microsoft Agent Framework, Azure OpenAI, and Azure Managed Redis demonstrating intelligent conversation management with persistent memory and semantic preference retrieval.

This sample was fully "vibe coded" using GitHub Copilot Agent. All specifications and prompts available in the [specs_and_prompts](./specs_and_prompts) folder.

## Features

- **Intelligent Travel Agent**: Single unified agent handling destination research, weather, flights, accommodations, and sports event booking
- **Persistent Conversation History**: All conversations stored in Azure Managed Redis and persist across sessions using Agent Framework's RedisChatMessageStore
- **Automatic Context Injection**: RedisProvider automatically injects relevant user preferences into each conversation using semantic search
- **Semantic Preference Retrieval**: Vector-based preference storage with semantic search capabilities powered by RediSearch
- **Per-User Context**: Each user has their own RedisProvider instance with preference storage
- **DevUI Integration**: Interactive testing interface with multi-user support

## Quick Start

Choose your deployment method:

### Option 1: Deploy to Azure

Deploy the entire application with all required Azure resources automatically provisioned:

**Prerequisites:**
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- Azure subscription with appropriate permissions
- Python 3.10 or higher

**Steps:**

1. **Clone the repository**
```powershell
git clone https://github.com/AzureManagedRedis/cool-vibes-travel-agent.git
cd cool-vibes-travel-agent
```

2. **Login to Azure**
```powershell
azd auth login
```

3. **Deploy everything with one command**
```powershell
azd up
```

This will automatically provision:
- Azure Managed Redis instance (with RediSearch module)
- Azure OpenAI service with required deployments (GPT-4o, text-embedding-3-small)
- Azure Container Apps for hosting the agent
- Application Insights for observability
- All necessary networking and security configurations

4. **Access your deployed application**

After deployment completes, `azd` will output the application URL. Open it in your browser to interact with the travel agent.

**Changing deployment settings:**
```powershell
# Change Azure region
azd env set AZURE_LOCATION eastus

# Set environment name
azd up -e production

# View all environment variables
azd env get-values
```

### Option 2: Run Locally (Development)

Run the application locally with your own Azure resources:

**Prerequisites:**
- Python 3.10 or higher
- Azure Managed Redis instance (with RediSearch module enabled)
- Azure OpenAI deployment with:
  - GPT-4o or GPT-4 model deployment
  - text-embedding-3-small or text-embedding-ada-002 deployment
- Valid Azure credentials

**Steps:**

1. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

2. **Configure Environment**

Copy `.env.example` to `.env` and fill in your credentials:

```
REDIS_URL=redis://:your_password@your-redis-instance.redis.cache.windows.net:6380?ssl=True
AZURE_OPENAI_ENDPOINT=https://your-openai-instance.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_EMBEDDING_API_VERSION=2023-05-15
```

3. **Run the Application**
```powershell
python main.py
```

4. **Access DevUI**

Open your browser to `http://localhost:8000` to interact with the agent.

## Project Structure

```
cool-vibes-travel-agent.vNext
├── agents/
│   └── travel_agent.py              # Travel agent definition and instructions
├── tools/
│   ├── user_tools.py                # User preference tools (remember, search, reseed)
│   ├── user_tools_enhanced.py       # Reference implementation with improvements
│   ├── travel_tools.py              # Travel research tools
│   └── sports_tools.py              # Sports event tools
├── data/
│   ├── sample_sport_events.py       # Sports event sample data
│   └── sample_sport_venues.py       # Venue seating sample data
├── specs_and_prompts/               # Specifications and prompts used to vibe code
│   ├── prompts to vibe code/
│   │   └── Prompts.md               # Prompts for GitHub Copilot Agent
│   ├── specs/                       # Feature specifications
│   │   ├── Agents_And_Tools.md
│   │   ├── Feature1-AgentsAndTools.md
│   │   ├── Feature2-SeedingPreferences.md
│   │   ├── Feature3-CachingConversations.md
│   │   ├── Feature4-DynamicPreferences.md
│   │   ├── RedisProvider.md         # RedisProvider implementation spec
│   │   └── RedisProvider2.md        # RedisProvider deep dive
│   └── Implementation_Plan_Context_Updates.md  # Context update strategies
├── seed.json                        # User preferences seed data
├── seeding.py                       # RedisProvider context seeding
├── redis_provider.py                # RedisProvider and vectorizer configuration
├── context_manager.py               # Programmatic context management utility
├── conversation_storage.py          # Redis conversation persistence
├── main.py                          # Application entry point
├── azure.yaml                       # Azure Developer CLI configuration
└── requirements.txt                 # Python dependencies
```

## Usage Examples

### Example 1: User with stored preferences (Automatic Context Injection)
```
User: Hi, I'm Mark. Can you help me plan a trip?
Agent: [RedisProvider automatically injects Mark's preferences via semantic search]
      Hello Mark! I'd be happy to help. I see you enjoy boutique hotels 
      and professional sports events...
```

Note: Preferences are automatically injected by RedisProvider - no explicit tool call needed!

### Example 2: Sports event booking
```
User: I'm traveling to New York in November and want to catch a basketball game
Agent: I found several NBA games in November! The Knicks vs Lakers on 
      November 15th at Madison Square Garden. Based on your preferences 
      for boutique experiences, I recommend premium seating...
```

### Example 3: Dynamic preference learning (Direct Context Update)
```
User: I also prefer aisle seats on flights. Please remember that.
Agent: [Calls remember_preference tool to write directly to RedisProvider's context store]
      ✅ I'll remember that Mark prefers aisle seats on flights
```

The preference is immediately stored with vector embedding in the Context namespace and will be automatically retrieved in future conversations.

### Example 4: Semantic preference retrieval
```
User: What do you know about my hotel preferences?
Agent: [Uses get_semantic_preferences with query "hotels"]
      Based on what I know, you enjoy boutique hotels with unique character
      and prefer staying in walkable neighborhoods...
```

## Architecture

### Agent
**Travel-Agent (Unified)**
- Destination research
- Weather information
- Flight and accommodation search (uses sample data)
- Sports event booking (uses sample data)
- General travel assistance
- Preference learning and retrieval

### Tools

**User Preference Tools:**
- `remember_preference` - Learn and store new preferences directly to RedisProvider's context store with embeddings
- `get_semantic_preferences` - Perform targeted semantic search for specific preference topics

Note: General preferences are automatically injected by RedisProvider - no explicit tool call needed for basic retrieval!

**Travel Tools:**
- `research_weather` - Get weather information
- `research_destination` - Destination attractions and culture
- `find_flights` - Flight options (uses sample data)
- `find_accommodation` - Hotel recommendations (uses sample data)
- `booking_assistance` - General booking support (uses sample data)

**Sports Tools:**
- `find_events` - Search professional sports events (uses sample data)
- `make_purchase` - Book tickets (simulated)

## Redis Memory Storage

### Conversation History
All conversations are automatically persisted to Redis using Agent Framework's `RedisChatMessageStore` under the namespace `cool-vibes-agent-vnext:Conversations:`. Each conversation thread stores:
- All messages (user and assistant)
- Message timestamps
- Agent information
- Complete conversation context

**Benefits**:
- Conversations persist across application restarts
- Users can resume previous conversations
- Full conversation history available for analysis
- Thread isolation per user (`thread_id="{user_name}"`)
- Automatic cleanup via `max_messages` configuration

### User Context with RedisProvider

User preferences are stored with vector embeddings in Redis under the namespace `cool-vibes-agent-vnext:Context:{user_name}:{doc_id}` using **agent-framework-redis RedisProvider**.

**Storage structure** (Redis Hash):
- `content`: Text content of the preference
- `embedding`: 1536-dimensional vector (text-embedding-3-small, stored as bytes)
- `role`: "user" (indicates user-provided context)
- `user_id`: User identifier (e.g., "Mark", "Shruti")
- `agent_id`: Agent identifier (e.g., "agent_mark")
- `application_id`: "cool-vibes-travel-agent-vnext"
- `timestamp`: ISO format timestamp
- `source`: "seed" (initial data) or "learned" (from conversation)
- `mime_type`: "text/plain"

**RedisProvider Capabilities**:
- **Automatic Context Injection**: Relevant preferences are automatically retrieved and injected into each conversation
- **Semantic Search**: Uses RediSearch HNSW vector similarity with cosine distance metric
- **Per-User Isolation**: Each user has their own context namespace and RedisProvider instance
- **Thread Awareness**: Can scope context to specific conversation threads if needed
- **Index Management**: Automatically creates and manages RediSearch index `user_preferences_ctx_vnext`

**Three Ways to Update Context**:

1. **Automatic Extraction** (Passive)
   - Happens naturally during conversation
   - Provider may extract preferences automatically
   - No explicit code needed

2. **Tool-Based Direct Write** (Active - Primary Method)
   - Use `remember_preference` tool to explicitly store preferences
   - Writes directly to Context namespace in RedisProvider format
   - Immediate storage with vector embedding
   - Example: "Please remember that I prefer luxury hotels"

3. **Programmatic Update** (System)
   - Use `ContextManager` class for bulk/system operations
   - Useful for migrations, batch imports, system-initiated updates
   - See `context_manager.py` for implementation

**Example Flow**:
```
User: "What hotels does Mark like?"
→ RedisProvider performs semantic search on Context:{Mark}:* keys
→ Finds: "Likes boutique hotels" (via vector similarity, even without exact match)
→ Automatically injects relevant preferences into conversation context
→ Agent responds with personalized recommendations
```

**RediSearch Index**:
- Index name: `user_preferences_ctx_vnext`
- Prefix: `cool-vibes-agent-vnext:Context:`
- Vector field: `embedding` (HNSW algorithm, cosine distance, 1536 dimensions)
- Filterable by: `user_id`, `agent_id`, `application_id`

**Verification**: 
```powershell
# Check stored context
redis-cli KEYS "cool-vibes-agent-vnext:Context:*"

# View index info
redis-cli FT.INFO user_preferences_ctx_vnext

# Check conversations
redis-cli KEYS "cool-vibes-agent-vnext:Conversations:*"
```

## Testing in Redis Insight

1. **Connect** to your Azure Managed Redis instance

2. **Look for these key patterns:**
   - `cool-vibes-agent-vnext:Context:*` - User context/preferences (RedisProvider)
   - `cool-vibes-agent-vnext:Conversations:*` - Conversation history (RedisChatMessageStore)

3. **Inspect user context:**
   ```
   HGETALL cool-vibes-agent-vnext:Context:Mark:abc123
   ```
   Each key is a hash with:
   - `content`: Preference text
   - `embedding`: 1536-dimensional vector (binary bytes)
   - `user_id`: User name
   - `agent_id`: Agent identifier
   - `application_id`: App identifier
   - `timestamp`: When stored
   - `source`: "seed" or "learned"
   - `role`: "user"
   - `mime_type`: "text/plain"

4. **Inspect conversation threads:**
   ```
   LRANGE cool-vibes-agent-vnext:Conversations:Mark 0 -1
   ```
   Each entry contains:
   - Complete message history
   - User and assistant messages
   - Timestamps and metadata
   - Thread isolation per user

5. **Run RediSearch queries:**
   ```
   # View all indexed context
   FT.SEARCH user_preferences_ctx_vnext "*"
   
   # View index details
   FT.INFO user_preferences_ctx_vnext
   
   # Search by user
   FT.SEARCH user_preferences_ctx_vnext "@user_id:{Mark}"
   
   # Vector similarity search (manual)
   FT.SEARCH user_preferences_ctx_vnext "*=>[KNN 5 @embedding $vec]" \
     PARAMS 2 vec <embedding_blob> DIALECT 2
   ```

6. **Verify Context Seeding:**
   - After startup, check that Context keys exist for each user from seed.json
   - Each user should have multiple context entries
   - All entries should have valid embeddings

7. **Test Dynamic Learning:**
   - Use DevUI to say "Please remember that I prefer window seats"
   - Check that new Context key is created with `source=learned`
   - Verify embedding exists and is correct dimension

## Notes

- Sports event data and ticket purchases are simulated with sample data
- This is a demonstration application showcasing Agent Framework capabilities
- RediSearch module required for vector similarity search
- In production, tools would connect to real travel and event APIs

## Troubleshooting

**Redis Connection Error:**
- Verify your REDIS_URL is correct
- Check firewall rules allow your IP
- Ensure SSL is enabled in connection string
- For Azure deployment: Resources are auto-configured by `azd up`

**Azure OpenAI Error:**
- Verify endpoint and API key are correct
- Check your deployment name matches
- Ensure you have quota available
- For rate limits: Consider implementing retry logic or increasing quota
- In case Agent Framework shows API invalid, please make sure your env file states AZURE_OPENAI_API_VERSION=preview

**Vector Search Not Working:**
- Ensure RediSearch module is enabled in your Redis instance
- Check embedding deployment is configured correctly
- Verify `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` environment variable
- Azure Managed Redis Enterprise tier required for RediSearch
- Verify index exists: `redis-cli FT.INFO user_preferences_ctx_vnext`
- Check that Context keys have embeddings: `redis-cli HKEYS cool-vibes-agent-vnext:Context:Mark:*`

**Context Not Being Injected:**
- Verify RedisProvider was created successfully (check logs)
- Ensure seed data was loaded properly on startup
- Check that Context keys exist in Redis
- Verify vectorizer is properly initialized
- Test with `get_semantic_preferences` tool to verify search works

**Import Errors:**
- Run `pip install --upgrade -r requirements.txt`
- Ensure Python 3.10+ is being used
- Check virtual environment is activated

**AZD Deployment Issues:**
- Run `azd auth login` to ensure you're authenticated
- Check you have permissions in the target subscription
- Verify the selected Azure region supports all required services
- Use `azd env get-values` to inspect environment configuration

## Credits
 - Jan Kalis, specfications, prompts and vibe coding
 - Jason Wang, AZD configuration

## License

MIT License - Sample/Demo Application
