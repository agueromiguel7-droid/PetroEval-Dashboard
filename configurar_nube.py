import json
import os

print("=========================================================")
print("  CONFIGURACIÓN DE ENTRADAS A LA NUBE (STREAMLIT)        ")
print("=========================================================\n")

json_path = input("Arrastra aquí o pega la ruta completa de tu archivo JSON descargado de Google Cloud:\n> ").strip().strip('"').strip("'")
url = input("\nPega aquí el enlace (URL) de tu Google Sheet:\n> ").strip()

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        creds = json.load(f)

    os.makedirs(".streamlit", exist_ok=True)
    with open(".streamlit/secrets.toml", 'w', encoding='utf-8') as f:
        f.write("[connections.gsheets]\n")
        f.write(f'spreadsheet = "{url}"\n')
        for key, value in creds.items():
            value_str = str(value).replace('\\n', '\\\\n') if isinstance(value, str) else value
            f.write(f'{key} = "{value_str}"\n')
            
    print("\n[ÉXITO]: El archivo .streamlit/secrets.toml ha sido generado correctamente.")
    print("La aplicación local ya tiene las llaves inyectadas para conectarse a Google Drive.")
except Exception as e:
    print(f"\n[ERROR]: Ocurrió un error al procesar el archivo o la URL: {e}")
