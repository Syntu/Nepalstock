# Use official Python 3.9 slim image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install dependencies
RUN apt-get update && apt-get install -y python3-pip \
    && pip3 install --no-cache-dir -r requirements.txt

# Expose the port (even though your bot may not need this, just in case)
EXPOSE 8000

# Run the bot
CMD ["python", "main.py"]
