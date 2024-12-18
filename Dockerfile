FROM python:3.9-slim

WORKDIR /app

# Install pip manually if it's missing
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "bot.py"]
