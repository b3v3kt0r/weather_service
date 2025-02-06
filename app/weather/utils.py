import os
from celery import shared_task
import httpx
import json
from dotenv import load_dotenv

from app.schemas import CityWeather


load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL")


@shared_task
def get_weather(cities: list) -> dict | None:
    """
    Function that allows to get weather information for list of cities.
    """
    task_id = get_weather.request.id
    result_url = None
    with httpx.Client() as client:
        for city in cities:
            try:
                response = client.get(BASE_URL, params={"key": API_KEY, "q": city})
                response.raise_for_status()
                data = response.json()

                data_to_file = {
                    "city": city,
                    "temperature": data["current"]["temp_c"],
                    "description": data["current"]["condition"]["text"]
                }

                region = data["location"]["tz_id"].split("/")[0]
                dir_path = f"app/weather/weather_data/{region}"
                file_path = f"{dir_path}/{task_id}.json"
                os.makedirs(dir_path, exist_ok=True)

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

                result_url = f"weather_data/{region}/{task_id}.json"

            except httpx.RequestError as e:
                print(f"Network or HTTP error occurred: {e}")
                return None
            except json.JSONDecodeError:
                print("Error decoding JSON response.")
                return None
            except KeyError as e:
                print(f"Missing expected key in the response: {e}")
                return None
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None

    return {"result_url": result_url}


def get_weather_for_cities_in_region(region: str):
    """
    Function that read information about weather for all cities in region.
    """
    data = []
    directory_path = f"app/weather/weather_data/{region}"

    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)

        with open(file_path, "r") as f:
            file_data = json.load(f)

            for city_weather in file_data:
                city_weather_data = CityWeather(
                    city=city_weather["city"],
                    temperature=str(city_weather["temperature"]),
                    description=city_weather["description"]
                )
                data.append(city_weather_data)

    return data
