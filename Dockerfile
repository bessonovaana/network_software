FROM ubuntu:22.04

COPY requirements.txt .

USER appuser

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel \
    && addgroup --system --gid 1000 appuser \
    && adduser --system --uid 1000 --gid 1000 appuser \
    && pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app



COPY . .


EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]