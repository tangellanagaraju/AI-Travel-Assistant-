# Smart Weather & Travel Assistant

An intelligent travel assistant agent powered by **LangGraph** and **OpenAI GPT-4o**. This assistant helps users plan trips by providing real-time weather, attraction searches, travel advice, and packing lists.

## Features

- **Weather Information**: Get current weather and 5-day forecasts for any city.
- **Attraction Search**: Find museums, parks, restaurants, and landmarks.
- **Travel Distance**: Calculate distance and time between locations.
- **Packing Suggestions**: Smart packing lists based on destination weather and trip type.
- **Conversational Agent**: Maintains context across multiple turns to assist with complex planning.
- **Modern Web UI**: A Django-based web interface with glassmorphism design and real-time chat.

## Project Structure

```text
├── agent.py                 # Core LangGraph agent logic
├── tool_implementations.py  # Python functions for tools (Weather, Packing, etc.)
├── tool_schemas.py          # JSON schemas for tool calling compatibility
├── manage.py                # Django management script
├── weather_project/         # Django project configuration
├── chat/                    # Chat application logic (Views, Consumers, Templates)
│   ├── templates/chat/      # Modern Glassmorphism UI templates
│   ├── consumers.py         # WebSocket handling for real-time chat
│   └── models.py            # Persistence for chat history
├── tests/                   # Unit tests and demo scripts
└── requirements.txt         # Project dependencies
```

## Architecture

The system uses a **LangGraph** state graph to manage the agent's execution flow:
1. **Agent Node**: Calls the OpenAI model with tool definitions.
2. **Tool Node**: Executes the requested Python functions (tools).
3. **State**: Maintains a history of messages (Human, AI, Tool results).

### Tools
- `get_current_weather` & `get_weather_forecast`: Uses Open-Meteo API.
- `search_attractions`, `calculate_travel_distance`: Mocked with realistic data for demo purposes.
- `get_packing_suggestions`: Logic-based recommendation engine.

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tangellanagaraju/AI-Travel-Assistant-.git
   cd AI-Travel-Assistant-
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   - Set your OpenAI API key in `agent.py` or as an environment variable `OPENAI_API_KEY`.

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

## Usage

### Web Interface (Recommended)
Run the Django development server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/chat/` to interact with the sleek glassmorphism UI.

### CLI Mode
Run the interactive CLI:
```bash
python agent.py
```

## Testing

Run unit tests:
```bash
python -m unittest tests/test_tools.py
```

## Design Decisions

- **LangGraph**: Chosen for its robust state management and ability to handle cyclic agent flows (Agent -> Tool -> Agent).
- **GPT-4o**: Selected for superior reasoning and tool-calling accuracy.
- **Django Channels**: Used for real-time WebSocket communication in the web UI.
- **Glassmorphism UI**: Implemented to provide a premium, modern user experience.

## Future Improvements

- Integrate real Google Maps API for distance and places.
- Add support for file uploads (itineraries, tickets).
- Implement user authentication and personalized travel profiles.
- Add more sophisticated trip planning logic (budgeting, itinerary generation).

