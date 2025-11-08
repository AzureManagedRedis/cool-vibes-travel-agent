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
        
        Use your tools proactively to provide detailed, helpful travel planning assistance.
        Always consider the user's preferences, budget, and travel dates when making recommendations.
        
        Be conversational, helpful, and provide actionable travel advice.
        """,
        chat_client=chat_client,
        tools=[
            research_weather,
            research_destination, 
            find_flights,
            find_accommodation,
            booking_assistance,
            find_events
            make_purchase


## Tools

user_preferences (read only ok, read from long term Redis memory store)
    User

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


find_events 
    destination: Annotated[str, "The destination to research pro-sport events"]
    Dates: Annotated[str, "Travel dates"] = "flexible")
    
booking_assistance - generate sample data, hardcode in the source code or retrieve pre-seeded data from Redis
   
make_purchase - generate sample data, hardcode in the source code or retrieve pre-seeded data from Redis


