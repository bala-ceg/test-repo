# Start from a slim Python base image
FROM python:3.10-slim

# Prevent Python from writing bytecode (.pyc) files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python prints output directly to terminal
ENV PYTHONUNBUFFERED 1
# Set timezone to UTC
ENV TZ=UTC

# Set the working directory within the Docker container
WORKDIR /app

# Install dependencies
COPY ./src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy your application code and other necessary files
COPY ./src .

# Expose port 8000 for the application
EXPOSE 8000

# Use a non-root user to run the application (optional, but recommended for security)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000", "--no-server-header"]
