## Weather service API

This project is a FastAPI application that allows sending a list of cities and receiving weather.

## Installation

To get started, clone the repository and set up a virtual environment.

```shell
# Clone the repository
git clone https://github.com/b3v3kt0r/weather_service

# Set up .env file
You have create .env using .env.sample. like example

# Build and run docker-compose container
docker compose up --build   

# Check it out
http://127.0.0.1:8000/docs/
```

## Configuration

Create .env file in the root directory and add your configuration using .env.sample like example.

Logs will be available in 'api_errors.log' file.

## API Endpoints

  - POST /weather/: Send list of cities.
  - GET /tasks/{task_id}: Retrieve details about specific task.
  - GET /results/{region}/: Retrieve weather of a specific region.

## Contact
For contact me:
* Fullname: Stanislav Sudakov
* Email: stanislav.v.sudakov@gmail.com
* Telegram: @sssvvvff
