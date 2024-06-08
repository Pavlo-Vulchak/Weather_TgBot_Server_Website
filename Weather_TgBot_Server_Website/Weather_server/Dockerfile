FROM python:3.10-slim
WORKDIR /bot
RUN pip install paho-mqtt
COPY . /bot
CMD ["python", "wetherserv.py"]