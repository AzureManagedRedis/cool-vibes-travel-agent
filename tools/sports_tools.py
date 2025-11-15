"""Sports event and ticket booking tools."""
from typing import Annotated
import random
from datetime import datetime
from data.sample_sport_events import EVENTS_DATA
from data.sample_sport_venues import SEATING_OPTIONS


def find_events(
    destination: Annotated[str, "The destination to research professional sports events"],
    dates: Annotated[str, "Travel dates"] = "flexible",
    sport_type: Annotated[str, "Preferred sport (basketball, football, baseball, soccer, etc.)"] = "any"
) -> str:
    """Research professional sports events in the destination during travel dates."""
    
    dest_lower = destination.lower()
    
    # Find events for the destination
    events = EVENTS_DATA.get(dest_lower, [])
    
    if not events:
        return f"No professional sports events found for {destination}. Try checking nearby cities like New York, Los Angeles, Chicago, or Boston."
    
    # Filter by sport type if specified
    if sport_type.lower() != "any":
        events = [e for e in events if sport_type.upper() in e['sport'].upper()]
    
    if not events:
        return f"No {sport_type} events found in {destination} for the specified dates."
    
    # Format the results
    result = f"🏟️ Professional Sports Events in {destination.title()}\n\n"
    result += f"📅 Search period: {dates}\n\n"
    
    for i, event in enumerate(events[:5], 1):  # Limit to 5 events
        result += f"{i}. {event['sport']}: {event['teams']}\n"
        result += f"   📍 Venue: {event['venue']}\n"
        result += f"   📅 Date: {event['date']} at {event['time']}\n"
        result += f"   🎫 Event ID: {event['id']}\n\n"
    
    result += "Use the event ID with make_purchase to book tickets!"
    
    return result


def make_purchase(
    event_id: Annotated[str, "The event identifier"],
    seating_preference: Annotated[str, "Seating preference (premium, mid-range, budget, family-friendly)"] = "mid-range",
    quantity: Annotated[int, "Number of tickets"] = 2
) -> str:
    """Handle ticket selection and simulated purchase for sports events."""
    
    # Find the event
    event = None
    for city_events in EVENTS_DATA.values():
        for e in city_events:
            if e['id'] == event_id:
                event = e
                break
        if event:
            break
    
    if not event:
        return f"Event not found with ID: {event_id}. Please use find_events to get valid event IDs."
    
    venue = event['venue']
    seating_data = SEATING_OPTIONS.get(venue, {})
    
    if not seating_data:
        return f"Seating information not available for {venue}."
    
    # Get seating preference
    pref_lower = seating_preference.lower()
    seating_info = seating_data.get(pref_lower, seating_data.get('mid-range', {}))
    
    if not seating_info:
        return f"Seating preference '{seating_preference}' not available. Try: premium, mid-range, budget, or family-friendly."
    
    # Generate seat details
    section = random.choice(seating_info['sections'])
    row = random.randint(1, 20)
    start_seat = random.randint(1, 15)
    seats = [f"{start_seat + i}" for i in range(quantity)]
    
    # Parse price range and calculate total
    price_range = seating_info['price_range'].replace('$', '').split('-')
    avg_price = (int(price_range[0]) + int(price_range[1])) // 2
    total_price = avg_price * quantity
    
    # Generate confirmation number
    confirmation = f"TKT-{random.randint(100000, 999999)}"
    
    return f"""
🎫 TICKET CONFIRMATION

Event: {event['sport']} - {event['teams']}
Venue: {venue}
Date & Time: {event['date']} at {event['time']}

SEATING DETAILS:
Section: {section}
Row: {row}
Seats: {', '.join(seats)}
Category: {seating_preference.title()}

PRICING:
Tickets: {quantity} x ${avg_price} = ${total_price}
Fees: ${quantity * 15}
Total: ${total_price + (quantity * 15)}

Confirmation Number: {confirmation}

📋 {seating_info['description']}

✅ Your tickets have been reserved! Check your email for details.

Transportation tip: Consider arriving 1 hour early for security and parking.
"""
