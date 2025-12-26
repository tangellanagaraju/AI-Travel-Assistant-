"""
Tool Schemas for the Smart Weather & Travel Assistant.
These schemas define the interface for the LLM to interact with the Python functions.
"""

TOOL_SCHEMAS = [
    {
        "name": "get_current_weather",
        "description": "Fetch current weather conditions for a specified city. Returns temperature, conditions, humidity, and wind speed.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city to get weather for, e.g., 'London' or 'New York'.",
                },
                "country_code": {
                    "type": "string",
                    "description": "Optional 2-letter country code to clarify the city (e.g., 'US', 'UK').",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_weather_forecast",
        "description": "Get a weather forecast for a location for a specified number of days (1-5).",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or location to get the forecast for.",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days for the forecast. Must be between 1 and 5.",
                    "minimum": 1,
                    "maximum": 5,
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "search_attractions",
        "description": "Find tourist attractions, restaurants, or activities in a specific area.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or area to search in.",
                },
                "category": {
                    "type": "string",
                    "description": "Type of places to search for.",
                    "enum": ["museum", "park", "restaurant", "landmark", "activity", "shopping"],
                },
                "price_range": {
                    "type": "string",
                    "description": "Optional price filter.",
                    "enum": ["cheap", "moderate", "expensive"],
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum rating (0-5) to filter results.",
                    "minimum": 0,
                    "maximum": 5,
                }
            },
            "required": ["location", "category"],
        },
    },
    {
        "name": "calculate_travel_distance",
        "description": "Calculate the distance and estimated travel time between two locations.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Starting location (city/address).",
                },
                "destination": {
                    "type": "string",
                    "description": "Ending location (city/address).",
                },
                "mode": {
                    "type": "string",
                    "description": "Mode of transport.",
                    "enum": ["driving", "walking", "transit", "bicycling"],
                }
            },
            "required": ["origin", "destination"],
        },
    },
    {
        "name": "get_packing_suggestions",
        "description": "Generate a packing list based on destination, trip duration, activity type, and weather context.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "The destination city or region.",
                },
                "duration_days": {
                    "type": "integer",
                    "description": "Length of the trip in days.",
                    "minimum": 1,
                },
                "trip_type": {
                    "type": "string",
                    "description": "The primary nature of the trip.",
                    "enum": ["business", "leisure", "beach", "hiking", "snow", "camping"],
                },
                "month": {
                    "type": "string",
                    "description": "The month of travel (to help estimate weather if not provided explicitly).",
                },
                "weather_context": {
                    "type": "string",
                    "description": "Current weather conditions known for the destination (e.g. 'rainy, 20C').",
                }
            },
            "required": ["destination", "duration_days", "trip_type"],
        },
    },
]
