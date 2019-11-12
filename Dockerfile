
FROM cytomineuliege/software-python3-base:v2.2.0-py3.6.8

RUN mkdir -p /app

ADD run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
