#FROM python:3.10.3
FROM nginx/unit:1.23.0-python3.9

COPY ./config/config.json /docker-entrypoint.d/config.json

#EXPOSE 5000

RUN mkdir build
RUN mkdir build/app

COPY ./app/requirements.txt ./build

RUN pip install --no-cache-dir -r ./build/requirements.txt

COPY ./app/data.pck ./build/app
COPY ./app/main.py ./build/app
COPY ./app/__init__.py ./build/app


#CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000" ]
EXPOSE  80