# Document Management System

A Django application for managing document uploads with metadata and search functionality.

## Features

- Drag and drop file upload
- Document metadata (UID, SSN, First Name, Last Name, Document Type)
- File storage on local filesystem
- PostgreSQL database integration (Docker-based)
- Search functionality across all fields
- Modern Bootstrap UI

## Prerequisites

- Python 3.8+
- Docker 2.x
- Virtual environment (recommended)

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start PostgreSQL using Docker:
```bash
docker compose up -d
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

6. Visit http://localhost:8000 in your browser

## Usage

1. Upload Documents:
- Click "Upload" in the navigation
- Fill out the document metadata
- Drag and drop a file or click to select one
- Click "Upload" to save

2. Search Documents:
- Click "Search" in the navigation
- Enter search terms to filter by any field
- Click on file links to view/download documents

## Docker Management

To manage the PostgreSQL container:

- Start the database: `docker compose up -d`
- Stop the database: `docker compose down`
- View logs: `docker compose logs db`
- Remove volumes (will delete all data): `docker compose down -v`

The PostgreSQL database will be accessible:
- Host: localhost
- Port: 5432
- Database: image_db
- Username: postgres
- Password: postgres 