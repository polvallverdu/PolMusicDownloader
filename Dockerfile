FROM python:3.10.6-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY requirements_torch.txt requirements_torch.txt
RUN pip3 install -r requirements_torch.txt

COPY . .

ENV RABBITMQ_URI="amqp://guest:guest@localhost:49154/"
ENV VOLUME="../songs"
ENV TIDAL_USERNAME="XD"
ENV TIDAL_PASSWORD="XD"

CMD [ "python3", "main.py"]
