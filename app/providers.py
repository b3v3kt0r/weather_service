from abc import ABC, abstractmethod
import json
import os
import httpx
from dotenv import load_dotenv

from app.logger import logger


load_dotenv()


class WeatherService(ABC):
    """
    Base class for weather.
    """

    @abstractmethod
    def fetch_weather(self, city: str, client) -> dict:
        """
        Method for receiving weather data.
        """


class WeatherAPIService(WeatherService):
    """
    Class for realization weather data via WeatherApi.com.
    """

    API_KEY = os.getenv("WEATHERAPI_API_KEY")
    BASE_URL = os.getenv("WEATHERAPI_API_URL")

    def fetch_weather(self, city: str, client):
        """
        Method for receiving weather data.
        """
        try:
            response = client.get(
                self.BASE_URL, params={"key": self.API_KEY, "q": city}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "city": city,
                "temperature": data["current"]["temp_c"],
                "description": data["current"]["condition"]["text"],
                "region": data["location"]["tz_id"].split("/")[0],
            }
        except httpx.RequestError as e:
            logger.error("Network or HTTP error occurred: %s", e)
        except json.JSONDecodeError:
            logger.error("Error decoding JSON response.")
        except KeyError as e:
            logger.error("Missing expected key in the response: %s", e)
        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)


class OpenWeatherAPIService(WeatherService):
    """
    Class for realization weather data via OpenWeather.com.
    """

    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    BASE_URL = os.getenv("OPENWEATHER_API_URL")

    def _get_continent_by_country_code(self, country_code):
        """
        Method that helps receive name of continent for the city.
        """
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        response = httpx.get(url)
        data = response.json()
        region = data[0].get("continents", ["Unknown"])[0]
        if "America" in region:
            return "America"
        return region

    def _city_to_geolocation(self, city):
        """
        Method that helps receive Latitude and Longitude for the city.
        """
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={self.API_KEY}"
        with httpx.Client() as client:
            response = client.get(url)
            data = response.json()
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            return [f"{lat:.2f}", f"{lon:.2f}"]

    def fetch_weather(self, city, client):
        """
        Method for receiving weather data.
        """
        with httpx.Client() as client:
            try:
                location = self._city_to_geolocation(city)
                url = f"{self.BASE_URL}lat={location[0]}&lon={location[1]}&appid={self.API_KEY}"
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                region = self._get_continent_by_country_code(data["sys"]["country"])
                return {
                    "city": city,
                    "temperature": round(data["main"]["temp"] - 273.15, 2),
                    "description": data["weather"][0]["description"].capitalize(),
                    "region": region,
                }

            except httpx.RequestError as e:
                logger.error("Network or HTTP error occurred: %s", e)
            except json.JSONDecodeError:
                logger.error("Error decoding JSON response.")
            except KeyError as e:
                logger.error("Missing expected key in the response: %s", e)
            except Exception as e:
                logger.error("An unexpected error occurred: %s", e)


def get_weather_service() -> WeatherService:
    """
    Determines which service to use, depending on the API key.
    """
    if os.getenv("WEATHERAPI_API_KEY"):
        return WeatherAPIService()
    elif os.getenv("OPENWEATHER_API_KEY"):
        return OpenWeatherAPIService()
    else:
        logger.error("No API key found! Unable to get weather.")
        raise ValueError("No API key found! Unable to get weather.")
