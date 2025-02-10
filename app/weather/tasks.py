import os
import httpx
import json
import re
from dotenv import load_dotenv
from transliterate import translit

from celery import shared_task

from app.logger import logger
from app.providers import get_weather_service


load_dotenv()


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
    weather_service = get_weather_service()
    task_id = get_weather.request.id
    result_url = []
    with httpx.Client() as client:
        for city in cities:

            city_latin = _translator_city_name_to_english(city)

            try:
                data = weather_service.fetch_weather(city_latin, client)

                if -50 <= data["temperature"] <= 50:
                    logger.error("Invalid temperature for the city: %s", city_latin)
                    continue

                dir_path = f"app/weather/weather_data/{data["region"]}"
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

                existing_data.append(data)

                with open(file_path, "w") as f:
                    json.dump(existing_data, f, indent=4)

                path_to_file = f"weather_data/{data["region"]}/task_{task_id}.json"
                if path_to_file not in result_url:
                    result_url.append(path_to_file)

            except Exception as e:
                logger.error("An unexpected error occurred: %s", e)

        return {"result_url": result_url}
