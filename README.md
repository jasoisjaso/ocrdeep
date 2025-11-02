# DeepSeek-OCR PDF Processor (Simplified PoC)

## High-Level Goal

This project provides a simplified, proof-of-concept setup for a powerful, scalable, and automated system for extracting structured data from various types of PDF documents. It is optimized for a headless Ubuntu server with an NVIDIA GPU.

## How It Works

1.  **Upload:** A user uploads a PDF through a simple web interface.
2.  **Process:** The application sends the PDF to a background Celery worker.
3.  **Extract:** The worker, running on a GPU, uses the DeepSeek-OCR model to analyze each page and extract the requested data based on a prompt.
4.  **Organize & Report:** The extracted data is used to organize the pages, and a summary report is generated.
5.  **Download:** The user can download a ZIP file with the processed files and the report.

## System Architecture

- **`web`**: A Flask web application for file uploads and job monitoring.
- **`worker`**: A Celery worker for GPU-intensive OCR processing.
- **`scheduler`**: A Celery beat scheduler for periodic tasks.
- **`db`**: A PostgreSQL database for storing job information.
- **`broker`**: A Redis instance for message passing between the web and worker services.
- **`flower`**: A web-based tool for monitoring the Celery cluster.

## Getting Started on a Headless Ubuntu Server

This guide assumes you have a headless Ubuntu server with Docker, Docker Compose, and the NVIDIA driver stack already installed.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Configure the Environment

Create a `.env` file from the example provided. For this simplified setup, you only need to provide basic database credentials. **No Redis password is required.**

```bash
cp .env.example .env
# Edit .env to set your POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB
# For example:
# POSTGRES_USER=myuser
# POSTGRES_PASSWORD=mypassword
# POSTGRES_DB=mydatabase
```

### 3. Build and Run the Application

```bash
docker-compose up -d --build
```

### 4. Access the Services

- **Web Application**: `http://<your-server-ip>:5000`
- **Flower Dashboard**: `http://<your-server-ip>:5555`

### 5. Create an Initial User

To log in to the web application, you need to create a user account.

```bash
docker-compose exec web flask create-user <username> <password>
```

Now you can log in and start processing documents.

## Project Customization

- **Adding New Document Types:** See `ADDING_DOCUMENT_TYPES.md`.
- **Testing and Debugging OCR:** See `OCR_DEBUGGING.md`.