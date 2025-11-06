# Feature: Multi-Agent Travel Planning System with Sports Event Booking

## Overview
Implement a multi-agent architecture for the Travel Chat Agent that includes a main orchestrator agent and a specialized sub-agent for professional sports event research and ticket booking. The system should be fully compatible with the Agent Framework DevUI for testing and demonstration.

## Agent Architecture

### 1. Main Agent: Travel-Agent

**Purpose**: Comprehensive travel planning orchestrator with research and booking assistance capabilities.

**Agent Configuration**:
- **Name**: `"travel-agent"`
- **Type**: `ChatAgent`
- **Description**: "Comprehensive travel planning agent with research and booking assistance"
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

When users express interest in sports or mention attending games, you should delegate to the 
ticket-purchase-agent to handle event research and ticket booking for professional sports events.

Use your tools proactively to provide detailed, helpful travel planning assistance.
Always consider the user's preferences, budget, and travel dates when making recommendations.

Be conversational, helpful, and provide actionable travel advice.
```

**Tools** (assigned to Travel-Agent):
1. `user_preferences` - Read user preferences from long-term Redis memory
2. `research_weather` - Weather research for destinations
3. `research_destination` - Destination research with attractions and culture
4. `find_flights` - Flight search and availability
5. `find_accommodation` - Accommodation search and recommendations
6. `booking_assistance` - General booking support

**Sub-Agent Integration**:
- Must be able to delegate to `ticket-purchase-agent` for sports event inquiries
- Pass relevant context (destination, dates, user preferences) to the sub-agent
- Receive and integrate sports event recommendations into the overall travel plan

---

### 2. Sub-Agent: Ticket-Purchase-Agent

**Purpose**: Specialized agent for researching professional sports events and handling ticket selection based on user preferences.

**Agent Configuration**:
- **Name**: `"ticket-purchase-agent"`
- **Type**: `ChatAgent` or specialized agent type
- **Description**: "Specialized agent for professional sports event research and ticket booking"
- **Invocation**: Called by Travel-Agent when sports event booking is needed

**Instructions/System Prompt**:
```
You are a specialized sports event booking agent focused on helping travelers attend professional 
sports games during their trips.

Your responsibilities:
1. Research professional sports events happening in the destination during the travel dates
2. Match events to the user's sports preferences and interests
3. Recommend appropriate seating options based on user preferences (e.g., premium seats for users 
   who prefer boutique experiences, family-friendly sections for users traveling with kids)
4. Handle ticket selection and purchase coordination

Always consider the user's profile when making recommendations:
- Budget preferences
- Seating preferences (close to action, family-friendly, premium experiences)
- Sports interests
- Travel dates and schedule

Provide clear information about:
- Event details (teams, venue, date/time)
- Available seating options with prices
- Venue amenities and accessibility
- Transportation to/from venue
```

**Tools** (assigned to Ticket-Purchase-Agent):
1. `user_preferences` - Read-only access to user preferences from long-term Redis memory
2. `find_events` - Research professional sports events in destination
3. `make_purchase` - Handle ticket selection and purchase (simulated with hardcoded data)

**Context Access**:
- Read-only access to user preferences from Redis (key: `"Preferences"`)
- Receives destination and travel dates from parent Travel-Agent
- Can query user preferences to personalize recommendations

---

## Tool Specifications

### Shared Tools

#### `user_preferences`
**Purpose**: Retrieve user preferences from long-term Redis memory store

**Access**: Read-only for both agents

**Parameters**:
```python
user_name: Annotated[str, "The name of the user to retrieve preferences for"]
```

**Returns**: 
- User insights/preferences as stored in Redis under `"Preferences"` key
- Format should include insights like "Likes to stay boutique hotels", "Loves food tours", etc.

**Implementation Notes**:
- Connects to Azure Managed Redis using context provider
- Queries the `"Preferences"` key by user name
- Returns empty/default preferences if user not found
- Should be accessible to both agents

---

### Travel-Agent Tools

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

### Ticket-Purchase-Agent Tools

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

## Multi-Agent Workflow

### Scenario: User wants to attend a sports game during their trip

1. **User Query**: "I'm traveling to New York in November and would love to catch a basketball game"

2. **Travel-Agent**:
   - Receives the query
   - Calls `user_preferences` to understand user profile (e.g., Mark likes boutique hotels)
   - Recognizes sports event request
   - **Delegates to Ticket-Purchase-Agent** with context:
     - Destination: "New York"
     - Dates: "November 2025"
     - Sport preference: "Basketball"
     - User profile: Mark's preferences

3. **Ticket-Purchase-Agent**:
   - Calls `user_preferences("Mark")` to get preferences
   - Calls `find_events(destination="New York", dates="November 2025", sport_type="basketball")`
   - Reviews available NBA games
   - Based on Mark's boutique hotel preference, infers he may prefer premium seating
   - Presents 2-3 game options with recommended seating

4. **User Selection**: "I'd like tickets for the Knicks vs Lakers game"

5. **Ticket-Purchase-Agent**:
   - Calls `make_purchase(event_id="knicks_lakers_nov15", seating_preference="premium", quantity=2)`
   - Returns confirmation with premium seats in section 101
   - Provides venue details and recommendations

6. **Travel-Agent**:
   - Receives sports event confirmation from sub-agent
   - Integrates into overall travel plan
   - May suggest accommodation near Madison Square Garden
   - May call `research_destination` for other activities around the game date

---

## DevUI Compatibility Requirements

### 1. Agent Registration
- Both agents must be properly registered with the Agent Framework
- Travel-Agent should be the primary/default agent displayed in DevUI
- Sub-agent should be invokable but not necessarily directly accessible in UI

### 2. Configuration
```python
# Travel-Agent (primary)
travel_agent = ChatAgent(
    name="travel-agent",
    description="Comprehensive travel planning agent with research and booking assistance",
    instructions="<full instructions as specified above>",
    chat_client=chat_client,
    tools=[user_preferences, research_weather, research_destination, 
           find_flights, find_accommodation, booking_assistance]
)

