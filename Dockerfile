FROM python:3.12.0-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "CompoundingSimulator.py", "--server.port=8080", "--server.address=0.0.0.0"]
