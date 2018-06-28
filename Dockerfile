
FROM cytomineuliege/software-python3-base

WORKDIR /app

ADD run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
