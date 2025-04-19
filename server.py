import httpx
import os
from mcp.server.fastmcp import FastMCP

from tealium_calls import obtener_versiones, obtener_lista_load_rules

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

@mcp.tool()
async def obtener_lista_load_rules_tealium(profile: str) -> dict:
    """A partir de un perfil de Tealium, obtiene el listado de load rules, donde se incluye infomración de las condiciones, quien las esta utilizando, etc."""
    try:
        load_rules = await obtener_lista_load_rules(API_KEY, user_email, tealium_account, profile)
        return load_rules
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")