import os
import json

from fastapi import HTTPException

from app.schemas import CityWeather


async def get_weather_for_cities_in_region(region: str):
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
