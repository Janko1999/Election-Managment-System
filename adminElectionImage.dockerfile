FROM python:3

RUN mkdir -p /opt/src/election/admin
WORKDIR /opt/src/election/admin

COPY Elections/Admin/application.py ./application.py
COPY Elections/Admin/adminDecoration.py ./adminDecoration.py

COPY Elections/models.py ./models.py
COPY Elections/configurations.py ./Configurations.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]