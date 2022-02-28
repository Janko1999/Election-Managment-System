FROM python:3

RUN mkdir -p /opt/src/migrationAuthentification
WORKDIR /opt/src/migrationAuthentification

COPY authentication/migrations.py ./migrations.py
COPY authentication/configurations.py ./configurations.py
COPY authentication/models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python", "./migrations.py"]