FROM python:3

RUN mkdir -p /opt/src/election/user
WORKDIR /opt/src/election/user

COPY Elections/User/application.py ./application.py
COPY Elections/models.py ./models.py
COPY Elections/User/Configurations.py ./Configurations.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]