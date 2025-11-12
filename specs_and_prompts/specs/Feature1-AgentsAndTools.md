# Feature: Travel Planning Agent with Sports Event Booking

## Overview
Implement a comprehensive travel planning agent that includes destination research, booking assistance, and professional sports event research and ticket booking capabilities. The system should be fully compatible with the Agent Framework DevUI for testing and demonstration.

## Agent Architecture

### Travel-Agent

**Purpose**: Comprehensive travel planning orchestrator with research, booking assistance, and sports event booking capabilities.

**Agent Configuration**:
- **Name**: `"travel-agent"`
- **Type**: `ChatAgent`
- **Description**: "Comprehensive travel planning agent with research, booking assistance, and sports event booking"
- **DevUI Compatibility**: Must be configured as the primary agent accessible through DevUI interface

**Instructions/System Prompt**:
```
You are an expert travel planning agent with access to comprehensive research and booking tools.

Your capabilities include:
- Destination research with attractions and cultural insights
- Professional sports events and game activities happening in the area during travel dates
- Flight search and booking assistance
- Accommodation research and booking guidance
- Weather information for destinations
- Travel insurance recommendations
- Documentation and visa requirements
- Sports event research and ticket booking

When users express interest in sports or mention attending games, use your find_events and 
make_purchase tools to help them find and book tickets for professional sports events.

Use your tools proactively to provide detailed, helpful travel planning assistance.
Always consider the user's preferences, budget, and travel dates when making recommendations.

Be conversational, helpful, and provide actionable travel advice.
```

**Tools** (assigned to Travel-Agent):
1. `user_preferences` - Read user preferences from Redis UserPref vector keys
2. `remember_preference` - Store new learned preferences with vector embeddings
3. `get_semantic_preferences` - Retrieve preferences using semantic search
4. `reseed_user_preferences` - Reset all preferences from seed.json
5. `research_weather` - Weather research for destinations
6. `research_destination` - Destination research with attractions and culture
7. `find_flights` - Flight search and availability
8. `find_accommodation` - Accommodation search and recommendations
9. `booking_assistance` - General booking support
10. `find_events` - Research professional sports events in destination
11. `make_purchase` - Handle ticket selection and purchase for sports events

---

## Tool Specifications

### User Preference Tools

#### `user_preferences`
**Purpose**: Retrieve user preferences from Redis UserPref vector keys

**Parameters**:
```python
user_name: Annotated[str, "The name of the user to retrieve preferences for"]
```

**Returns**: 
- User insights/preferences as stored in Redis under `cool-vibes-agent:UserPref:{user_name}:*` keys
- Format includes insights like "Likes to stay boutique hotels", "Loves food tours", etc.

**Implementation Notes**:
- Reads from vectorized UserPref keys in Redis
- Returns empty/default preferences if user not found

---

#### `remember_preference`
**Purpose**: Store a new preference for a user with semantic search capabilities

**Parameters**:
```python
user_name: Annotated[str, "The name of the user"]
preference: Annotated[str, "The preference to remember for this user"]
```

**Returns**: Confirmation message

**Implementation Notes**:
- Stores preference with vector embedding for semantic search
- Uses Azure OpenAI text-embedding-3-small model
- Allows agent to learn new preferences during conversations

---

#### `get_semantic_preferences`
**Purpose**: Retrieve user preferences using semantic search

**Parameters**:
```python
user_name: Annotated[str, "The name of the user"]
query: Annotated[Optional[str], "Optional query to find relevant preferences"] = None
```

**Returns**: Formatted string of user preferences (optionally filtered by semantic similarity)

**Implementation Notes**:
- Uses vector embeddings for semantic similarity search
- If query provided, returns preferences most relevant to the query
- Fallback to regular user_preferences if vector search unavailable

---

#### `reseed_user_preferences`
**Purpose**: Delete all existing vectorized user preferences and re-seed from seed.json

**Parameters**: None

**Returns**: Confirmation message

**Implementation Notes**:
- Deletes all cool-vibes-agent:UserPref:* keys
- Drops and recreates RediSearch index
- Re-seeds from seed.json with fresh vector embeddings

---

### Travel Tools

#### `research_weather`
**Purpose**: Get weather information for a destination

**Parameters**:
```python
destination: Annotated[str, "The destination to research weather for"]
dates: Annotated[str, "Travel dates (optional)"] = "current"
```

**Returns**: Weather forecast or current conditions (can use hardcoded/mock data)

---

#### `research_destination`
**Purpose**: Research destination attractions and cultural insights

**Parameters**:
```python
destination: Annotated[str, "The destination to research"]
interests: Annotated[str, "Travel interests or preferences"] = "general tourism"
```

**Returns**: Destination information, attractions, cultural insights (can use hardcoded/mock data)

---

#### `find_flights`
**Purpose**: Search for flight options

