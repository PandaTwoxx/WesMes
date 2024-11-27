#!/bin/bash

npm install
npx tailwindcss -i ./service/static/input.css -o ./service/static/output.css
python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry export -f requirements.txt --output requirements.txt --without-hashes
if [ $# -eq 0 ]
then
    docker compose up --watch
elif [ $1 -eq 1 ]
then
    docker compose up --build --watch
fi