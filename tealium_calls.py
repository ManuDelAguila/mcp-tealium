import json
import httpx
import asyncio
import time
import threading

max_retries = 1

access_tokens = {}  # {user_id: {'token': '...', 'expiry': timestamp}}
TOKEN_DURATION = 30 * 60  # 30 minutos en segundos

def guardar_access_token(profile, token, url_base):
    expiry_time = time.time() + TOKEN_DURATION
    access_tokens[profile] = {'token': token, 'url_base': url_base,'expiry': expiry_time}
    # Opcional: Programar la eliminación del token después de la expiración
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
            print(f"Error al obtener el JWT y la URL base: {e}")
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
            try:
                error_response = response.json()
                print(f"Error al obtener versiones del perfil {profile}: {error_response}")
            except json.JSONDecodeError:
                print(f"Error al obtener el detalle de la revisión: {e}")
            if response.status_code == 401:  # Unauthorized
                print("Token expirado, obteniendo un nuevo token...")
                if retries < max_retries:
                    await asyncio.sleep(1)
                    return await obtener_versiones(api_key, username, account, profile, retries + 1)
            print(f"Error al obtener la lista de versiones: {e}")
            return []

