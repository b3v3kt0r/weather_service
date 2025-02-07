from fastapi import FastAPI, HTTPException
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
    if not isinstance(cities.cities, list) or len(cities.cities) == 0:
        raise HTTPException(
            status_code=400,
            detail="The cities parameter must be a non-empty list."
        )
    task = get_weather.delay(cities.cities)
    return TaskID(task_id=task.id)


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """
    Function that allows to get tasks id, status, path to result.
    """
    task_res = AsyncResult(task_id, app=celery_app)

    if task_res.state == "SUCCESS":
        result = task_res.result
        result_urls = result.get("result_url", None)
        if isinstance(result_urls, str):
            result_urls = [result_urls]
        return TaskStatus(
            task_id=task_id,
            status=task_res.state,
            result_urls=result_urls
        )

    elif task_res.state == "FAILURE":
        return TaskStatus(
            task_id=task_id,
            status=task_res.state,
            result_url=None
        )

    else:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id: {task_id} was not found or in progress"
        )


@app.get("/results/{region}")
async def get_weather_results(region: str):
    """
    Function that allows to get weather for cities in region.
    """
    weather_data = get_weather_for_cities_in_region(region)
    return Weather(region=region, results=weather_data)
