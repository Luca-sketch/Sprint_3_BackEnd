FROM python:3.12.0

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]



