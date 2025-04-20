import json
import httpx
import asyncio
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TealiumCalls")

max_retries = 1

access_tokens = {} 
TOKEN_DURATION = 30 * 60  # 30 minutos en segundos

def guardar_access_token(profile, token, url_base):
    expiry_time = time.time() + TOKEN_DURATION
    access_tokens[profile] = {'token': token, 'url_base': url_base,'expiry': expiry_time}
    threading.Timer(TOKEN_DURATION, eliminar_access_token, args=[profile]).start()

def obtener_access_token(profile):
    token_data = access_tokens.get(profile)
    if token_data and token_data['expiry'] > time.time():
        return token_data['token'], token_data['url_base']
    return None, None

def eliminar_access_token(profile):
    if profile in access_tokens:
        del access_tokens[profile]

async def obtener_jwt_y_url_base_tealium(api_key, username, account, profile):
    """
    Obtiene el JWT y la URL base de Tealium a partir del API Key y account, teniendo en cuenta que es para un perfil concreto.
    """
    url = f"https://platform.tealiumapis.com/v3/auth/accounts/{account}/profiles/{profile}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "username": username,
        "key": api_key
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            response_json = response.json()
            token = response_json["token"]
            url_base = response_json["host"]
            guardar_access_token(profile, token, url_base)
        except httpx.RequestError as e:
            logger.exception("Error al obtener el JWT y la URL base")
            return None, None

async def obtener_versiones(api_key, username, account, profile, retries=0):
    """
    Obtiene la lista de versiones de un perfil de Tealium (API v3).
    """
    jwt, url_base = obtener_access_token(profile)

    if not jwt or not url_base:
        await obtener_jwt_y_url_base_tealium(api_key, username, account, profile)
        jwt, url_base = obtener_access_token(profile)

    url = f"https://{url_base}/v3/tiq/accounts/{account}/profiles/{profile}?includes=versionIds"
    headers = {"Authorization": f"Bearer {jwt}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.exception("Error al obtener la lista de versiones")
            if response.status_code == 401 and retries < max_retries:  # Unauthorized
                logger.info("Token expirado, obteniendo un nuevo token...")
                await asyncio.sleep(1)
                return await obtener_versiones(api_key, username, account, profile, retries + 1)
            return []

async def obtener_lista_load_rules(api_key, username, account, profile, retries=0):
    """
    A partir de un perfil de Tealium, obtiene el listado de load rules, donde se incluye infomraci\u00f3n de las condiciones, quien las esta utilizando, etc.
    """
    jwt, url_base = obtener_access_token(profile)

    if not jwt or not url_base:
        await obtener_jwt_y_url_base_tealium(api_key, username, account, profile)
        jwt, url_base = obtener_access_token(profile)

    url = f"https://{url_base}/v3/tiq/accounts/{account}/profiles/{profile}?includes=loadRules"
    headers = {"Authorization": f"Bearer {jwt}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.exception("Error al obtener la lista de load rules")
            if response.status_code == 401 and retries < max_retries:  # Unauthorized
                logger.info("Token expirado, obteniendo un nuevo token...")
                await asyncio.sleep(1)
                return await obtener_lista_load_rules(api_key, username, account, profile, retries + 1)
            return []

async def actualizar_load_rule(api_key, username, account, profile, notes, load_rule_id, load_rule_name, load_rule_state, load_rule_conditions, retries=0):
    """
    Actualiza un load rule en Tealium.
    """
    jwt, url_base = obtener_access_token(profile)

    if not jwt or not url_base:
        await obtener_jwt_y_url_base_tealium(api_key, username, account, profile)
        jwt, url_base = obtener_access_token(profile)

    url = f"https://{url_base}/v3/tiq/accounts/{account}/profiles/{profile}?tps=4"
    headers = {"Authorization": f"Bearer {jwt}"}

    json_load_rule = {
        "saveType": "save",
        "notes": f"{notes}",
        "operationList": [
            {
                "op": "replace",
                "path": f"/loadRules/{load_rule_id}",
                "value": {
                    "object": "loadRule",
                    "name": f"{load_rule_name}",
                    "status": f"{load_rule_state}",
                    "conditions": load_rule_conditions
                }
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, headers=headers, data=json.dumps(json_load_rule))
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.exception("Error al actualizar el load rule")
            if response.status_code == 401 and retries < max_retries:  # Unauthorized
                logger.info("Token expirado, obteniendo un nuevo token...")
                await asyncio.sleep(1)
                return await actualizar_load_rule(api_key, username, account, profile, notes, load_rule_id, load_rule_name, load_rule_state, load_rule_conditions, retries + 1)
            return []
