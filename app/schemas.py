import re
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.logger import logger


class CitiesList(BaseModel):
    """
    Model for accepting a list of cities with validation.
    """

    cities: List[str]

    @field_validator("cities", mode="before")
    @classmethod
    def validate_cities(cls, value):
        """
        Method that validates city for allowed symbols.
        Checks if a city consists of letters, spaces, and hyphens.
        """
        pattern = r"^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\s\-']+$"
        for city in value:
            if not isinstance(city, str) or not re.match(pattern, city):
                logger.error("Validation error: Invalid city name: %s", city)
                raise ValueError(f"Invalid city name: {city}")

        return value


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


class RegionWeather(BaseModel):
    """
    Model for responding weather, regions, cities.
    """

    region: str
    results: List[CityWeather]
