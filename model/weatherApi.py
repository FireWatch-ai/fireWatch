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
            "end_dt": date,  # Same date for the end_dt will get data for the specified date only
            "hour": 0,       # Hour is set to 0 for getting data for the whole day
            "units": "metric"
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Check for any request errors

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            print("Error while fetching weather data:", e)
            return None

    def main(self):
        # Replace YOUR_API_KEY with your actual API key from Weatherapi.com
        api_key = "9352563de1bf43599ca193930230308"
        latitude = self.x  # Replace with your desired latitude
        longitude = self.y  # Replace with your desired longitude
        date = "2023-08-05"  # Replace with the desired date in the format "YYYY-MM-DD"

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


