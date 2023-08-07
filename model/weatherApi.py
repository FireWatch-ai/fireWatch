import requests

class temp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.temperature = self.main()

    def get_historical_weather(self, api_key, latitude, longitude, date):
        base_url = "http://api.weatherapi.com/v1/history.json"
        params = {
            "key": api_key,
            "q": f"{latitude},{longitude}",
            "dt": date,
            "end_dt": date,
            "hour": 0,
            "units": "metric"
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            print("Error while fetching weather data:", e)
            return None

    def main(self):
        api_key = "9352563de1bf43599ca193930230308"
        latitude = self.x
        longitude = self.y
        date = "2023-08-07"

        weather_data = self.get_historical_weather(api_key, latitude, longitude, date)

        if weather_data and "forecast" in weather_data:
            # Extract relevant weather information from the response data
            weather_description = weather_data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
            temperature = weather_data["forecast"]["forecastday"][0]["day"]["avgtemp_c"]
            humidity = weather_data["forecast"]["forecastday"][0]["day"]["avghumidity"]

            weather_conditions = [weather_description, temperature, humidity]
            return weather_conditions
        else:
            print("Weather data not available for the specified date.")
            return None

