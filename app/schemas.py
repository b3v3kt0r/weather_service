from typing import List, Optional
from pydantic import BaseModel


class CitiesList(BaseModel):
    """
    Model for accepting list of cities.
    """
    cities: List[str] = []


class TaskID(BaseModel):
    """
    Model for responding of task id.
    """
    task_id: str


class TaskStatus(BaseModel):
    """
    Model for responding of task status and link.
    """
    task_id: str
    status: str
    result_urls: Optional[List[str]]


class CityWeather(BaseModel):
    """
    Model for responding of cities and weather.
    """
    city: str
    temperature: str
    description: str

    def __eq__(self, other):
        if isinstance(other, CityWeather):
            return self.city == other.city
        return False
    
    def __hash__(self):
        return hash(self.city)


class Weather(BaseModel):
    """
    Model for responding weather, regions, cities.
    """
    region: str
    results: List[CityWeather]
