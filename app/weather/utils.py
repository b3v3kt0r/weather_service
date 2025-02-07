import os
import re
import httpx
import json
from dotenv import load_dotenv

from transliterate import translit
from fastapi import HTTPException
from celery import shared_task

from app.schemas import CityWeather


load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL")


def _translator_city_name_to_english(city: str):
    """
    Function that translates city name to English.
    """
    cyrylic = r"^[а-яА-ЯёЁіІїЇєЄґҐа-ґ\s\-']+$"
    if re.match(cyrylic, city):
        return translit(city, reversed=True)
    return city


def _validate_city_spelling(city: str):
    """
    Function that validates city for allowed symbols.
    Checks if a city consists of letters, spaces, and hyphens.
    """
    pattern = r"^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐа-ґ\s\-']+$"
    return bool(re.match(pattern, city))


@shared_task
def get_weather(cities: list) -> dict | None:
    """
    Function that allows to get weather information for list of cities.
    """
    task_id = get_weather.request.id
    result_url = []
    with httpx.Client() as client:
        for city in cities:

            checker = _validate_city_spelling(city)
            if checker is False:
                print(f"City {city} failed validation")
                continue

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
                print(f"Network or HTTP error occurred: {e}")
            except json.JSONDecodeError:
                print("Error decoding JSON response.")
            except KeyError as e:
                print(f"Missing expected key in the response: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    return {"result_url": result_url}


def get_weather_for_cities_in_region(region: str):
    """
    Function that read information about weather for all cities in region.
    """
    data = set()
    directory_path = f"app/weather/weather_data/{region}"

    if not os.path.exists(directory_path):
        raise HTTPException(
            status_code=404, detail=f"Data for region {region} not found"
        )

    files = sorted(
        os.listdir(directory_path),
        key=lambda file: os.path.getmtime(os.path.join(directory_path, file)),
        reverse=True,
    )

    for file in files:
        file_path = os.path.join(directory_path, file)

        with open(file_path, "r") as f:
            file_data = json.load(f)

            for city_weather in file_data:
                city_weather_data = CityWeather(
                    city=city_weather["city"],
                    temperature=str(city_weather["temperature"]),
                    description=city_weather["description"],
                )
                data.add(city_weather_data)

    return list(data)
