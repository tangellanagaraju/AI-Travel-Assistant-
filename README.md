# Smart Weather & Travel Assistant

A intelligent travel assistant agent powered by **LangGraph** and **Gemini 2.0 Flash**. This assistant helps users plan trips by providing real-time weather, attraction searches, travel advice, and packing lists.

## Features

-   **Weather Information**: Get current weather and 5-day forecasts for any city.
-   **Attraction Search**: Find museums, parks, restaurants, and landmarks.
-   **Travel Distance**: Calculate distance and time between locations.
-   **Packing Suggestions**: Smart packing lists based on destination weather and trip type.
-   **Conversational Agent**: Maintains context across multiple turns to assist with complex planning.

## Architecture

The system uses a **LangGraph** state graph to manage the agent's execution flow:
1.  **Agent Node**: Calls the Gemini LLM with tool definitions.
2.  **Tool Node**: Executes the requested Python functions (tools).
3.  **State**: Maintains a history of messages (Human, AI, Tool results).

### Tools
-   `get_current_weather` & `get_weather_forecast`: Uses Open-Meteo API.
-   `search_attractions`, `calculate_travel_distance`: Mocked with realistic data for demo purposes.
-   `get_packing_suggestions`: Logic-based recommendation engine.

## Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd Smart Weather_Travel Assistant
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**:
    -   Open `agent.py` and set `GOOGLE_API_KEY` (or set it as an environment variable).
    -   *Note: The project currently requires a valid Gemini API key.*

## Usage

Run the interactive CLI:

```bash
python agent.py
```

**Example Commands**:
-   "What's the weather in Tokyo?"
-   "I'm going to Paris for 5 days. What should I pack?"
-   "Find me some museums in London."

## Testing

Run unit tests:
```bash
python -m unittest tests/test_tools.py
```

Run demo scenarios (requires valid API key):
```bash
python tests/demo_runner.py
```

## Design Decisions

-   **LangGraph**: Chosen for its robust state management and ability to handle cyclic agent flows (Agent -> Tool -> Agent).
-   **Gemini 2.0 Flash**: Selected for speed and strong function-calling capabilities.
-   **Tool Schemas**: Defined in standard OpenAI/JSON schema format for maximum compatibility.
-   **Mocking vs Real APIs**: Open-Meteo is used for weather to prove real API integration capability, while Attractions/Distance are mocked to ensure demo reliability without managing multiple complex API keys (Google Maps, Yelp, etc.).

## Future Improvements

-   Integrate real Google Maps API for distance and places.
-   Add a persistent database (SQLite/PostgreSQL) for user sessions.
-   Build a web interface (Streamlit or React) instead of CLI.
-   Add more sophisticated trip planning logic (budgeting, itinerary generation).
