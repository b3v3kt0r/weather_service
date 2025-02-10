import traceback

from fastapi import FastAPI, HTTPException, Request
from celery.result import AsyncResult

from app.schemas import CitiesList, TaskID, TaskStatus, RegionWeather
from app.celery_ import celery_app
from app.weather.tasks import get_weather
from app.weather.utils import get_weather_for_cities_in_region
from app.logger import logger


app = FastAPI()


@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    """
    Middleware for logging.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        error_message = (
            f"URL: {request.url} - Exception: {str(e)}\n{traceback.format_exc()}"
        )
        logger.error(error_message)
        raise e


@app.post("/weather/")
async def send_list_of_city(cities: CitiesList):
    """
    Function that allows to send list of cities for processing.
    """
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
            task_id=task_id, status=task_res.state, result_urls=result_urls
        )

    elif task_res.state == "FAILURE":
        return TaskStatus(task_id=task_id, status=task_res.state, result_urls=None)

    else:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id: {task_id} was not found or in progress",
        )


@app.get("/results/{region}")
async def get_weather_results(region: str):
    """
    Function that allows to get weather for cities in region.
    """
    weather_data = await get_weather_for_cities_in_region(region)
    return RegionWeather(region=region, results=weather_data)
