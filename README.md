## This is a project for playing with fastapi and docker for microservice app


## How to run
1. Install docker
2. Install docker-compose
3. Create a `.env.dev` and `.env` files in the root directory with the contents presented in the `.env.dev.example` and `.env.example` files.
4. In the terminal run `docker-compose -f docker-compose-dev.yml --env-file .env.dev up --env-file .env -d --build` for testing dev app locally.
5. Go to `http://localhost:8000/docs` to see the swagger docs
6. Go to `http://localhost:8000/redoc` to see the redoc docs
7. Go to `http://localhost:8000/api/v1/messages` to send requests
