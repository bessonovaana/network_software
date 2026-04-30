FROM python:3.11-slim AS builder
WORKDIR /
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /
COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8101
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8101"]