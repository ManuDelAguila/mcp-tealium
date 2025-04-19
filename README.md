# mcp-tealium
Servidor MCP para interactuar con Tealium

# Preparar entorno

### Crear un entorno virtual de python
```sh
python -m venv venv
```

### Visual code studio
    Ctrl + Shift + P
    Buscar "Python: Select Interpreter"
    Seleccionar el que tiene "venv"

### Activar el entorno virtual
```sh
venv\Scripts\activate
```

## Tabajar con el requirements.txt
### Actualizar el requirements.txt
```sh
pip freeze > requirements.txt
```

### Instalar requerimientos
```sh
pip install -r requirements.txt
```


# Añadir el MCP    
Ctrl + Shift + P
Bzuscar "Preferences: Open User Settings (JSON)"
Dentro de mcp > servers añadir el de Tealium MCP

Substituir las variables:
1. Cambia ambos "<<RUTA_PROYECTO>>" por la ruta donde esta el proyecto  (hasta la carpteta mcp-tealium incluida)
2. Cambia el "<<RUTA_API_KEY_TEALIUM>>" por ruta a un fichero txt donde contenga la API_KEY de Tealium
3. Cambia el "<<EMAIL_DEL_USUARIO_DE_LA_API>>" por el email del usuario al que esta ligado la API KEY
4. Cambia el "<<TEALIUM_ACCOUNT>>" por la cuenta de Tealium

```json
{
    "mcp": {        
        "servers": {
            "Tealim MCP": {
                "command": "<<RUTA_PROYECTO>>/venv/Scripts/python",
                "args": [
                    "<<RUTA_PROYECTO>>/server.py",
                ],
                "env": {
                    "API_KEY_FILE": "<<RUTA_API_KEY_TEALIUM>>",
                    "USER_EMAIL": "<<EMAIL_DEL_USUARIO_DE_LA_API>>",
                    "TEALIUM_ACCOUNT": "<<TEALIUM_ACCOUNT>>"
                }
            }
        }
    }
}
```
