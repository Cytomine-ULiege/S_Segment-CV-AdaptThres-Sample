
FROM cytomineuliege/software-python3-base:latest

RUN mkdir -p /app

ADD run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
