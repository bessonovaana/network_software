FROM python:3.11-slim AS builder
WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /
COPY --from=builder /install /usr/local
COPY main.py /
COPY proto/ /proto/

EXPOSE 50051
CMD ["python", "main.py"]