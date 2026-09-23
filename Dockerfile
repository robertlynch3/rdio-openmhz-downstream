FROM python:3.11
RUN apt update && apt install ffmpeg -y
ADD ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

ADD server.py /
ADD gunicorn.py /

CMD ["gunicorn", "server:app", "--config", "/gunicorn.py"]