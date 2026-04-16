# gPRC

gRPC is Google’s framework for remote procedure calls. This week we describe our service not in code, but in a special `.proto` file, and generate the server and client from it. In REST, we send data as text (JSON). That is convenient for humans, but slower for machines because the text has to be parsed. In gRPC, we send binary data (Protocol Buffers). It is very fast and compact.

Also, in REST the contract is just a convention or documentation, like Swagger. In gRPC the contract is law. If you change a field type in the `.proto` file, the code will simply fail to compile or will fail with a clear error.

## Key concepts
- **Protocol Buffers (Protobuf)** — an interface description language (IDL). You write `int32 id = 1`, and it turns into efficient code for Python, Go, Java, and C++.
- **Unary RPC** — the simplest interaction type: the client sends one request and the server returns one response. It is very similar to a normal function call, only over the network.
- **Stub** — generated client-side code that looks like a normal object. You call `stub.GetItem(request)`, and it packs the data and sends it over the network.

## Why this is useful
1. **Speed**: Protobuf serialization is much faster than JSON.
2. **Less traffic**: Binary format takes less space.
3. **Code generation**: You do not need to write clients manually. You just give your colleagues the `.proto` file, and they generate a client for their language.

## Tools
In Python, we use the `grpcio` and `grpcio-tools` libraries.  
The generation command usually looks like this:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/service.proto
```

## gRPC vs REST

Starting REST benchmark...

REST: 1.1095 sec

Starting gRPC benchmark...

gRPC: 0.1773 sec

**Conclusion**

In this test, gRPC showed better performance than REST.  
The difference is due to the more compact serialization format (Protobuf instead of JSON) and the lower protocol overhead of gRPC over HTTP/2.  
However, for real-world use it is also important to consider development complexity, frontend compatibility, and logging/monitoring infrastructure, which are usually simpler with REST services.