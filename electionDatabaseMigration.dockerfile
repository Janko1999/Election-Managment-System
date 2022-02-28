FROM python:3

RUN mkdir -p /opt/src/migrationElection
WORKDIR /opt/src/migrationElection

COPY Elections/migrations.py ./migrations.py
COPY Elections/configurations.py ./configurations.py
COPY Elections/models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python", "./migrations.py"]