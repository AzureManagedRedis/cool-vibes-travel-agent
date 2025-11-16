# Travel Chat Agent with Azure Managed Redis

A sample Travel Chat Agent built with Microsoft Agent Framework, Azure OpenAI, and Azure Managed Redis demonstrating intelligent conversation management with persistent memory and semantic preference retrieval.

This sample was fully "vibe coded" using GitHub Copilot Agent. All specifications and prompts are saves in the spects_and_prompts folder.

## Features

- **Intelligent Travel Agent**: Single unified agent handling destination research, weather, flights, accommodations, and sports event booking
- **Persistent Conversation History**: All conversations stored in Azure Managed Redis and persist across sessions
- **Semantic Preference Retrieval**: Vector-based preference storage with semantic search capabilities
- **Dynamic Learning**: Agent can learn and remember new user preferences by asking it to "Save my preferences" to invoke the remember_pterefence tool. This update the long term store in Redis.
- **DevUI Integration**: Interactive testing interface

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
cool-vibes-travel-agent
├── agents/
│   └── travel_agent.py          # Travel agent definition
├── tools/
│   ├── user_tools.py            # User preference tools
│   ├── travel_tools.py          # Travel research tools
│   └── sports_tools.py          # Sports event tools
├── data/
│   ├── sample_sport_events.py   # Sports event sample data
│   └── sample_sport_venues.py   # Venue seating sample data
├── specs_and_prompts/           # Specifications and propmpts used to vibe code
│   ├── prompts to vibe code/
│   │   └── Prompts.md           # Prompts for GitHub Copilot Agent to vibe code the application code
│   └── specs/                                  # Detailed Copilot generated & human reviewed feature specifications
│       ├── Agents_And_Tools.md                 # Definition of agents and tools
│       ├── Feature1-AgentsAndTools.md          # Agent and tool implementation spec
│       ├── Feature2-SeedingPreferences.md      # Preference seeding spec
│       ├── Feature3-CachingConversations.md    # Conversation persistence spec
│       └── Feature4-DynamicPreferences.md      # Semantic preferences spec
├── seed.json                    # User preferences seed data
├── seeding.py                   # Redis seeding with vector embeddings
├── context_provider.py          # Vector search configuration
├── conversation_storage.py      # Redis conversation persistence
├── main.py                      # Application entry point
├── azure.yaml                   # Azure Developer CLI configuration
└── requirements.txt             # Python dependencies
```

## Usage Examples

### Example 1: User with stored preferences
```
User: Hi, I'm Mark. Can you help me plan a trip?
Agent: [Retrieves Mark's preferences via semantic search from Redis vectors]
      Hello Mark! I'd be happy to help. I see you enjoy boutique hotels 
      and professional sports events...
```

### Example 2: Sports event booking
```
User: I'm traveling to New York in November and want to catch a basketball game
Agent: I found several NBA games in November! The Knicks vs Lakers on 
      November 15th at Madison Square Garden. Based on your preferences 
      for boutique experiences, I recommend premium seating...
```

### Example 3: Dynamic preference learning
```
User: I also prefer aisle seats on flights
Agent: [Calls remember_preference tool to store with vector embedding]
      Got it! I'll remember that you prefer aisle seats for future recommendations.
```

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
- `user_preferences` - Retrieve all stored preferences from Redis
- `remember_preference` - Learn and store new preferences with embeddings
- `reseed_user_preferences` - Reset preferences from seed.json (demo)

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
All conversations are automatically persisted to Redis under the namespace `cool-vibes-agent:Conversations:`. Each conversation thread stores:
- All messages (user and assistant)
- Message timestamps
- Agent information
- Complete conversation context

**Benefits**:
- Conversations persist across application restarts
- Users can resume previous conversations
- Full conversation history available for analysis
- Thread isolation for concurrent users

### Preferences
User preferences are stored with vector embeddings in Redis under keys like `cool-vibes-agent:UserPref:{user_name}:{id}`. 

**Storage structure**:
- Text content of the preference
- 1536-dimensional vector embedding (text-embedding-3-small)
- Metadata (user, timestamp, source)

**Capabilities**:
- **Semantic retrieval**: Find preferences by meaning, not just keywords
- **Dynamic learning**: Agent can learn new preferences during conversations
- **Context-aware**: Retrieve only relevant preferences for specific queries
- **Powered by RediSearch**: Uses HNSW vector similarity search

**Example**:
- Query: "What hotels does Mark like?"
- Retrieves: "Likes boutique hotels" (even without exact word match)
- Uses: Vector similarity with 85% threshold

**Verification**: Run `python verify_redis.py` to check stored data in Redis.

## Testing in Redis Insight

1. Connect to your Azure Managed Redis instance
2. Look for these key patterns:
   - `cool-vibes-agent:UserPref:*` - User preferences with vector embeddings
   - `cool-vibes-agent:Conversations:*` - Conversation threads
3. Inspect user preferences:
   - Each key is a hash with: `content`, `vector`, `user`, `timestamp`, `source`
   - Vector field contains 1536-dimensional embedding
4. Inspect conversation threads to see:
   - Complete message history
   - User and assistant messages
   - Timestamps and metadata
5. Run RediSearch queries:
   - `FT.SEARCH idx:user_preferences "*"` - View all indexed preferences
   - `FT.INFO idx:user_preferences` - View index details
6. Each new conversation in DevUI creates a new thread in Redis

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
- Verify `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` environment variable
- Azure Managed Redis Enterprise tier required for RediSearch

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
 - Jan Kalis, prompts and vibe coding
 - Jason Wang, AZD configuration

## License

MIT License - Sample/Demo Application
