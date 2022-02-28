FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication/application.py ./application.py
COPY authentication/adminDecoration.py ./adminDecoration.py
COPY authentication/models.py ./models.py
COPY authentication/configurations.py ./configurations.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]