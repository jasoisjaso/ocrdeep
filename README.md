# Streamlit OCR Document Processing Application

This application provides a web-based interface for OCR document processing, featuring a deduction form splitter and an invoice extractor. It is built with Streamlit and utilizes a Hugging Face transformer model for OCR, all containerized with Docker for easy deployment.

## Installation and Setup

This guide assumes you have Docker and Docker Compose installed on your system.

### 1. Clone the Repository

If you haven't already, clone the repository to your local machine:

```bash
git clone https://github.com/jasoisjaso/ocrdeep.git
cd ocrdeep
```

### 2. Build the Docker Image

Navigate to the root directory of the cloned repository (where `docker-compose.yml` and `Dockerfile` are located) and build the Docker image:

```bash
docker-compose build
```

This process may take some time as it downloads the necessary base images and installs all Python dependencies, including the OCR model.

### 3. Run the Docker Containers

Once the image is built, you can start the application containers:

```bash
docker-compose up
```

If you want to run it in detached mode (in the background), use:

```bash
docker-compose up -d
```

### 4. Access the Application

Open your web browser and navigate to the following address:

```
http://localhost:8501
```

The Streamlit OCR application should now be running and accessible.
