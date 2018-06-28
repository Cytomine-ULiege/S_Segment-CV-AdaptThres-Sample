
FROM cytomineuliege/software-python3-base:latest

WORKDIR /app

ADD run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
