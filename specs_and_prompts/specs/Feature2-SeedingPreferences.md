# Feature 1: Redis Memory Seeding for User Preferences

## Overview
Implement a seeding mechanism that loads user preferences from `seed.json` into Azure Managed Redis when the application launches. This will initialize or replace the durable memory (long-term context) for named users with their travel preferences.

## Requirements

### 1. Seed Data Structure
- Read user preferences from `seed.json` file located in the project root
- The JSON structure contains a `user_memories` object with named users as keys
- Each user has an array of insights representing their travel preferences

### 2. Redis Storage Implementation
- **Redis Key**: Use `"Preferences"` as the primary key for storing user preferences
- This allows easy verification in Redis Insight that the seeding worked correctly
- Store the data in a format that's compatible with the Agent Framework's context provider system
- Ensure the data structure supports efficient retrieval by user name

### 3. Seeding Behavior
- Execute the seeding process automatically when the application starts
- **Replace existing data**: If preferences already exist for a user, completely replace them with the new data from `seed.json`
- Log the seeding operation clearly so developers can confirm it executed successfully
- Handle errors gracefully (e.g., file not found, Redis connection issues, invalid JSON format)

### 4. Integration Requirements
- Integrate with the existing Azure Managed Redis configuration (using `REDIS_URL` from `.env`)
- Work seamlessly with the Agent Framework's context provider system
- Ensure seeded preferences are immediately available to the Travel Chat Agent after seeding completes

### 5. Data Format in Redis
- Store preferences in a way that the Agent can easily query by user name
- Consider using Redis Hash or JSON data structures for efficient storage and retrieval
- The stored format should maintain the insight structure from `seed.json`
- Example expected format after seeding:
  - Key: `Preferences`
  - User "Mark" should have insights: "Likes to stay boutique hotels" and "Likes to explore any professional sports in the vicinity"
  - User "Shruti" should have insights: "Loves food tours" and "Prioritizes kids friendly activities"

### 6. Verification
- After seeding, developers should be able to open Redis Insight and:
  - See the `Preferences` key
  - View all seeded users and their preferences
  - Confirm the data matches `seed.json`

### 7. Code Organization
- Create a dedicated module/function for the seeding logic
- Keep seeding code separate from the main agent logic for maintainability
- Make it easy to disable or modify the seeding behavior if needed

### 8. Error Handling
- Validate `seed.json` structure before attempting to write to Redis
- Provide clear error messages if:
  - `seed.json` is missing or malformed
  - Redis connection fails
  - Write operations fail
- Decide whether the application should continue if seeding fails (recommendation: log error and continue, as the agent can still function without seeded data)

## Implementation Considerations

### Startup Sequence
1. Load application configuration (including Redis connection)
2. Read and parse `seed.json`
3. Connect to Azure Managed Redis
4. Clear/replace existing preferences under the `Preferences` key
5. Write new user preferences to Redis
6. Log success/failure
7. Continue with normal agent initialization

### Context Provider Integration
- Ensure the seeded data is accessible through the Agent Framework's context provider system
- The agent should be able to query: "What are Mark's travel preferences?" and receive the seeded insights
- Test that the context provider can retrieve preferences for both existing (seeded) and new users

### Testing Strategy
- Manually verify in Redis Insight after first run
- Test seeding with modified `seed.json` data to confirm replacement behavior
- Test agent's ability to use seeded preferences in conversations
- Verify behavior with missing or empty `seed.json`

## Success Criteria

1. ✅ Application successfully reads `seed.json` on startup
2. ✅ Preferences are stored in Redis under the `Preferences` key
3. ✅ All users from `seed.json` are properly seeded with their insights
4. ✅ Existing preferences are replaced (not merged) when app restarts
5. ✅ Data is visible and correctly formatted in Redis Insight
6. ✅ Agent can access and use seeded preferences in conversations
7. ✅ Appropriate error handling and logging is in place

## Example Usage Flow

```
User: "Hi, I'm Mark. Can you help me plan a trip?"
Agent: [Accesses seeded preferences from Redis]
       "Hello Mark! I'd be happy to help you plan a trip. I see you enjoy staying at 
       boutique hotels and like exploring professional sports events. Would you like 
       recommendations that align with these preferences?"
```

## Related Files
- `seed.json` - Source data for user preferences
- `.env` - Redis connection configuration (`REDIS_URL`)
- Redis context provider implementation (to be created/modified)

## Notes
- This is a development/demo feature to showcase Redis memory persistence
- In production, user preferences would typically come from a database or user registration system
- The seeding approach demonstrates how to pre-populate context for the Agent Framework
