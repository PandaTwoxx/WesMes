#!/bin/bash

npm install tailwindcss@latest
npm install postcss-import@latest
npx tailwindcss -i ./service/input.css -o ./service/static/output.css
poetry export -f requirements.txt --output requirements.txt --without-hashes
if [ $# -eq 0 ]
then
    docker compose up
elif [ $1 -eq 1 ]
then
    docker compose up --build
fi