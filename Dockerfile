FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install curl -y

COPY requirements.txt ./

# Copy the .env file to the image
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
