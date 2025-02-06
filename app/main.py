from fastapi import FastAPI
from celery.result import AsyncResult

from app.schemas import CitiesList, TaskID, TaskStatus, Weather
from app.celeryy import celery_app
from app.weather.utils import get_weather, get_weather_for_cities_in_region

app = FastAPI()


@app.post("/weather/")
async def send_list_of_city(cities: CitiesList):
    """
    Function that allows to send list of cities for processing.
    """
    task = get_weather.delay(cities.cities)
    return {"task_id": task.id}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """
    Function that allows to get tasks id, status, path to result.
    """
    task_res = AsyncResult(task_id, app=celery_app)

    if task_res.state == "SUCCESS":
        result = task_res.result
        result_url = result.get("result_url", None)
        return TaskStatus(
            task_id=task_id,
            status=task_res.state,
            result_url=result_url
        )

    elif task_res.state == "FAILURE":
        return TaskStatus(
            task_id=task_id,
            status=task_res.state,
            result_url=None
        )

    else:
        return TaskStatus(
            task_id=task_id,
            status=task_res.state,
            result_url=None
        )


@app.get("/results/{region}")
async def get_weather_results(region: str):
    """
    Function that allows to get weather for cities in region.
    """
    weather_data = get_weather_for_cities_in_region(region)
    return Weather(region=region, results=weather_data)