# Ticket-Purchase-Agent (sub-agent)
ticket_agent = ChatAgent(
    name="ticket-purchase-agent",
    description="Specialized agent for professional sports event research and ticket booking",
    instructions="<full instructions as specified above>",
    chat_client=chat_client,
    tools=[user_preferences, find_events, make_purchase]
)
```

### 3. Tool Definitions
- All tools must be properly decorated with `@function_tool` or equivalent
- Parameter annotations must use `Annotated[type, "description"]` format
- Return types should be clear and structured

### 4. Context Provider Integration
- User preferences tool must integrate with Redis context provider
- Should access data stored under `"Preferences"` key (from Feature 1 seeding)
- Context should be available across agent invocations

### 5. Thread Management
- Conversations should persist in Redis
- Both agents should have access to conversation history as needed
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
   - Test user preference retrieval for seeded users (Mark, Shruti)
   - Test sports event flow with different cities and dates
   - Verify sub-agent delegation works correctly

2. **Verification Points**:
   - User preferences correctly retrieved from Redis
   - Sports events returned match destination and dates
   - Seating recommendations align with user preferences
   - Conversation history persists across interactions
   - Both agents visible/functional in DevUI

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
3. ✅ Ticket-Purchase-Agent properly invoked by Travel-Agent
4. ✅ Sports event research returns relevant hardcoded events
5. ✅ Ticket purchase simulation completes with confirmation
6. ✅ User preferences correctly retrieved from Redis and influence recommendations
7. ✅ Conversation flows naturally between agents
8. ✅ Thread history persists in Redis
9. ✅ Error handling prevents conversation breakdown
10. ✅ Code is well-documented with clear agent/tool separation

---

## File Organization

Recommended structure:
```
agents/
    travel_agent.py       # Main Travel-Agent definition
    ticket_agent.py       # Ticket-Purchase-Agent definition
    
tools/
    user_tools.py         # user_preferences tool
    travel_tools.py       # research_weather, research_destination, find_flights, find_accommodation, booking_assistance
    sports_tools.py       # find_events, make_purchase
    
data/
    mock_events.py        # Hardcoded sports event data
    mock_venues.py        # Hardcoded venue and seating data
    
main.py                   # Application entry point, agent registration, DevUI setup
```

---

## Related Specifications
- Overall project spec: `Start.md`
- Redis seeding feature: `Feature1.md`
- Agent and tool definitions: `Agents_And_Tools.md`

---

## Notes
- This is a demonstration application showcasing multi-agent architecture
- Sports event data and ticket purchases are simulated (hardcoded)
- In production, these would connect to real ticketing APIs
- Focus is on demonstrating Agent Framework capabilities and Redis integration
- DevUI compatibility ensures easy testing and demonstration
