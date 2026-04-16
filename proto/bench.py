import time
import requests
import grpc
import service_pb2
import service_pb2_grpc


def run_rest_bench():
    print("Starting REST benchmark...")
    start = time.time()
    for _ in range(1000):
        resp = requests.get("http://localhost:8000/orders")
        assert resp.status_code == 200
    end = time.time()
    print(f"REST: {end - start:.4f} sec")


def run_grpc_bench():
    print("Starting gRPC benchmark...")
    with grpc.insecure_channel('localhost:8138') as channel:
        stub = service_pb2_grpc.CommentsServiceStub(channel)
        start = time.time()
        for _ in range(1000):
            req = service_pb2.CreateCommentRequest(
                text="test", author="ananas", post_id="1"
            )
            stub.CreateComment(req)
        end = time.time()
        print(f"gRPC: {end - start:.4f} sec")


if __name__ == "__main__":
    run_rest_bench()
    run_grpc_bench()