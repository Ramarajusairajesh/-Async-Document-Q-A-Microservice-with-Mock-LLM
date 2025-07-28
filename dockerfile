# Dockerfile for the FastAPI Q&A Microservice

# Use a lightweight Python base image. Python 3.10 is specified in requirements.txt
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
# This step is done early to leverage Docker's build cache
COPY requirements.txt .
ENV PYTHONPATH=/app

# Install Python dependencies
# --no-cache-dir: Prevents pip from storing cached data, reducing image size
# --upgrade pip: Ensures pip is up-to-date
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes main.py, config.py, database.py, models.py, schemas.py, services.py, and the routers/ directory
COPY . .

# Expose the port FastAPI will run on. This matches SERVER_PORT in .env.example.
EXPOSE 8000

# Command to run the application using Uvicorn
# "main:app" refers to the 'app' FastAPI instance in 'main.py'
# --host 0.0.0.0 makes the server accessible from outside the container
# --port 8000 specifies the port to listen on, matching EXPOSE and SERVER_PORT
# Note: The --reload flag (often used in development) is typically omitted in production Dockerfiles
# for performance reasons, but it's included here as it's common for development setups.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

