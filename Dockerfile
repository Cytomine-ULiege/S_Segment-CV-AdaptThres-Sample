
FROM cytomineuliege/software-python3-base

ADD run.py .

ENTRYPOINT ["python", "run.py"]
