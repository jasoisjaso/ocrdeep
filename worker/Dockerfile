FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    build-essential \
    ninja-build \
    cmake \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set build env vars
ENV MAX_JOBS=4
ENV FLASH_ATTENTION_FORCE_BUILD=TRUE

# Copy requirements
COPY requirements.txt .

# Install in correct order per DeepSeek docs
RUN pip3 install packaging setuptools wheel && \
    pip3 install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install transformers==4.46.3 tokenizers==0.20.3 accelerate einops addict easydict && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install flash-attn==2.7.3 --no-build-isolation

# Copy worker code
COPY . .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]