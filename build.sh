#!/bin/bash
npx tailwindcss -i ./service/input.css -o ./service/static/output.css --watch
poetry export -f requirements.txt --output requirements.txt --without-hashes