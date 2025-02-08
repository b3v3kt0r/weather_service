import os
import httpx
import json
import re
from dotenv import load_dotenv
from transliterate import translit

from celery import shared_task

from app.logger import logger


load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL")

def _translator_city_name_to_english(city: str):
    """
    Function that translates city name to English.
    """
    cyrillic = r"^[а-яА-ЯёЁіІїЇєЄґҐа-ґ\s\-']+$"
    if re.match(cyrillic, city):
        return translit(city, reversed=True)
    return city


@shared_task
def get_weather(cities: list) -> dict | None:
    """
    Function that allows to get weather information for list of cities.
    """
    task_id = get_weather.request.id
    result_url = []
    with httpx.Client() as client:
        for city in cities:

            city_latin = _translator_city_name_to_english(city)

            try:
                response = client.get(BASE_URL, params={"key": API_KEY, "q": city_latin})
                response.raise_for_status()
                data = response.json()

                data_to_file = {
                    "city": city_latin,
                    "temperature": data["current"]["temp_c"],
                    "description": data["current"]["condition"]["text"],
                }

                region = data["location"]["tz_id"].split("/")[0]
                dir_path = f"app/weather/weather_data/{region}"
                os.makedirs(dir_path, exist_ok=True)
                file_path = f"{dir_path}/task_{task_id}.json"

                existing_data = []
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r") as f:
                            existing_data = json.load(f)
                            if not isinstance(existing_data, list):
                                existing_data = [existing_data]
                    except json.JSONDecodeError:
                        existing_data = []

                existing_data.append(data_to_file)

                with open(file_path, "w") as f:
                    json.dump(existing_data, f, indent=4)

                path_to_file = f"weather_data/{region}/task_{task_id}.json"
                if path_to_file not in result_url:
                    result_url.append(path_to_file)

            except httpx.RequestError as e:
                logger.error("Network or HTTP error occurred: %s", e)
            except json.JSONDecodeError:
                logger.error("Error decoding JSON response.")
            except KeyError as e:
                logger.error("Missing expected key in the response: %s", e)
            except Exception as e:
                logger.error("An unexpected error occurred: %s", e)

    return {"result_url": result_url}
