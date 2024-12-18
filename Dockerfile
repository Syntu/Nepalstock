# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Uninstall conflicting libraries and install required dependencies
RUN pip uninstall telegram -y && pip install python-telegram-bot==20.3 \
    && pip install --no-cache-dir -r requirements.txt

# Expose port (if necessary, though Telegram bot doesn't use it)
EXPOSE 8000

# Run the bot
CMD ["python", "bot.py"]
