import os
import json
import logging
from mcp.server.fastmcp import FastMCP

from tealium_calls import obtener_versiones, obtener_lista_load_rules, actualizar_load_rule, obtener_detalles_version

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TealiumMCP")

# Create an MCP server
mcp = FastMCP("Tealim MCP")

# Load API key from an environment variable
api_key_file = os.getenv("API_KEY_FILE")
if api_key_file and os.path.exists(api_key_file):
    with open(api_key_file, "r") as file:
        API_KEY = file.read().strip()
else:
    logger.error(f"API key file '{api_key_file}' not found or not set.")
    raise FileNotFoundError(f"API key file '{api_key_file}' not found or not set.")

user_email = os.getenv("USER_EMAIL")
if not user_email:
    logger.error("USER_EMAIL environment variable is not set.")
    raise ValueError("USER_EMAIL environment variable is not set.")

tealium_account = os.getenv("TEALIUM_ACCOUNT")
if not tealium_account:
    logger.error("TEALIUM_ACCOUNT environment variable is not set.")
    raise ValueError("TEALIUM_ACCOUNT environment variable is not set.")

@mcp.tool()
async def obtener_versiones_tealium(profile: str) -> dict:
    """
    Obtiene del perfil indicado en Tealium el listado de versiones.

    Args:
        profile (str): Nombre del perfil de Tealium.

    Returns:
        dict: Un diccionario con el listado de versiones o un mensaje de error.
    """
    if not profile:
        logger.error("El parámetro 'profile' no está informado.")
        return {"error": "El parámetro 'profile' es obligatorio."}

    try:
        versiones = await obtener_versiones(API_KEY, user_email, tealium_account, profile)
        return versiones
    except Exception as e:
        logger.exception("Error al obtener el detalle de la version de Tealium")
        return {"error": str(e)}

@mcp.tool()
async def obtener_detalles_version_tealium(profile: str, versionId: str) -> dict:
    """
    Obtiene del perfil indicado de Tealium información detallada de la versión indicada.

    Args:
        profile (str): Nombre del perfil de Tealium.
        versionId (str): ID de la versión.

    Returns:
        dict: Un diccionario con el detalle de la version indicada o un mensaje de error.
    """
    if not profile:
        logger.error("El parámetro 'profile' no está informado.")
        return {"error": "El parámetro 'profile' es obligatorio."}

    try:
        versiones = await obtener_detalles_version(API_KEY, user_email, tealium_account, profile, versionId)
        return versiones
    except Exception as e:
        logger.exception("Error al obtener versiones de Tealium")
        return {"error": str(e)}

@mcp.tool()
async def obtener_lista_load_rules_tealium(profile: str) -> dict:
    """
    A partir de un perfil de Tealium, obtiene el listado de load rules, donde se incluye información de las condiciones y quién las está utilizando.

    Args:
        profile (str): Nombre del perfil de Tealium.

    Returns:
        dict: Un diccionario con el listado de load rules o un mensaje de error.
    """
    if not profile:
        logger.error("El parámetro 'profile' no está informado.")
        return {"error": "El parámetro 'profile' es obligatorio."}

    try:
        load_rules = await obtener_lista_load_rules(API_KEY, user_email, tealium_account, profile)
        return load_rules
    except Exception as e:
        logger.exception("Error al obtener lista de load rules de Tealium")
        return {"error": str(e)}
    
@mcp.tool()
async def actualizar_load_rule_tealium(profile: str, notes: str, load_rule_id: str, load_rule_name: str, load_rule_state: str, load_rule_conditions: list) -> dict:
    """
    Actualiza una load rule de Tealium.

    Args:
        profile (str): Nombre del perfil de Tealium.
        notes (str): Comentario de lo que se está actualizando en la load rule.
        load_rule_id (str): ID de la load rule a actualizar.
        load_rule_name (str): Nombre de la load rule.
        load_rule_state (str): Estado de la load rule (active/inactive).
        load_rule_conditions (list): Lista de condiciones en formato JSON.

    Returns:
        dict: Un diccionario con el resultado de la operación o un mensaje de error.
    """
    missing_params = []
    if not profile:
        missing_params.append("profile")
    if not notes:
        missing_params.append("notes")
    if not load_rule_id:
        missing_params.append("load_rule_id")
    if not load_rule_name:
        missing_params.append("load_rule_name")
    if not load_rule_state:
        missing_params.append("load_rule_state")
    if not load_rule_conditions:
        missing_params.append("load_rule_conditions")

    if missing_params:
        logger.error(f"Faltan parámetros obligatorios: {', '.join(missing_params)}")
        return {"error": "Faltan parámetros obligatorios.", "missing_params": missing_params}

    try:
       return await actualizar_load_rule(API_KEY, user_email, tealium_account, profile, notes, load_rule_id, load_rule_name, load_rule_state, load_rule_conditions)
    except Exception as e:
        logger.exception("Error al actualizar load rule de Tealium")
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
