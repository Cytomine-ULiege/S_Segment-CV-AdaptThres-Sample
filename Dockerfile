FROM cytomineuliege/software-python3-base:v2.2.0-py3.6.8

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
