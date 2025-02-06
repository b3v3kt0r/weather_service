import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

# from app.schemas import CitiesList


load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL")


async def get_weather(cities: list) -> dict | None:
    """
    Function that allows to get weather information for list of cities.
    """
    async with httpx.AsyncClient() as client:
        for city in cities:
            try:
                response = await client.get(BASE_URL, params={"key": API_KEY, "q": city})
                response.raise_for_status()
                data = response.json()

                data_to_file = {
                    "city": city,
                    "temperature": data["current"]["temp_c"],
                    "description": data["current"]["condition"]["text"]
                }

                region = data["location"]["tz_id"].split("/")[0]
                dir_path = f"weather/weather_data/{region}"
                file_path = f"{dir_path}/{data["location"]["name"]}"
                os.makedirs(dir_path, exist_ok=True)

                with open(file_path, "w") as f:
                    json.dump(data_to_file, f, indent=4)

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

async def ge():
    res = await get_weather(cities=["Kyiv", "Pekin"])
    print(res)

asyncio.run(ge())
