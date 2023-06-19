FROM python:3.11.3-buster

ENV PYTHONPATH=$PYTHONPATH:/usr/src/app/

RUN apt-get update && apt-get -y upgrade && apt-get clean

WORKDIR /usr/src/app/

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY ./Diploma /usr/src/app/


CMD ["/bin/bash", "-c", "exec invoke run"]
