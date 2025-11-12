"""Travel-related tools for the travel agent."""
from typing import Annotated
import random
import requests
from datetime import datetime, timedelta


def research_weather(
    destination: Annotated[str, "The destination to research weather for"],
    dates: Annotated[str, "Travel dates (optional)"] = "current"
) -> str:
    """Get weather information for a destination."""
    
    # Major city coordinates
    cities = {
        "new york": (40.7128, -74.0060), "los angeles": (34.0522, -118.2437),
        "chicago": (41.8781, -87.6298), "boston": (42.3601, -71.0589),
        "san francisco": (37.7749, -122.4194), "seattle": (47.6062, -122.3321),
        "miami": (25.7617, -80.1918), "las vegas": (36.1699, -115.1398),
        "orlando": (28.5383, -81.3792), "denver": (39.7392, -104.9903)
    }
    
    lat, lon = cities.get(destination.lower(), (None, None))
    
    # Fallback to geocoding if city not found
    if not lat:
        try:
            geo_resp = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1&format=json",
                timeout=5
            ).json()
            if geo_resp.get('results'):
                lat, lon = geo_resp['results'][0]['latitude'], geo_resp['results'][0]['longitude']
            else:
                return f"⚠️ Could not find weather data for '{destination}'. Try a major city name."
        except Exception as e:
            return f"⚠️ Unable to fetch weather data: {str(e)}"
    
    try:
        # Fetch weather data
        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m"
            f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&temperature_unit=fahrenheit&forecast_days=5",
            timeout=5
        ).json()
        
        curr = weather['current']
        daily = weather['daily']
        
        # Weather icons
        icons = {
            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️",
            51: "🌧️", 53: "🌧️", 55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "🌧️",
            71: "❄️", 73: "❄️", 75: "❄️", 80: "🌦️", 81: "🌦️", 82: "🌦️",
            95: "⛈️", 96: "⛈️", 99: "⛈️"
        }
        
        def f_to_c(f):
            return round((f - 32) * 5/9, 1)
        
        temp_f = curr['temperature_2m']
        feels_f = curr['apparent_temperature']
        
        result = f"""🌍 Weather for {destination.title()}

📅 Current: {icons.get(curr['weather_code'], '🌡️')} {temp_f}°F ({f_to_c(temp_f)}°C)
Feels like: {feels_f}°F ({f_to_c(feels_f)}°C) | Wind: {curr['wind_speed_10m']} mph

📆 5-Day Forecast:"""
        
        for i in range(5):
            high, low = daily['temperature_2m_max'][i], daily['temperature_2m_min'][i]
            result += f"\n{daily['time'][i]}: {icons.get(daily['weather_code'][i], '🌡️')} {high}°F ({f_to_c(high)}°C) / {low}°F ({f_to_c(low)}°C)"
            if daily['precipitation_sum'][i] > 0:
                result += f" 🌧️ {daily['precipitation_sum'][i]}in"
        
        result += f"\n\n💡 Travel Dates: {dates}"
        
        # Add personalized weather tips
        avg_high = sum(daily['temperature_2m_max'][:5]) / 5
        has_rain = any(daily['precipitation_sum'][i] > 0.1 for i in range(5))
        
        result += "\n\n� Packing Tips:"
        if avg_high > 75:
            result += "\n• Light, breathable clothing recommended"
        elif avg_high < 50:
            result += "\n• Pack warm layers and a jacket"
        
        if has_rain:
            result += "\n• Don't forget an umbrella or rain jacket"
        
        return result
        
    except Exception as e:
        return f"⚠️ Error fetching weather data: {str(e)}"


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
    origin: Annotated[str, "Departure city or airport (REQUIRED - must ask user if not provided)"],
    destination: Annotated[str, "Arrival city or airport (REQUIRED - must ask user if not provided)"],
    dates: Annotated[str, "Travel dates"] = "flexible",
    budget: Annotated[str, "Budget preference"] = "moderate"
) -> str:
    """Search for flight options. MUST have both origin and destination."""
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
