"""User preference tools."""
from typing import Annotated
import redis
from seeding import get_user_preferences

# Global Redis client (will be set by main.py)
_redis_client: redis.Redis = None


def set_redis_client(client: redis.Redis):
    """Set the global Redis client."""
    global _redis_client
    _redis_client = client


def user_preferences(user_name: Annotated[str, "The name of the user to retrieve preferences for"]) -> str:
    """
    Retrieve user preferences from long-term Redis memory.
    
    Args:
        user_name: The name of the user
        
    Returns:
        A formatted string of user preferences
    """
    if not _redis_client:
        return "User preferences service is not available."
    
    insights = get_user_preferences(_redis_client, user_name)
    
    if not insights:
        return f"No stored preferences found for {user_name}. This might be a new user."
    
    # Format insights into a readable string
    preferences_list = [insight.get('insight', '') for insight in insights if 'insight' in insight]
    
    if preferences_list:
        return f"User {user_name}'s preferences:\n" + "\n".join(f"- {pref}" for pref in preferences_list)
    else:
        return f"No specific preferences found for {user_name}."