**Parameters**:
```python
origin: Annotated[str, "Departure city or airport"]
destination: Annotated[str, "Arrival city or airport"]
dates: Annotated[str, "Travel dates"] = "flexible"
budget: Annotated[str, "Budget preference"] = "moderate"
```

**Returns**: Flight options with prices and schedules (can use hardcoded/mock data)

---

#### `find_accommodation`
**Purpose**: Search for accommodation options

**Parameters**:
```python
destination: Annotated[str, "Destination city"]
dates: Annotated[str, "Check-in and check-out dates"] = "flexible"
budget: Annotated[str, "Budget level"] = "moderate"
accommodation_type: Annotated[str, "Type preference (hotel, boutique, resort, etc.)"] = "any"
```

**Returns**: Accommodation options with prices and amenities (can use hardcoded/mock data)

**Personalization**: Should consider user preferences (e.g., recommend boutique hotels for users who prefer them)

---

#### `booking_assistance`
**Purpose**: Provide general booking support and coordination

**Parameters**:
```python
booking_type: Annotated[str, "Type of booking (flight, hotel, package, etc.)"]
details: Annotated[str, "Booking details and requirements"]
```

**Returns**: Booking guidance and next steps (can use hardcoded/mock responses)

---

### Sports Event Tools

#### `find_events`
**Purpose**: Research professional sports events in the destination during travel dates

**Parameters**:
```python
destination: Annotated[str, "The destination to research professional sports events"]
dates: Annotated[str, "Travel dates"] = "flexible"
sport_type: Annotated[str, "Preferred sport (basketball, football, baseball, soccer, etc.)"] = "any"
```

**Returns**: 
- List of professional sports events with details:
  - Sport type (NBA, NFL, MLB, MLS, etc.)
  - Teams playing
  - Venue name and location
  - Date and time
  - Ticket availability overview

**Implementation Notes**:
- Generate hardcoded sample data for major cities (e.g., New York, Los Angeles, Chicago, Boston)
- Include variety of sports (NBA, NFL, MLB, NHL, MLS, etc.)
- Consider travel dates when filtering events
- Should return 3-5 relevant events per query

**Sample Hardcoded Data Structure**:
```python
events = {
    "New York": [
        {"sport": "NBA", "teams": "Knicks vs Lakers", "venue": "Madison Square Garden", 
         "date": "2025-11-15", "time": "19:30"},
        {"sport": "NHL", "teams": "Rangers vs Bruins", "venue": "Madison Square Garden", 
         "date": "2025-11-16", "time": "19:00"},
    ],
    "Los Angeles": [
        {"sport": "NBA", "teams": "Lakers vs Warriors", "venue": "Crypto.com Arena", 
         "date": "2025-11-20", "time": "19:30"},
    ],
    # ... more cities and events
}
```

---

#### `make_purchase`
**Purpose**: Handle ticket selection and simulated purchase for sports events

**Parameters**:
```python
event_id: Annotated[str, "The event identifier"]
seating_preference: Annotated[str, "Seating preference (premium, mid-range, budget, family-friendly)"] = "mid-range"
quantity: Annotated[int, "Number of tickets"] = 2
```

**Returns**:
- Ticket confirmation details:
  - Selected seats (section, row, seat numbers)
  - Price breakdown
  - Venue information
  - Event details
  - Confirmation number (generated)

**Implementation Notes**:
- Generate hardcoded seating options for different venues
- Price tiers based on seating location
- Consider user preferences when recommending sections:
  - Users who like "boutique" experiences → Premium seating
  - Users who prioritize "kids friendly" → Family-friendly sections
  - Budget-conscious users → Upper deck/affordable options

**Sample Hardcoded Data Structure**:
```python
seating_options = {
    "Madison Square Garden": {
        "premium": {"sections": ["101", "102", "103"], "price_range": "$250-500"},
        "mid-range": {"sections": ["200-210"], "price_range": "$100-200"},
        "budget": {"sections": ["300-320"], "price_range": "$40-80"},
        "family-friendly": {"sections": ["215", "216"], "price_range": "$120-180"},
    },
    # ... more venues
}
```

---

## Workflow Example

### Scenario: User wants to attend a sports game during their trip

1. **User Query**: "I'm traveling to New York in November and would love to catch a basketball game"

2. **Travel-Agent**:
   - Receives the query
   - Calls `user_preferences("Mark")` to understand user profile (e.g., Mark likes boutique hotels)
   - Recognizes sports event request
   - Calls `find_events(destination="New York", dates="November 2025", sport_type="basketball")`
   - Reviews available NBA games
   - Based on Mark's boutique hotel preference, infers he may prefer premium seating
   - Presents 2-3 game options with recommended seating

3. **User Selection**: "I'd like tickets for the Knicks vs Lakers game"

