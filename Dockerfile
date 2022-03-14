
FROM cytomine/software-python3-base:v2.2.2

RUN pip install opencv-python-headless==4.1.2.30

ADD descriptor.json /app/descriptor.json
ADD run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
