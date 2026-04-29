# WebRTC and P2P communication
WebRTC (Web Real-Time Communication) is the magic that lets browsers talk directly to each other. It's the foundation for Google Meet, Zoom (in the browser), Discord, and tons of online games.

## How does it work?
Browsers are often stuck behind NAT (routers) and don't know their public IP addresses. To connect, they go on a quest:

1. Signaling: Browsers connect via a regular server (WebSocket/HTTP) and negotiate: "I support these codecs, here are my parameters."

2. STUN: The browser asks a special STUN server: "What's my public IP:port?"

3. ICE Candidates: The browser gathers all possible addresses (local IP, public IP) and sends them to the other party via Signaling.

3. P2P Connection: Browsers try to punch through NAT and establish a direct UDP connection.

4. Data Channel / Media Stream: If it works—traffic flows directly. The server is no longer needed (almost).
## Start
``` bash
python starter/signaling.py
firefox client/index.html
firefox client/index.html
```