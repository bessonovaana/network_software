import grpc
from concurrent import futures
import sys
from pathlib import Path
# Импортируйте сгенерированные модули

proto_dir = Path(__file__).resolve().parent / "proto"
sys.path.append(str(proto_dir))
import service_pb2
import service_pb2_grpc

class ServiceImplementation(service_pb2_grpc.UsersServiceServicer): # Унаследуйтесь от сгенерированного Servicer
    def DoWork(self, request, context):
        return service_pb2.MyResponse(
            result=f"Processed users={request.users}",
            email=request.email,
        )

    # Реализуйте методы сервиса

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UsersServiceServicer_to_server(service_pb2_grpc.UsersServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()