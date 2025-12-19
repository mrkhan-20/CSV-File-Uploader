# CSV File Uploader

A FastAPI-based application for uploading and processing CSV/Excel files with background task processing using Celery and Redis.

## Features

- Upload CSV and Excel files
- Process files with operations like deduplication, unique filtering, and custom filtering
- Asynchronous task processing with Celery
- Task status tracking and monitoring
- RESTful API with automatic documentation

## Prerequisites

- Python 3.14 or higher
- Redis server
- (Optional) Docker and Docker Compose for containerized deployment

## Local Development Setup

### 1. Install Dependencies

Navigate to the `api` directory and install Python dependencies:

```bash
cd api
pip install -r requirements.txt
```

### 2. Start Redis Server

Redis is required as the message broker for Celery. Start Redis using one of the following methods:

**Option A: Using Docker (Recommended)**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Option B: Using Redis installed locally**
```bash
# On Windows (if Redis is installed)
redis-server

# On Linux/Mac
redis-server
```

**Option C: Using Homebrew (Mac)**
```bash
brew services start redis
```

### 3. Start the Application

You need to run three services: FastAPI server, Celery worker, and Redis (if not already running).

#### Terminal 1: Start FastAPI Server

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

#### Terminal 2: Start Celery Worker

```bash
cd api
celery -A tasks worker --loglevel=info --concurrency=4
```

#### Terminal 3: (Optional) Start Flower - Celery Monitoring

```bash
cd api
celery -A tasks flower --port=5555
```

Flower will be available at: http://localhost:5555

### Verify Services are Running

- **FastAPI**: Visit http://localhost:8000/health
- **Redis**: Check if Redis is accepting connections (should be running on port 6379)
- **Celery Worker**: Check the terminal output for "ready" message
- **Flower**: Visit http://localhost:5555 (if started)

## Docker Setup

### Using Docker Compose (Recommended)

The easiest way to run the entire application stack is using Docker Compose:

```bash
cd api
docker-compose up --build
```

This will start all services:
- **Redis** on port 6379
- **FastAPI** server on port 8000
- **Celery Worker** for background task processing
- **Flower** monitoring on port 5555

### Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower**: http://localhost:5555

### Docker Compose Commands

```bash
# Start services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild containers
docker-compose up --build
```

### Individual Docker Services

If you prefer to run services individually:

#### Start Redis
```bash
docker run -d -p 6379:6379 --name csv_redis redis:7-alpine
```

#### Build and Run FastAPI
```bash
cd api
docker build -t csv-api .
docker run -d -p 8000:8000 --name csv_api --link csv_redis:redis -e REDIS_URL=redis://redis:6379/0 csv_api
```

#### Build and Run Celery Worker
```bash
cd api
docker build -t csv-api .
docker run -d --name csv_celery_worker --link csv_redis:redis -e REDIS_URL=redis://redis:6379/0 csv_api celery -A tasks worker --loglevel=info
```

## Project Structure

```
CSV-File-Uploader/
├── api/
│   ├── main.py              # FastAPI application entry point
│   ├── tasks.py             # Celery task definitions
│   ├── config.py            # Application configuration
│   ├── schemas.py           # Pydantic models
│   ├── validators.py        # File validation utilities
│   ├── routers/             # API route handlers
│   │   ├── upload.py        # File upload endpoints
│   │   ├── operations.py    # Operation endpoints
│   │   ├── tasks.py         # Task status endpoints
│   │   └── files.py         # File management endpoints
│   ├── services/            # Business logic services
│   │   ├── file_service.py  # File handling service
│   │   └── task_service.py  # Task management service
│   ├── uploads/             # Uploaded files directory
│   ├── processed/           # Processed files directory
│   ├── requirements.txt     # Python dependencies
│   ├── dockerfile           # Docker image definition
│   └── docker-compose.yml   # Docker Compose configuration
└── README.md
```

## API Endpoints

- `POST /upload` - Upload a CSV/Excel file
- `POST /operations/{operation}` - Apply operations to files
- `GET /tasks/{task_id}` - Get task status
- `GET /files` - List uploaded files

Visit http://localhost:8000/docs for interactive API documentation.


