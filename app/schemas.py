from typing import List, Optional
from pydantic import BaseModel


class CitiesList(BaseModel):
    """
    Model for accepting list of cities.
    """
    name: List[str]


class TaskID(BaseModel):
    """
    Model for responding of task id.
    """
    id: str


class TaskStatus(BaseModel):
    """
    Model for responding of task status and link.
    """
    id: str
    status: str
    result_url: Optional[str]


class CityWeather(BaseModel):
    """
    Model for responding of cities and weather.
    """
    city: str
    temperature: str
    description: str


class Weather(BaseModel):
    """
    Model for responding weather, regions, cities.
    """
    region: str
    results: List[CityWeather]
