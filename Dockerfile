FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim-2021-10-02

WORKDIR /usr/src/app

RUN apt-get update && apt-get install curl -y

COPY requirements.txt ./

# Copy the .env file to the image
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file to the image
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000
ENV UVICORN_WORKERS=2

COPY . .

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
