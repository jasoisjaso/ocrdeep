# Streamlit OCR Document Processing Application

This application provides a web-based interface for OCR document processing, featuring a deduction form splitter and an invoice extractor. It is built with Streamlit and utilizes a Hugging Face transformer model for OCR, all containerized with Docker for easy deployment.

## Installation and Setup

This guide assumes you have Docker and Docker Compose installed on your system.

### Scenario 1: Setting up a new repository from existing files

If you have received these project files and wish to create a new GitHub repository for them, follow these steps:

1.  **Initialize a Git repository:**
    Navigate to the root directory of the project files and initialize a new Git repository:
    ```bash
    git init
    ```

2.  **Add and commit the files:**
    Add all project files to the repository and make an initial commit:
    ```bash
    git add .
    git commit -m "Initial commit of Streamlit OCR application"
    ```

3.  **Create a new GitHub repository:**
    Go to [GitHub](https://github.com/new) and create a new empty repository. Do NOT initialize it with a README, .gitignore, or license.

4.  **Add GitHub remote and push:**
    Replace `<YOUR_GITHUB_REPO_URL>` with the URL of the new repository you just created on GitHub:
    ```bash
    git remote add origin <YOUR_GITHUB_REPO_URL>
    git push -u origin main
    ```

### Scenario 2: Cloning an existing repository

If you are cloning an existing repository that contains this project, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd <YOUR_REPOSITORY_NAME>
    ```

### Common Steps (for both scenarios)

After setting up your repository (either by creating a new one and pushing, or by cloning an existing one), proceed with these steps to run the application:

1.  **Build the Docker Image**
    Navigate to the root directory of the project (where `docker-compose.yml` and `Dockerfile` are located) and build the Docker image:
    ```bash
    docker-compose build
    ```
    This process may take some time as it downloads the necessary base images and installs all Python dependencies, including the OCR model.

2.  **Run the Docker Containers**
    Once the image is built, you can start the application containers:
    ```bash
    docker-compose up
    ```
    If you want to run it in detached mode (in the background), use:
    ```bash
    docker-compose up -d
    ```

3.  **Access the Application**
    Open your web browser and navigate to the following address:
    ```
    http://localhost:8501
    ```
    The Streamlit OCR application should now be running and accessible.