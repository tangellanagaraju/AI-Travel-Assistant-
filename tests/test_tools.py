import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent dir to path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_implementations import (
    get_current_weather,
    get_weather_forecast,
    search_attractions,
    calculate_travel_distance,
    get_packing_suggestions
)

class TestTools(unittest.TestCase):

    def test_get_packing_suggestions(self):
        # Test basic logic
        result = get_packing_suggestions(
            destination="Hawaii",
            duration_days=5,
            trip_type="beach"
        )
        data = json.loads(result)
        self.assertIn("swimsuit", data["recommendations"]["clothing"])
        self.assertEqual(data["destination"], "Hawaii")

    def test_get_packing_suggestions_weather_context(self):
        # Test weather influence
        result = get_packing_suggestions(
            destination="London",
            duration_days=3,
            trip_type="business",
            weather_context="Rainy, 10C"
        )
        data = json.loads(result)
        self.assertIn("raincoat", data["recommendations"]["clothing"])
        self.assertIn("blazer", data["recommendations"]["clothing"])

    def test_search_attractions_mock(self):
        # Test Paris mock
        result = search_attractions("Paris", "museum")
        data = json.loads(result)
        self.assertTrue(len(data["results"]) > 0)
        self.assertEqual(data["results"][0]["name"], "Louvre Museum")
        
    def test_search_attractions_filter(self):
        # Test filtering
        result = search_attractions("Paris", "museum", min_rating=5.0) # Should be empty/few
        data = json.loads(result)
        # Louvre is 4.9, so if we ask for 5.0 it might be empty
        self.assertEqual(len(data["results"]), 0)

    def test_calculate_travel_distance_mock(self):
        result = calculate_travel_distance("London", "Paris", "driving")
        data = json.loads(result)
        self.assertIn("450 km", data["distance"])

    @patch('requests.get')
    def test_get_current_weather_api(self, mock_get):
        # Mock geocoding then weather
        mock_response_geo = MagicMock()
        mock_response_geo.json.return_value = {"results": [{"latitude": 10.0, "longitude": 20.0}]}
        mock_response_geo.status_code = 200
        
        mock_response_weather = MagicMock()
        mock_response_weather.json.return_value = {
            "current_weather": {
                "temperature": 25,
                "windspeed": 10,
                "weathercode": 0
            }
        }
        mock_response_weather.status_code = 200

        mock_get.side_effect = [mock_response_geo, mock_response_weather]

        result = get_current_weather("Test City")
        data = json.loads(result)
        self.assertEqual(data["temperature"], "25°C")
        self.assertEqual(data["conditions"], "Clear")

if __name__ == '__main__':
    unittest.main()
