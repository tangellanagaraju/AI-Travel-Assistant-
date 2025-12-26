import requests
import json
import random

# --- Helper Functions ---

def _get_coordinates(city: str):
    """
    Fetches latitude and longitude for a city using Open-Meteo Geocoding API.
    """
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
        return None, None
    except Exception as e:
        print(f"Error fetching coordinates for {city}: {e}")
        return None, None

# --- Tool Implementations ---

def get_current_weather(city: str, country_code: str = None) -> str:
    """
    Fetch current weather conditions for a specified city using Open-Meteo.
    """
    search_query = f"{city}, {country_code}" if country_code else city
    lat, lon = _get_coordinates(city) # Note: API search is better with just city usually, but we could filter
    
    if not lat:
        return json.dumps({"error": f"Could not find coordinates for city: {search_query}"})

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        cw = data.get("current_weather", {})
        
        # Mapping WMO codes to descriptions (simplified)
        wmo_code = cw.get("weathercode", 0)
        conditions = "Clear"
        if wmo_code in [1, 2, 3]: conditions = "Partly Cloudy"
        elif wmo_code in [45, 48]: conditions = "Fog"
        elif wmo_code in [51, 53, 55, 61, 63, 65]: conditions = "Rain"
        elif wmo_code in [71, 73, 75, 77]: conditions = "Snow"
        elif wmo_code >= 95: conditions = "Thunderstorm"

        result = {
            "location": search_query,
            "temperature": f"{cw.get('temperature')}°C",
            "conditions": conditions,
            "wind_speed": f"{cw.get('windspeed')} km/h",
            "humidity": "N/A (Open-Meteo current_weather endpoint doesn't return humidity, check forecast)" 
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch weather data: {str(e)}"})

def get_weather_forecast(location: str, days: int = 3) -> str:
    """
    Get a weather forecast for a location for a specified number of days (1-5).
    """
    if days < 1 or days > 5:
        return json.dumps({"error": "Days must be between 1 and 5"})
        
    lat, lon = _get_coordinates(location)
    
    if not lat:
        return json.dumps({"error": f"Could not find coordinates for location: {location}"})

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto&forecast_days={days}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        forecasts = []
        
        for i in range(len(daily.get("time", []))):
            wmo_code = daily["weathercode"][i]
            # Simple mapping
            condition = "Unknown"
            if wmo_code == 0: condition = "Clear"
            elif wmo_code <= 3: condition = "Cloudy"
            elif wmo_code < 50: condition = "Fog"
            elif wmo_code < 80: condition = "Rain"
            elif wmo_code < 90: condition = "Showers"
            else: condition = "Thunderstorm/Snow"
            
            entry = {
                "date": daily["time"][i],
                "high": f"{daily['temperature_2m_max'][i]}°C",
                "low": f"{daily['temperature_2m_min'][i]}°C",
                "condition": condition
            }
            forecasts.append(entry)
            
        return json.dumps({"location": location, "forecast": forecasts})
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch forecast: {str(e)}"})

def search_attractions(location: str, category: str, price_range: str = None, min_rating: float = 0.0) -> str:
    """
    Find tourist attractions, restaurants, or activities in an area. (Mock Implementation)
    """
    # Mock Database
    mock_db = {
        "paris": [
            {"name": "Eiffel Tower", "category": "landmark", "rating": 4.8, "price": "moderate", "description": "Iconic iron lady."},
            {"name": "Louvre Museum", "category": "museum", "rating": 4.9, "price": "moderate", "description": "World's largest art museum."},
            {"name": "Le Jules Verne", "category": "restaurant", "rating": 4.6, "price": "expensive", "description": "Dining on the Eiffel Tower."},
        ],
        "london": [
            {"name": "British Museum", "category": "museum", "rating": 4.8, "price": "cheap", "description": "Human history and culture."},
            {"name": "The Shard", "category": "landmark", "rating": 4.7, "price": "expensive", "description": "Skyscraper with a view."},
            {"name": "Hyde Park", "category": "park", "rating": 4.9, "price": "cheap", "description": "Major park in Central London."},
        ],
        "new york": [
            {"name": "Statue of Liberty", "category": "landmark", "rating": 4.8, "price": "moderate", "description": "Symbol of freedom."},
            {"name": "Central Park", "category": "park", "rating": 4.9, "price": "cheap", "description": "Urban oasis."},
            {"name": "The Met", "category": "museum", "rating": 4.9, "price": "moderate", "description": "Metropolitan Museum of Art."},
        ]
    }
    
    city_lower = location.lower()
    
    # Simple fuzzy match or partial match for city
    found_city = None
    for k in mock_db:
        if k in city_lower or city_lower in k:
            found_city = k
            break
            
    if not found_city:
        # Generate generic mock data if city not found, so the demo always works
        generic_results = [
            {"name": f"{location} City Museum", "category": "museum", "rating": 4.5, "price": "moderate", "description": "Local history museum."},
            {"name": f"The Grand {location} Park", "category": "park", "rating": 4.7, "price": "cheap", "description": "Beautiful city park."},
            {"name": f"{location} Tower", "category": "landmark", "rating": 4.6, "price": "expensive", "description": "City viewpoint."},
        ]
        results = [r for r in generic_results if (category.lower() in r["category"] or category.lower() == r["category"])]
    else:
        results = mock_db[found_city]
    
    # Filtering
    filtered = []
    for item in results:
        # Category filter (strict or partial)
        if category.lower() not in item["category"]:
            continue
        # Price filter
        if price_range and item["price"] != price_range:
            continue
        # Rating filter
        if item["rating"] < min_rating:
            continue
        filtered.append(item)
        
    return json.dumps({"location": location, "results": filtered})

def calculate_travel_distance(origin: str, destination: str, mode: str = "driving") -> str:
    """
    Calculate distance and travel time. (Mock Implementation)
    """
    # Mock logic: Distance based on string length difference hash for consistency + random factor
    # This is just to return numbers that look real
    
    # Only for key demo routes
    routes = {
        ("london", "paris"): {"distance": "450 km", "time": "5h 30m" if mode=="driving" else "2h 20m"},
        ("paris", "london"): {"distance": "450 km", "time": "5h 30m" if mode=="driving" else "2h 20m"},
        ("new york", "washington"): {"distance": "360 km", "time": "4h 00m"},
    }
    
    key = (origin.lower(), destination.lower())
    if key in routes:
        data = routes[key]
        return json.dumps({"origin": origin, "destination": destination, "mode": mode, **data})
    
    # Generic Fallback
    base_dist = abs(hash(origin) - hash(destination)) % 1000 + 50
    
    speed = 60 # km/h driving
    if mode == "walking": speed = 5
    if mode == "transit": speed = 50
    if mode == "bicycling": speed = 15
    
    duration_hours = base_dist / speed
    hours = int(duration_hours)
    minutes = int((duration_hours - hours) * 60)
    
    return json.dumps({
        "origin": origin, 
        "destination": destination, 
        "mode": mode,
        "distance": f"{base_dist} km",
        "travel_time": f"{hours}h {minutes}m"
    })

def get_packing_suggestions(destination: str, duration_days: int, trip_type: str, month: str = None, weather_context: str = None) -> str:
    """
    Generate packing list suggestions.
    """
    essentials = ["passport", "phone charger", "underwear", "toothbrush", "toothpaste", "deodorant"]
    clothing = []
    gear = []
    
    # Weather-based logic
    is_cold = False
    is_rainy = False
    
    if weather_context:
        weather_lower = weather_context.lower()
        if "rain" in weather_lower or "shower" in weather_lower:
            is_rainy = True
        if "snow" in weather_lower or "cold" in weather_lower:
            is_cold = True
            
        # Try to parse temperature if present (e.g. "15C")
        import re
        temp_match = re.search(r"(-?\d+)", weather_context)
        if temp_match:
            temp = int(temp_match.group(1))
            if temp < 10: is_cold = True
            
    elif month:
        # Guess based on Northern Hemisphere month
        month_lower = month.lower()
        if month_lower in ["december", "january", "february"]:
            is_cold = True
            
    # Suggestions
    if is_cold:
        clothing.extend(["heavy coat", "scarf", "gloves", "thermal wear", "sweaters"])
    else:
        clothing.extend(["t-shirts", "light jacket"])
        
    if is_rainy:
        clothing.append("raincoat")
        gear.append("umbrella")
        
    # Trip Type logic
    trip_type_lower = trip_type.lower()
    if "beach" in trip_type_lower:
        clothing.extend(["swimsuit", "flip-flops", "sun hat"])
        gear.extend(["sunscreen", "beach towel", "sunglasses"])
    elif "hike" in trip_type_lower or "hiking" in trip_type_lower:
        clothing.extend(["hiking boots", "moisture-wicking socks"])
        gear.extend(["water bottle", "backpack", "first-aid kit", "bug spray"])
    elif "business" in trip_type_lower:
        clothing.extend(["blazer", "formal shoes", "dress shirts/blouses"])
        gear.extend(["laptop", "business cards", "notebook"])
    elif "snow" in trip_type_lower or "ski" in trip_type_lower:
        clothing.extend(["ski jacket", "snow pants"])
        gear.extend(["goggles"])
        
    # Duration logic
    num_outfits = duration_days + 1
    clothing.append(f"{num_outfits} sets of daily clothes")
    
    return json.dumps({
        "destination": destination,
        "trip_type": trip_type,
        "recommendations": {
            "essentials": essentials,
            "clothing": clothing,
            "gear": gear,
            "notes": f"Packing list generated for {duration_days} days in {destination} ({trip_type})."
        }
    })
