FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary files
COPY worker/tasks.py .
COPY worker/processors/ ./processors/
COPY worker/prompts/ ./prompts/

CMD ["celery", "-A", "tasks", "beat", "--loglevel=info"]
