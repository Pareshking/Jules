FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

# Create a non-root user with UID 1000
RUN useradd -m -u 1000 user

COPY . .

# Change ownership of the application directory to the non-root user
RUN chown -R user:user /app

# Switch to the non-root user
USER user

# Add local bin to PATH (though dependencies are installed globally, this is good practice)
ENV PATH="/home/user/.local/bin:$PATH"

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
