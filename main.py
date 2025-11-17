"""Main application entry point for Travel Chat Agent."""
import os
import json
import logging
import asyncio
from dotenv import load_dotenv
import redis
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework import ChatAgent
from agent_framework.devui import serve
from azure.identity import AzureCliCredential
from agent_framework.observability import get_tracer, setup_observability

# AMR/AF: Tools and Agent section
# Ignite Code Location
# Import tools
from tools.user_tools import (
    remember_preference,
    get_semantic_preferences,
    reseed_user_preferences,
    set_redis_client
)
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

# Import conversation storage
from conversation_storage import create_chat_message_store_factory

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

    app_insights_conn_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

    # Setup observability if connection string is provided
    if app_insights_conn_string:
        setup_observability(enable_sensitive_data=True, applicationinsights_connection_string=app_insights_conn_string)
        logger.info("✓ Application Insights initialized successfully")
    else:
        logger.info("⚠ Application Insights connection string not found, skipping observability setup")
    
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
    
    # NOTE: Vector search is now handled by RedisProvider (initialized below)
    # The old manual context_provider.py approach has been replaced
    
    # Create chat message store factory for conversation persistence
    logger.info("Initializing conversation storage with Redis...")
    try:
        chat_message_store_factory = create_chat_message_store_factory(redis_url)
        logger.info("✓ Conversation storage configured")
        logger.info("  Conversations will be stored under: cool-vibes-agent-vnext:Conversations")
    except Exception as e:
        logger.error(f"Failed to initialize conversation storage: {e}")
        logger.warning("⚠ Continuing without conversation persistence")
        chat_message_store_factory = None
    
    # Note: Vector search components are no longer needed here since tools now use
    # the Context:* namespace that RedisProvider manages. All preference data is seeded
    # via seed_redis_providers_directly() below.
    
    # Initialize Azure OpenAI Responses client
    logger.info("Initializing Azure OpenAI Responses client...")
    try:
        # Set environment variables for Azure OpenAI
        os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint
        os.environ["AZURE_OPENAI_API_KEY"] = azure_key
        os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"] = azure_deployment
        
        # Use a supported API version for Responses/Assistants API
        azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', 'preview')
        os.environ["AZURE_OPENAI_API_VERSION"] = azure_api_version
        
        logger.info(f"Using Azure OpenAI API version: {azure_api_version}")
        logger.info(f"Using deployment: {azure_deployment}")
        
        responses_client = AzureOpenAIResponsesClient()
        logger.info("✓ Azure OpenAI Responses client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI Responses client: {e}")
        return
    
    # Load users from seed.json
    logger.info("Loading users from seed.json...")
    users = []
    try:
        with open('seed.json', 'r') as f:
            seed_data = json.load(f)
            users = list(seed_data.get('user_memories', {}).keys())
        logger.info(f"✓ Found {len(users)} users: {', '.join(users)}")
    except Exception as e:
        logger.error(f"Failed to load seed.json: {e}")
        return
    
    # Create travel agent tools list
    # Note: user_preferences removed - RedisProvider now automatically injects preferences
    travel_tools = [
        get_semantic_preferences,  # For targeted preference searches
        remember_preference,  # To learn new preferences
        reseed_user_preferences,  # To reset context data
        research_weather,
        research_destination,
        find_flights,
        find_accommodation,
        booking_assistance,
        find_events,
        make_purchase
    ]
    
    # Create RedisProviders - need to create index BEFORE seeding data
    logger.info("Initializing Redis context system...")
    redis_providers = {}
    
    try:
        from redis_provider import create_redis_provider, create_vectorizer
        from seeding import seed_to_redis_directly_sync
        
        # Create shared vectorizer once for consistency
        shared_vectorizer = create_vectorizer()
        logger.info("✓ Created shared vectorizer")
        
        # Create FIRST provider to initialize the index (with overwrite_index=True)
        # This ensures the index exists before we seed data
        first_user = users[0]
        logger.info(f"Creating first RedisProvider to initialize index...")
        first_provider = create_redis_provider(
            first_user, 
            redis_url, 
            shared_vectorizer,
            overwrite_index=True
        )
        redis_providers[first_user] = first_provider
        logger.info(f"✓ Index created via {first_user}'s provider")
        
        # NOW seed data - index exists so data will be indexed
        logger.info("Seeding user preferences directly to Redis...")
        seed_success = seed_to_redis_directly_sync(redis_url, shared_vectorizer)
        if seed_success:
            logger.info("✓ User preferences seeded and indexed")
        else:
            logger.warning("⚠ Seeding failed, providers will start with empty context")
        
        # Create remaining RedisProviders (overwrite_index=False)
        logger.info("Creating remaining RedisProviders...")
        for user_name in users[1:]:
            try:
                provider = create_redis_provider(
                    user_name, 
                    redis_url, 
                    shared_vectorizer,
                    overwrite_index=False  # Don't recreate index
                )
                redis_providers[user_name] = provider
                logger.info(f"✓ RedisProvider created for {user_name}")
            except Exception as e:
                logger.error(f"Failed to create RedisProvider for {user_name}: {e}")
        
    except Exception as e:
        logger.error(f"Failed to initialize RedisProviders: {e}")
        redis_providers = {}
    
    # Create one agent per user with their RedisProvider
    logger.info("Creating travel agents for each user...")
    agents = []
    
    for user_name in users:
        agent_name = f"{user_name}-cool-vibes-travel-agent"
        redis_provider = redis_providers.get(user_name)
        
        try:
            agent = responses_client.create_agent(
                name=agent_name,
                description=f"{TRAVEL_AGENT_DESCRIPTION} for {user_name}",
                instructions=TRAVEL_AGENT_INSTRUCTIONS,
                tools=travel_tools,
                chat_message_store_factory=chat_message_store_factory,
                context_providers=redis_provider if redis_provider else None
            )
            agents.append(agent)
            
            if redis_provider:
                logger.info(f"✓ {agent_name} created with automatic context injection")
            else:
                logger.info(f"✓ {agent_name} created (explicit tools only)")
            
        except Exception as e:
            logger.error(f"Failed to create agent for {user_name}: {e}")
    
    logger.info(f"✓ Created {len(agents)} travel agents")
    
    # Start DevUI
    logger.info("Starting DevUI...")
    logger.info("=" * 60)
    logger.info("🚀 Travel Chat Agents are ready!")
    logger.info("=" * 60)
    logger.info("Access the DevUI in your browser to start chatting")
    logger.info(f"Available agents: {', '.join([a.name for a in agents])}")
    logger.info("Select an agent from the dropdown to start a conversation")
    logger.info("Each agent has personalized context for their user")
    logger.info("=" * 60)
    
    # Start DevUI with all user agents
    serve(
        entities=agents,
        host="0.0.0.0",
        port=8000,
        auto_open=False
    )


if __name__ == "__main__":
    main()
