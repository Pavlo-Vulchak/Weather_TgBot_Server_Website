FROM python:3.10-slim
WORKDIR /bot
# Install python requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /bot
CMD ["python", "wetherserv.py"]