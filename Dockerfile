FROM ubuntu:latest
WORKDIR /app

RUN apt-get -y update && apt-get install -y --no-install-recommends python3 python3-pip ffmpeg

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD python3 main.py