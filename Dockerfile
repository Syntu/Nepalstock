# Use the full Python image (not slim) to avoid issues
FROM python:3.9

# Set working directory
WORKDIR /app

# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Copy code to container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run bot
CMD ["python", "main.py"]
