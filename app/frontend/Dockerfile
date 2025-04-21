FROM python:3.13-slim

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8001", "--browser.gatherUsageStats", "false" ]
