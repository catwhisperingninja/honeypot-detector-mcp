import asyncio
import os
import httpx
from typing import Dict, Any
from fastapi import FastAPI, Request

# Configuration - NO API KEY REQUIRED
HONEYPOT_API_URL = "https://honeypot.is/ethereum"

app = FastAPI()

async def fetch_honeypot_data(address: str) -> Dict[str, Any]:
    """Fetch data from honeypot.is API"""
    async with httpx.AsyncClient() as client:
        headers: Dict[str, str] = {}
        params = {"address": address}
        try:
            response = await client.get(HONEYPOT_API_URL, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API request failed: {str(e)}")

@app.get("/check_honeypot")
async def check_honeypot(address: str) -> str:
    """Check if a token address is a honeypot using honeypot.is API"""
    if not address.startswith("0x") or len(address) != 42:
        raise ValueError("Invalid address format")

    data = await fetch_honeypot_data(address)
    is_honeypot = data.get("honeypotResult", {}).get("isHoneypot", False)
    risk = data.get("summary", {}).get("risk", "unknown")
    token_name = data.get("token", {}).get("name", "Unknown")
    buy_tax = data.get("simulationResult", {}).get("buyTax", "N/A")
    sell_tax = data.get("simulationResult", {}).get("sellTax", "N/A")
    transfer_tax = data.get("simulationResult", {}).get("transferTax", "N/A")
    is_open_source = data.get("contractCode", {}).get("openSource", "Unknown")

    result = f"""# Honeypot Analysis for {token_name}
- **Address**: {address}
- **Is Honeypot**: {is_honeypot}
- **Risk Level**: {risk}
- **Buy Tax**: {buy_tax}
- **Sell Tax**: {sell_tax}
- **Transfer Tax**: {transfer_tax}
- **Contract Code Open Source**: {is_open_source}
"""
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8288)
