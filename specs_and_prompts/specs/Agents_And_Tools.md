## DevUI-compatible agents
### Main Travel agent 
  
    agent1 = ChatAgent(
        name="travel-agent",
        description="Comprehensive travel planning agent with research and booking assistance",
        instructions="""
        You are an expert travel planning agent with access to comprehensive research and booking tools.
        
        Your capabilities include:
        - Destination research with attractions and cultural insights
        - Sport and game activities, including attending professional sport games happening in the area closer to dates of travel
        - Destination research with attractions and cultural insights
        - Flight search and booking assistance
        - Accommodation research and booking guidance
        - Travel insurance recommendations
        - Documentation and visa requirements
        - Professional sports event research and ticket booking
        
        Use your tools proactively to provide detailed, helpful travel planning assistance.
        Always consider the user's preferences, budget, and travel dates when making recommendations.
        
        Be conversational, helpful, and provide actionable travel advice.
        """,
        chat_client=chat_client,
        tools=[
            user_preferences,
            research_weather,
            research_destination, 
            find_flights,
            find_accommodation,
            booking_assistance,
            find_events,
            make_purchase,
            remember_preference,
            get_semantic_preferences,
            reseed_user_preferences
        ]
    )


## Tools

user_preferences (read user preferences from Redis UserPref vector keys)
    user_name: Annotated[str, "The name of the user to retrieve preferences for"]

remember_preference (store new learned preferences with vector embeddings)
    user_name: Annotated[str, "The name of the user"]
    preference: Annotated[str, "The preference to remember for this user"]

get_semantic_preferences (retrieve preferences using semantic search)
    user_name: Annotated[str, "The name of the user"]
    query: Annotated[Optional[str], "Optional query to find relevant preferences"] = None

reseed_user_preferences (reset all preferences from seed.json)
    No parameters - resets all vectorized preferences

research_weather(
    destination: Annotated[str, "The destination to research weather for"])

research_destination(
    destination: Annotated[str, "The destination to research"],
    interests: Annotated[str, "Travel interests or preferences"] = "general tourism")

find_flights(
    origin: Annotated[str, "Departure city or airport"],
    destination: Annotated[str, "Arrival city or airport"],
    dates: Annotated[str, "Travel dates"] = "flexible")

find_accommodation(
    destination: Annotated[str, "Destination city"],
    budget: Annotated[str, "Budget level"] = "moderate")

find_events (research professional sports events)
    destination: Annotated[str, "The destination to research pro-sport events"]
    dates: Annotated[str, "Travel dates"] = "flexible")
    
booking_assistance (generate sample data, hardcode in the source code or retrieve pre-seeded data from Redis)
   
make_purchase (handle ticket selection and purchase for sports events - generate sample data, hardcode in the source code or retrieve pre-seeded data from Redis)


