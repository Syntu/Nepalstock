# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (not strictly necessary for Telegram bots)
EXPOSE 8000

# Run the bot
CMD ["python", "main.py"]