import httpx
import os
from mcp.server.fastmcp import FastMCP

from tealium_calls import obtener_versiones

# Create an MCP server
mcp = FastMCP("Tealim MCP")

# Load API key from an environment variable
api_key_file = os.getenv("API_KEY_FILE")
if api_key_file and os.path.exists(api_key_file):
    with open(api_key_file, "r") as file:
        API_KEY = file.read().strip()
else:
    raise FileNotFoundError(f"API key file '{api_key_file}' not found or not set.")

user_email = os.getenv("USER_EMAIL")
if not user_email:
    raise ValueError("USER_EMAIL environment variable is not set.")

tealium_account = os.getenv("TEALIUM_ACCOUNT")
if not tealium_account:
    raise ValueError("TEALIUM_ACCOUNT environment variable is not set.")

@mcp.tool()
async def obtener_versiones_tealium(profile: str) -> dict:
    """Obtiene del pefil indicado en Tealium el listado de versiones."""
    try:
        versiones = await obtener_versiones(API_KEY, user_email, tealium_account, profile)
        return versiones
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")