## Together streaming integration

This repo includes a streaming AI assistant that uses the Together Python client as a backend model provider.

How it works
- server/ai_stream.py calls Together's Python client in streaming mode and prints one JSON line per token.
- server/index.js spawns that Python script and proxies its stdout as Server-Sent Events (SSE) to /api/ai-chat-stream.
- The frontend (index.html) opens an EventSource to /api/ai-chat-stream and renders tokens as they arrive.

Required secrets (add these to GitHub Secrets or your host environment):
- TOGETHER_API_KEY — API key for Together (used by ai_stream.py)
- MONGO_URI — MongoDB Atlas connection string
- STRIPE_SECRET_KEY — Stripe secret key (test & live as needed)
- STRIPE_PUBLISHABLE_KEY
- STRIPE_WEBHOOK_SECRET
- TRAVELPAYOUTS_TOKEN — TravelPayouts API token

Docker notes
- The server Dockerfile now installs Python and the Together Python client. Build may take a bit longer on first run.

Local testing
1. Add TOGETHER_API_KEY and other required env vars locally.
2. Start the server (recommended via Docker Compose):
   docker-compose up --build
3. Visit http://localhost:3000 and use the AI Autopilot panel.

Security notes
- Never expose TOGETHER_API_KEY or other secrets in client-side code.
- The SSE endpoint should be protected/rate-limited in production to avoid abuse and cost spikes.
