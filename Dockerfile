
FROM cytomineuliege/software-python3-base:v2.2.0-py3.6.8

RUN pip install opencv-python-headless==4.1.0.25

ADD run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
