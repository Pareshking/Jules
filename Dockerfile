FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user with UID 1000
RUN useradd -m -u 1000 user

COPY requirements.txt .

# Install dependencies as root (globally available)
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files with ownership for the non-root user
COPY --chown=user . .

# Switch to non-root user
USER user

# Expose the port
EXPOSE 7860

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

# Entrypoint
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
