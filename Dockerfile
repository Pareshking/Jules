FROM python:3.10-slim

# Create unprivileged user for Hugging Face Spaces security
RUN useradd -m -u 1000 user
USER user

ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user:user requirements.txt .

RUN pip3 install --user --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
