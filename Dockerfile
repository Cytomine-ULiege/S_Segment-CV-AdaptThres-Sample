FROM cytomine/software-python3-base:v2.2.2

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
