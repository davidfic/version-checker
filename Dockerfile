# FROM python:3.8.0-alpine3.10
FROM python:3.7-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
# RUN mkdir /app
COPY . ./
RUN pip install Flask gunicorn requests bs4
RUN pip install -r /app/requirements.txt
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 app:app
