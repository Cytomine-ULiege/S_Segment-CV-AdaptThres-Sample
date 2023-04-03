FROM python:3.8-slim-bullseye

RUN python -m pip install -U --force-reinstall pip
RUN apt-get update -y && apt-get install -y git libgeos-dev libglib2.0-0

RUN pip3 install git+https://github.com/cytomine-uliege/Cytomine-python-client.git@v2.9.0

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
