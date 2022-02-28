FROM python:3

RUN mkdir -p /opt/src/deamon
WORKDIR /opt/src/deamon

COPY Elections/Deamon/application.py ./application.py

COPY Elections/models.py ./models.py
COPY Elections/configurations.py ./Configurations.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]