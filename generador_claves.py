import bcrypt
import getpass

def generar_hash(password: str) -> str:
    """Genera un hash seguro usando bcrypt (rondas=12)"""
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if __name__ == "__main__":
    print("=========================================================")
    print("  GENERADOR DE CLAVES SEGURAS PARA PETROEVAL AI          ")
    print("=========================================================\n")
    print("Usa este script para encriptar las contraseñas antes de ")
    print("pegarlas en la columna 'password_hash' de Google Sheets.\n")
    
    while True:
        pwd = getpass.getpass("Ingresa la nueva contraseña (o presiona Enter para salir): ")
        if not pwd:
            break
            
        hashed_pwd = generar_hash(pwd)
        print(f"\n[🔑 HASH GENERADO]:\n{hashed_pwd}\n")
        print("-" * 50)
