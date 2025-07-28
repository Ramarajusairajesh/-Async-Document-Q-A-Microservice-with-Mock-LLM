AI Document Q&A Microservice

This project implements a Python backend microservice using FastAPI and PostgreSQL to manage documents and answer questions about them using a simulated LLM.
🎯 Objective

To build a robust backend service that allows users to:

    Upload documents (a file, along with a title and content for LLM Q&A).

    Ask questions about specific documents.

    Receive asynchronously simulated LLM-generated answers.

    Query the status and response of a question.

📚 Use Case Description

This service acts as the backend for an AI document Q&A application. It handles document storage (both the physical file and its metadata), question submission, and simulates a Large Language Model (LLM) processing answers in the background. This setup mimics real-world LLM-powered products, focusing on core backend skills, Python design, and asynchronous processing.
🧰 Technical Requirements Met

    Core Python & Backend:

        FastAPI is used for building the API.

        Code is structured modularly into routers, services, schemas, and models.

        Clean coding practices and type annotations are followed.

    Database: PostgreSQL

        SQLAlchemy (async) is used for ORM.

        Document Model: Stores id, title, content (for LLM), filename, file_path, created_at, updated_at.

        Question Model: Stores id, document_id, question_text, answer, status, created_at, updated_at.

    APIs Implemented:

        POST /documents/: Upload a document (a file, title, and content).

        GET /documents/{id}: Retrieve a document's details (ID, title, content, filename, file path, timestamps).

        POST /documents/{id}/question: Submit a question related to a document. Triggers an async background job.

        GET /questions/{id}: Retrieve status (pending, answered, failed) and the answer for a question.

    Async Background Job:

        When a question is submitted, asyncio.create_task() is used to run a background job.

        asyncio.sleep(5) simulates LLM processing time.

        A dummy answer like "This is a generated answer to your question: {question}" is returned.

    Docker:

        Dockerfile is provided for the FastAPI application.

        docker-compose.yml is included to orchestrate the FastAPI app and a PostgreSQL database.

    Code Quality & Version Control:

        (Assumed) Git for version control.

        README.md with setup instructions.

        .env.example for configuration.

    Bonus Features Implemented:

        Pydantic BaseModel with validation for API schemas.

        Simple logging for each API request and service operation.

        /health route for uptime checks.

🚀 Setup and Running the Application
Prerequisites

    Python 3.10+

    pip (Python package installer)

    Docker and Docker Compose (recommended for easy setup)

1. Clone the Repository (if applicable)

# If this were a real repository
# git clone <your-repo-url>
# cd ai-qna-microservice

2. Create and Configure .env file

Copy the example environment file and fill in your desired values. For local development with Docker Compose, the defaults should work.

cp .env.example .env

You can open .env and modify variables if needed (e.g., database credentials, server port).
3. Install Python Dependencies (if running locally without Docker)

pip install -r requirements.txt

4. Running with Docker Compose (Recommended)

Docker Compose simplifies running both the FastAPI app and the PostgreSQL database.

docker-compose up --build -d

    --build: Builds the Docker images before starting containers.

    -d: Runs the containers in detached mode (in the background).

Wait a few moments for the database to become healthy and the FastAPI app to start. You can check the logs:

docker-compose logs -f

5. Running Locally (without Docker Compose)

This requires you to have PostgreSQL installed and running on your machine, and you'll need to manually create the database (qna_db) and user (user/password) or configure your .env file to point to an existing PostgreSQL instance.

    Start PostgreSQL: Ensure your PostgreSQL server is running.

    Update .env: Change POSTGRES_HOST in your .env file from db to localhost or 127.0.0.1.

    POSTGRES_HOST="localhost"
    DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/qna_db"

    Run Migrations (if needed): The init_db function in database.py will automatically create tables on startup.

    Start the FastAPI application:

    python main.py

🧪 Testing the Endpoints

Once the server is running (either via Docker Compose or locally), you can access the interactive API documentation at http://localhost:8000/docs (or http://0.0.0.0:8000/docs depending on your host configuration).

Here are curl examples to test the endpoints:
1. Health Check

curl -X GET "http://localhost:8000/health" -H "accept: application/json"

2. Upload a Document (POST /documents/)

Important: Create a dummy text file first, e.g., my_document.txt, with some content.

# Create a dummy file for testing (Linux/macOS)
echo "This is the content of my dummy document file. It's a sample text file." > my_document.txt

# Or on Windows PowerShell:
# Set-Content -Path my_document.txt -Value "This is the content of my dummy document file. It's a sample text file."

curl -X POST "http://localhost:8000/documents/" \
-H "accept: application/json" \
-F "title=My Uploaded File Document" \
-F "content=This is the text content for the LLM to process about the uploaded file." \
-F "file=@./my_document.txt"

    Expected Response: A JSON object representing the created document, including its id, filename, and file_path. Make note of the id.

3. Retrieve a Document (GET /documents/{id})

Replace [DOCUMENT_ID] with the ID obtained from the previous step.

curl -X GET "http://localhost:8000/documents/[DOCUMENT_ID]" \
-H "accept: application/json"

    Expected Response: A JSON object with the document's details (id, title, content, filename, file_path, timestamps).

4. Submit a Question (POST /documents/{id}/question)

Replace [DOCUMENT_ID] with the ID of the document you want to ask about.

curl -X POST "http://localhost:8000/documents/[DOCUMENT_ID]/question" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d '{
  "question_text": "What is the main topic of the LLM content for this document?"
}'

    Expected Response: A JSON object representing the created question, including its id and status: "pending". Make note of the id. The HTTP status code will be 202 Accepted.

5. Retrieve Question Status and Answer (GET /questions/{id})

Replace [QUESTION_ID] with the ID obtained from the previous step.

curl -X GET "http://localhost:8000/questions/[QUESTION_ID]" \
-H "accept: application/json"

    Expected Response (immediately after submission): {"status": "pending", "answer": null}

    Expected Response (after ~5 seconds): {"status": "answered", "answer": "This is a generated answer to your question: 'What is the main topic of the LLM content for this document?'"}"

    You might need to make this request a few times until the status changes from pending to answered.

🛑 Shutting Down

To stop the Docker Compose services:

docker-compose down

To stop the locally running FastAPI app, press Ctrl+C in your terminal.
🧹 Cleaning Up (Docker)

To remove the Docker volumes (which store database data) and images:

docker-compose down


