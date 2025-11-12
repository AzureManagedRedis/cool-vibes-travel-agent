# Travel Chat Agent with Azure Managed Redis

A sample Travel Chat Agent built with Microsoft Agent Framework, Azure OpenAI, and Azure Managed Redis demonstrating multi-agent architecture with persistent memory.

## Features

- **Multi-Agent Architecture**: Main travel agent with specialized sports event booking sub-agent
- **Persistent Memory**: User preferences and conversation history stored in Azure Managed Redis
- **Conversation Continuity**: All conversations persist across sessions and application restarts
- **DevUI Integration**: Interactive testing interface
- **Personalized Recommendations**: Agents use stored user preferences to customize suggestions

## Prerequisites

- Python 3.10 or higher
- Azure Managed Redis instance
- Azure OpenAI deployment
- Valid Azure credentials

## Setup

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
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

3. **Run the Application**
```powershell
python main.py
```

4. **Access DevUI**

Open your browser to `http://localhost:8000` to interact with the agents.

## Project Structure

```
AF.AMR.VibeCoded/
├── agents/
│   ├── travel_agent.py      # Main travel agent configuration
│   └── ticket_agent.py       # Sports event booking agent
├── tools/
│   ├── user_tools.py         # User preference retrieval
│   ├── travel_tools.py       # Travel research tools
│   └── sports_tools.py       # Sports event tools
├── data/
│   ├── mock_events.py        # Sports event data
│   └── mock_venues.py        # Venue seating data
├── seed.json                 # User preferences seed data
├── seeding.py                # Redis seeding logic
├── conversation_storage.py   # Redis conversation persistence
├── verify_redis.py           # Redis verification utility
├── main.py                   # Application entry point
└── requirements.txt          # Python dependencies
```

## Usage Examples

### Example 1: User with stored preferences
```
User: Hi, I'm Mark. Can you help me plan a trip?
Agent: [Retrieves Mark's preferences: boutique hotels, professional sports]
      Hello Mark! I'd be happy to help. I see you enjoy boutique hotels 
      and professional sports events...
```

### Example 2: Sports event booking
```
User: I'm traveling to New York in November and want to catch a basketball game
Agent: [Delegates to ticket-purchase-agent]
      I found several NBA games in November! The Knicks vs Lakers on 
      November 15th at Madison Square Garden. Based on your preferences 
      for boutique experiences, I recommend premium seating...
```

### Example 3: Family travel
```
User: Hi, I'm Shruti. What are some family-friendly activities in Chicago?
Agent: [Retrieves Shruti's preferences: food tours, kids friendly]
      Hello Shruti! For family-friendly fun in Chicago, I recommend...
```

## Agents

### Travel-Agent (Primary)
- Destination research
- Weather information
- Flight and accommodation search
- General booking assistance
- Delegates to ticket-purchase-agent for sports events

### Ticket-Purchase-Agent (Sub-agent)
- Professional sports event research
- Personalized seating recommendations
- Simulated ticket booking

## Tools

**Shared:**
- `user_preferences` - Retrieve stored user preferences from Redis

**Travel Tools:**
- `research_weather` - Get weather information
- `research_destination` - Destination attractions and culture
- `find_flights` - Flight options
- `find_accommodation` - Hotel recommendations
- `booking_assistance` - General booking support

**Sports Tools:**
- `find_events` - Search professional sports events
- `make_purchase` - Book tickets (simulated)

## Redis Memory

### User Preferences
User preferences are seeded from `seed.json` on startup and stored in Redis under the key `cool-vibes-agent:Preferences`. 

### Conversation History
All conversations are automatically persisted to Redis under the namespace `cool-vibes-agent:Conversations:`. Each conversation thread has a unique ID and stores:
- All messages (user and assistant)
- Message timestamps
- Agent information
- Complete conversation context

**Verify Storage**: Run `python verify_redis.py` to check what's stored in Redis.

**Benefits**:
- Conversations persist across application restarts
- Users can resume previous conversations
- Full conversation history available for analysis
- Thread isolation for concurrent users

## Testing in Redis Insight

1. Connect to your Azure Managed Redis instance
2. Look for these keys:
   - `cool-vibes-agent:Preferences` - User preferences (Mark, Shruti, Jan, Roberto)
   - `cool-vibes-agent:Conversations:*` - Conversation threads (each with unique ID)
3. Inspect conversation threads to see:
   - Complete message history
   - User and assistant messages
   - Timestamps and metadata
4. Each new conversation in DevUI creates a new thread in Redis

## Notes

- Sports event data and ticket purchases are simulated with hardcoded data
- This is a demonstration application showcasing Agent Framework capabilities
- In production, tools would connect to real APIs

## Troubleshooting

**Redis Connection Error:**
- Verify your REDIS_URL is correct
- Check firewall rules allow your IP
- Ensure SSL is enabled in connection string

**Azure OpenAI Error:**
- Verify endpoint and API key are correct
- Check your deployment name matches
- Ensure you have quota available

**Import Errors:**
- Run `pip install -r requirements.txt`
- Ensure Python 3.10+ is being used

## License

MIT License - Sample/Demo Application
