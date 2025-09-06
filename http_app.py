import os
from typing import Any

from fastapi import FastAPI

# This keeps all tools unchanged and simply exposes them over HTTP.
from main import mcp  # noqa: E402

# Create the MCP ASGI app using Streamable HTTP transport.
# Path is explicitly set to /mcp to avoid conflicts with health endpoints.
# Clients and inspectors should connect to: http://<host>:<port>/mcp
mcp_app = mcp.http_app(path="/mcp", transport="streamable-http")

# FastAPI app must adopt the MCP app lifespan to initialize sessions correctly
app = FastAPI(title="Honeypot Detector MCP", lifespan=mcp_app.lifespan)

# Health check for Smithery and Docker
@app.get("/healthz")
async def healthz(_: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")

# Mount the MCP app
app.mount("/", mcp_app)

# Optional: allow running with uvicorn directly for local dev
#   poetry run uvicorn http_app:app --host 0.0.0.0 --port ${PORT:-8288}
if __name__ == "__main__":
    # Lazy import to avoid uvicorn dependency at import time
    import uvicorn  # type: ignore

    port_str = os.getenv("PORT", "8288")
    try:
        port = int(port_str)
    except ValueError:
        port = 8288

    uvicorn.run("http_app:app", host="0.0.0.0", port=port, reload=False)