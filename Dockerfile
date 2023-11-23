FROM python:3.9.18

WORKDIR /code

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip

