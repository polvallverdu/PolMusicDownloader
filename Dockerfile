FROM python:3.10.6-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY requirements_torch.txt requirements_torch.txt
RUN pip3 install -r requirements_torch.txt

COPY . .

CMD [ "python3", "main.py"]
