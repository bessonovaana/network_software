#!/bin/bash
set -e

echo "=== REST API (wrk) ==="


echo "Concurrency 1:"
wrk -t1 -c1 -d10s http://localhost:8101/orders

echo "Concurrency 10:"
wrk -t2 -c10 -d10s http://localhost:8101/orders

echo "Concurrency 100:"
wrk -t4 -c100 -d10s http://localhost:8101/orders


echo "=== gRPC (ghz) ==="

echo "Concurrency 1:"
ghz --insecure \
    --proto tickets.proto \
    --call tickets.v1.TicketsService.ListTickets \
    --total 100 \
    --concurrency 1 \
    localhost:50051

echo "Concurrency 10:"
ghz --insecure \
    --proto tickets.proto \
    --call tickets.v1.TicketsService.ListTickets \
    --total 1000 \
    --concurrency 10 \
    localhost:50051

echo "Concurrency 100:"
ghz --insecure \
    --proto tickets.proto \
    --call tickets.v1.TicketsService.ListTickets \
    --total 10000 \
    --concurrency 100 \
    localhost:50051