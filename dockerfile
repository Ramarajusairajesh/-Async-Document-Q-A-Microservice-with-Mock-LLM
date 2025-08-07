FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Do not cache pip packages, reduces image size
# --upgrade pip: Ensure pip is up-to-date
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application using Uvicorn
# The --host 0.0.0.0 makes the server accessible from outside the container
# The --reload flag is useful for development but should be removed in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
