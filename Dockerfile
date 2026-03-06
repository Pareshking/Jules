FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user with UID 1000
RUN useradd -m -u 1000 user

# Set up the environment for the user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Copy the app code and chown to the new user
COPY --chown=user . $HOME/app
WORKDIR $HOME/app

# Expose the Streamlit port
EXPOSE 7860

# Run the application on the required HF port
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
