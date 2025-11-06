"""Main application entry point for Travel Chat Agent."""
import os
import logging
from dotenv import load_dotenv
import redis
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework import ChatAgent
from agent_framework.devui import serve
from azure.identity import AzureCliCredential
from agent_framework.observability import get_tracer, setup_observability

# Import tools
from tools.user_tools import user_preferences, set_redis_client
from tools.travel_tools import (
    research_weather,
    research_destination,
    find_flights,
    find_accommodation,
    booking_assistance
)
from tools.sports_tools import find_events, make_purchase

# Import agent configurations
from agents.travel_agent import (
    TRAVEL_AGENT_NAME,
    TRAVEL_AGENT_DESCRIPTION,
    TRAVEL_AGENT_INSTRUCTIONS
)
from agents.ticket_agent import (
    TICKET_AGENT_NAME,
    TICKET_AGENT_DESCRIPTION,
    TICKET_AGENT_INSTRUCTIONS
)

# Import seeding
from seeding import seed_user_preferences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize and run the Travel Chat Agent."""
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    redis_url = os.getenv('REDIS_URL')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_key = os.getenv('AZURE_OPENAI_API_KEY')
    azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

    setup_observability(enable_sensitive_data=True, applicationinsights_connection_string="InstrumentationKey=ac20080d-e4d8-4e2d-bc32-3f37c9bf3c28;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/;LiveEndpoint=https://westus2.livediagnostics.monitor.azure.com/;ApplicationId=cea5dbb7-3a1d-4704-a179-dc0ec23b1e3e")
    logger.info("App Insights initialized successfully")
    
    if not all([redis_url, azure_endpoint, azure_key, azure_deployment]):
        logger.error("Missing required environment variables. Please check your .env file.")
        logger.error("Required: REDIS_URL, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME")
        return
    
    # Initialize Redis client
    logger.info("Connecting to Azure Managed Redis...")
    try:
        redis_client = redis.from_url(redis_url, decode_responses=False)
        redis_client.ping()
        logger.info("✓ Connected to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return
    
    # Set Redis client for user tools
    set_redis_client(redis_client)
    
    # Seed user preferences
    logger.info("Seeding user preferences from seed.json...")
    if seed_user_preferences(redis_client):
        logger.info("✓ User preferences seeded successfully")
    else:
        logger.warning("⚠ Seeding completed with warnings or was skipped")
    
    # Initialize Azure OpenAI Responses client
    logger.info("Initializing Azure OpenAI Responses client...")
    try:
        # Set environment variables for Azure OpenAI
        os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint
        os.environ["AZURE_OPENAI_API_KEY"] = azure_key
        os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"] = azure_deployment
        
        # Use a supported API version for Responses API (2024-08-01-preview is known to work)
        azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
        os.environ["AZURE_OPENAI_API_VERSION"] = azure_api_version
        
        logger.info(f"Using Azure OpenAI API version: {azure_api_version}")
        logger.info(f"Using deployment: {azure_deployment}")
        
        responses_client = AzureOpenAIResponsesClient()
        logger.info("✓ Azure OpenAI Responses client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI Responses client: {e}")
        return
    
    # Create travel agent tools list
    travel_tools = [
        user_preferences,
        research_weather,
        research_destination,
        find_flights,
        find_accommodation,
        booking_assistance,
        find_events,
        make_purchase
    ]
    
    # Create ticket agent tools list
    ticket_tools = [
        user_preferences,
        find_events,
        make_purchase
    ]
    
    # Create Travel Agent
    logger.info("Creating Travel Agent...")
    travel_agent = responses_client.create_agent(
        name=TRAVEL_AGENT_NAME,
        description=TRAVEL_AGENT_DESCRIPTION,
        instructions=TRAVEL_AGENT_INSTRUCTIONS,
        tools=travel_tools
    )
    logger.info(f"✓ {TRAVEL_AGENT_NAME} created")
    
    # Create Ticket Purchase Agent
    logger.info("Creating Ticket Purchase Agent...")
    ticket_agent = responses_client.create_agent(
        name=TICKET_AGENT_NAME,
        description=TICKET_AGENT_DESCRIPTION,
        instructions=TICKET_AGENT_INSTRUCTIONS,
        tools=ticket_tools
    )
    logger.info(f"✓ {TICKET_AGENT_NAME} created")
    
    # Start DevUI
    logger.info("Starting DevUI...")
    logger.info("=" * 60)
    logger.info("🚀 Travel Chat Agent is ready!")
    logger.info("=" * 60)
    logger.info("Access the DevUI in your browser to start chatting")
    logger.info("Try these example queries:")
    logger.info("  - 'Hi, I'm Mark. Can you help me plan a trip?'")
    logger.info("  - 'I want to visit New York in November and catch a basketball game'")
    logger.info("  - 'Hi, I'm Shruti. What family-friendly activities are in Chicago?'")
    logger.info("=" * 60)
    
    # Start DevUI with both agents
    serve(
        entities=[travel_agent, ticket_agent],
        host="localhost",
        port=8000,
        auto_open=True
    )


if __name__ == "__main__":
    main()
