FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=5000

WORKDIR /app

# System packages needed by project dependencies (Torch/Pillow/pyttsx3/pdf parsing).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    espeak-ng \
    libespeak1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

# Runtime directories used by the app.
RUN mkdir -p uploads/chroma_db uploads/temp_images static/audio

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--timeout", "180", "--bind", "0.0.0.0:5000", "app:app"]
