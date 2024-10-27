# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
EXPOSE 6379
COPY . .
CMD ["python3", "launch.py"]