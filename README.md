# API Gateway

- **Reverse Proxy** is a server that sits in front of your services and protects them. The client thinks it is talking to the proxy, while the proxy forwards the request to the backend and returns the response. 
- **Upstream** is the “real” service that the proxy forwards the request to.
- **Routing** means rules like: “if `/users` comes in, go left; if `/billing`, go right”. 

## Need to

1. **Security:** You can block direct access to microservice ports with a firewall, leaving only the Gateway exposed. 
2. **Single domain:** No `api.users.com` and `api.billing.com` — everything lives on `api.mysite.com`. 
3. **SSL/TLS:** Certificates can be configured only on the Gateway, while inside the trusted network traffic can go over plain HTTP. 
4. **Load balancing:** The Gateway can spread traffic across 10 replicas of the same service. 

## Realisation

In docker-compose.yml, the reverse proxy is run as a separate service, and all microservices are attached to the same internal network. The proxy exposes only one public entry point, while the backend services do not publish their ports to the host. 