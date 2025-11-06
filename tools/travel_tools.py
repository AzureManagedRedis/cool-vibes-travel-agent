"""Travel-related tools for the travel agent."""
from typing import Annotated
import random


def research_weather(
    destination: Annotated[str, "The destination to research weather for"],
    dates: Annotated[str, "Travel dates (optional)"] = "current"
) -> str:
    """Get weather information for a destination."""
    # Mock weather data
    weather_conditions = [
        f"☀️ Sunny and pleasant in {destination}. Temperature: 72°F (22°C). Perfect for sightseeing!",
        f"⛅ Partly cloudy in {destination}. Temperature: 68°F (20°C). Light jacket recommended.",
        f"🌧️ Light rain expected in {destination}. Temperature: 65°F (18°C). Don't forget your umbrella!",
        f"🌤️ Clear skies in {destination}. Temperature: 75°F (24°C). Great weather for outdoor activities!"
    ]
    
    return random.choice(weather_conditions)


def research_destination(
    destination: Annotated[str, "The destination to research"],
    interests: Annotated[str, "Travel interests or preferences"] = "general tourism"
) -> str:
    """Research destination attractions and cultural insights."""
    # Mock destination data
    destinations = {
        "new york": {
            "attractions": "Empire State Building, Central Park, Times Square, Statue of Liberty, Broadway shows",
            "culture": "Diverse cultural scene with world-class museums, restaurants, and entertainment",
            "highlights": "The city that never sleeps! Famous for its iconic skyline, diverse neighborhoods, and vibrant arts scene."
        },
        "los angeles": {
            "attractions": "Hollywood Sign, Santa Monica Pier, Getty Center, Griffith Observatory, Venice Beach",
            "culture": "Entertainment capital with beaches, studios, and diverse culinary scene",
            "highlights": "Sunny weather year-round, perfect for beach lovers and movie enthusiasts."
        },
        "chicago": {
            "attractions": "Millennium Park, Navy Pier, Art Institute of Chicago, Willis Tower, Magnificent Mile",
            "culture": "Architecture, deep-dish pizza, blues music, and lakefront activities",
            "highlights": "Beautiful architecture and lakefront views, famous for its food scene."
        },
        "boston": {
            "attractions": "Freedom Trail, Fenway Park, Boston Common, Museum of Fine Arts, Quincy Market",
            "culture": "Historic city with colonial charm, academic atmosphere, and seafood",
            "highlights": "Rich American history and charming neighborhoods."
        }
    }
    
    dest_lower = destination.lower()
    if dest_lower in destinations:
        info = destinations[dest_lower]
        return f"""
📍 {destination.title()} Travel Guide

✨ Highlights: {info['highlights']}

🎭 Top Attractions: {info['attractions']}

🌆 Cultural Scene: {info['culture']}

Interests noted: {interests}
"""
    else:
        return f"{destination} is a wonderful destination! Popular for its unique attractions and local culture. Consider exploring local markets, historic sites, and trying regional cuisine."


def find_flights(
    origin: Annotated[str, "Departure city or airport"],
    destination: Annotated[str, "Arrival city or airport"],
    dates: Annotated[str, "Travel dates"] = "flexible",
    budget: Annotated[str, "Budget preference"] = "moderate"
) -> str:
    """Search for flight options."""
    # Mock flight data
    airlines = ["Delta", "American Airlines", "United", "JetBlue"]
    
    flight1 = {
        "airline": random.choice(airlines),
        "price": "$" + str(random.randint(200, 400)),
        "duration": f"{random.randint(2, 5)}h {random.randint(0, 55)}m",
        "stops": "Nonstop"
    }
    
    flight2 = {
        "airline": random.choice(airlines),
        "price": "$" + str(random.randint(150, 300)),
        "duration": f"{random.randint(4, 8)}h {random.randint(0, 55)}m",
        "stops": "1 stop"
    }
    
    return f"""
✈️ Flight Options from {origin} to {destination}

📅 Dates: {dates}
💰 Budget: {budget}

Option 1: {flight1['airline']}
  • Price: {flight1['price']}
  • Duration: {flight1['duration']}
  • Stops: {flight1['stops']}

Option 2: {flight2['airline']}
  • Price: {flight2['price']}
  • Duration: {flight2['duration']}
  • Stops: {flight2['stops']}

Would you like to proceed with booking?
"""


def find_accommodation(
    destination: Annotated[str, "Destination city"],
    dates: Annotated[str, "Check-in and check-out dates"] = "flexible",
    budget: Annotated[str, "Budget level"] = "moderate",
    accommodation_type: Annotated[str, "Type preference (hotel, boutique, resort, etc.)"] = "any"
) -> str:
    """Search for accommodation options."""
    # Mock accommodation data
    
    if "boutique" in accommodation_type.lower():
        return f"""
🏨 Boutique Hotel Options in {destination}

📅 Dates: {dates}
💰 Budget: {budget}

1. The Artisan Boutique Hotel
   • $280/night
   • Stylish rooms with unique decor
   • Rooftop bar and local art gallery
   • Rating: ⭐⭐⭐⭐⭐ 4.8/5

2. Heritage Boutique Inn
   • $240/night
   • Historic building with modern amenities
   • Complimentary wine tasting
   • Rating: ⭐⭐⭐⭐ 4.6/5

Perfect for travelers who appreciate unique, personalized experiences!
"""
    else:
        return f"""
🏨 Accommodation Options in {destination}

📅 Dates: {dates}
💰 Budget: {budget}

1. Grand Plaza Hotel
   • $180/night
   • Central location, modern amenities
   • Gym and pool access
   • Rating: ⭐⭐⭐⭐ 4.5/5

2. Comfort Suites Downtown
   • $150/night
   • Great value, clean rooms
   • Free breakfast included
   • Rating: ⭐⭐⭐⭐ 4.3/5

3. Luxury Resort & Spa
   • $320/night
   • Premium experience with spa
   • Fine dining on-site
   • Rating: ⭐⭐⭐⭐⭐ 4.9/5
"""


def booking_assistance(
    booking_type: Annotated[str, "Type of booking (flight, hotel, package, etc.)"],
    details: Annotated[str, "Booking details and requirements"]
) -> str:
    """Provide general booking support and coordination."""
    return f"""
📝 Booking Assistance for {booking_type}

I can help you with:
✓ Comparing prices and options
✓ Understanding cancellation policies
✓ Coordinating multiple bookings
✓ Travel insurance recommendations
✓ Special requests and accommodations

Details noted: {details}

To proceed with booking, I recommend:
1. Reviewing the options carefully
2. Checking cancellation policies
3. Considering travel insurance
4. Having your payment information ready

Would you like me to provide more specific information about any of these steps?
"""