4. **Travel-Agent**:
   - Calls `make_purchase(event_id="knicks_lakers_nov15", seating_preference="premium", quantity=2)`
   - Returns confirmation with premium seats in section 101
   - Provides venue details and recommendations
   - May suggest accommodation near Madison Square Garden using `find_accommodation`
   - May call `research_destination` for other activities around the game date

---

## DevUI Compatibility Requirements

### 1. Agent Registration
- Travel-Agent must be properly registered with the Agent Framework
- Travel-Agent should be the primary/default agent displayed in DevUI

### 2. Configuration
```python
# Travel-Agent (single agent with all tools)
travel_agent = ChatAgent(
    name="travel-agent",
    description="Comprehensive travel planning agent with research, booking assistance, and sports event booking",
    instructions="<full instructions as specified above>",
    chat_client=chat_client,
    tools=[user_preferences, remember_preference, get_semantic_preferences, reseed_user_preferences,
           research_weather, research_destination, find_flights, find_accommodation, 
           booking_assistance, find_events, make_purchase]
)
```

### 3. Tool Definitions
- All tools must be properly decorated with `@function_tool` or equivalent
- Parameter annotations must use `Annotated[type, "description"]` format
- Return types should be clear and structured

### 4. Context Provider Integration
- User preferences tool must integrate with Redis context provider
- Should access data stored under `cool-vibes-agent:UserPref:*` keys (vector storage)
- Context should be available across agent invocations
- Support for dynamic learning with remember_preference and semantic search

### 5. Thread Management
- Conversations should persist in Redis
- Agent should have access to conversation history as needed
- Thread isolation for concurrent users

---

## Implementation Considerations

### Error Handling
- Gracefully handle cases where user preferences are not found
- Provide default recommendations if sports events are not available
- Handle Redis connection issues without breaking the conversation flow

### Testing Strategy
1. **DevUI Manual Testing**:
   - Open DevUI and start conversation with Travel-Agent
   - Test user preference retrieval for seeded users (Mark, Shruti, Jan, Roberto)
   - Test remember_preference to store new preferences during conversations
   - Test get_semantic_preferences for semantic search queries
   - Test sports event flow with different cities and dates
   - Verify ticket booking works correctly

2. **Verification Points**:
   - User preferences correctly retrieved from Redis UserPref keys
   - New preferences can be learned and stored with embeddings
   - Semantic search returns relevant preferences
   - Sports events returned match destination and dates
   - Seating recommendations align with user preferences
   - Conversation history persists across interactions
   - Agent visible/functional in DevUI

### Personalization Examples

**For Mark** (likes boutique hotels, professional sports):
- Recommend premium seating for games
- Suggest boutique hotels near sports venues
- Prioritize major sporting events

**For Shruti** (loves food tours, kids friendly):
- Recommend family-friendly seating sections
- Suggest afternoon games suitable for children
- Include family amenities at venues

---

## Success Criteria

1. ✅ Travel-Agent successfully accessible through DevUI
2. ✅ All Travel-Agent tools functional with mock/hardcoded data
3. ✅ Sports event research returns relevant hardcoded events
4. ✅ Ticket purchase simulation completes with confirmation
5. ✅ User preferences correctly retrieved from Redis UserPref keys and influence recommendations
6. ✅ Dynamic learning works - new preferences can be stored with remember_preference
7. ✅ Semantic search retrieves relevant preferences with get_semantic_preferences
8. ✅ Conversation flows naturally
9. ✅ Thread history persists in Redis
10. ✅ Error handling prevents conversation breakdown
11. ✅ Code is well-documented with clear agent/tool separation

---

## File Organization

Recommended structure:
```
agents/
    travel_agent.py       # Travel-Agent definition with all capabilities
    
tools/
    user_tools.py         # user_preferences, remember_preference, get_semantic_preferences, reseed_user_preferences
    travel_tools.py       # research_weather, research_destination, find_flights, find_accommodation, booking_assistance
    sports_tools.py       # find_events, make_purchase
    
data/
    mock_events.py        # Hardcoded sports event data
    mock_venues.py        # Hardcoded venue and seating data
    
context_provider.py       # Vector storage and retrieval functions
seeding.py                # Redis seeding with vector embeddings
conversation_storage.py   # Conversation persistence
main.py                   # Application entry point, agent registration, DevUI setup
```

---

## Related Specifications
- Overall project spec: `Start.md`
- Redis seeding with vectors: `Feature4-DynamicPreferences.md`
- Conversation persistence: `Feature3.md`

---

## Notes
- This is a demonstration application showcasing Agent Framework capabilities
- Sports event data and ticket purchases are simulated (hardcoded)
- In production, these would connect to real ticketing APIs
- Focus is on demonstrating Agent Framework capabilities and Redis integration with vector search
- DevUI compatibility ensures easy testing and demonstration
- Dynamic learning allows the agent to remember new user preferences during conversations
