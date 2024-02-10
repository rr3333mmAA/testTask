FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000