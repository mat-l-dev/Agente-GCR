"""
Script de verificación del sistema Bot ISP
Verifica que todas las configuraciones y servicios estén correctos
"""

import os
import sys

# Colores para la consola
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(condition, message):
    if condition:
        print(f"{GREEN}✅ {message}{RESET}")
        return True
    else:
        print(f"{RED}❌ {message}{RESET}")
        return False

def warn(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

print("="*60)
print("🔍 VERIFICACIÓN DEL SISTEMA BOT ISP")
print("="*60)
print()

# 1. Verificar Python
print("📌 1. VERSIÓN DE PYTHON")
import sys
version = sys.version_info
check(version.major == 3 and version.minor >= 10, 
      f"Python {version.major}.{version.minor}.{version.micro}")
print()

# 2. Verificar variables de entorno
print("📌 2. VARIABLES DE ENTORNO (.env)")
from dotenv import load_dotenv
load_dotenv()

checks = [
    ("TWILIO_ACCOUNT_SID", os.getenv("TWILIO_ACCOUNT_SID")),
    ("TWILIO_AUTH_TOKEN", os.getenv("TWILIO_AUTH_TOKEN")),
    ("TWILIO_FROM_NUMBER", os.getenv("TWILIO_FROM_NUMBER")),
    ("TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN")),
    ("TELEGRAM_ADMIN_ID", os.getenv("TELEGRAM_ADMIN_ID")),
    ("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY")),
    ("SUPABASE_URL", os.getenv("SUPABASE_URL")),
    ("SUPABASE_KEY", os.getenv("SUPABASE_KEY")),
    ("MIKROTIK_HOST", os.getenv("MIKROTIK_HOST")),
    ("MIKROTIK_USER", os.getenv("MIKROTIK_USER")),
    ("MIKROTIK_PASS", os.getenv("MIKROTIK_PASS")),
]

all_ok = True
for name, value in checks:
    ok = check(value is not None and value != "", f"{name}: {'*' * min(len(value or ''), 20)}")
    all_ok = all_ok and ok
print()

# 3. Verificar paquetes instalados
print("📌 3. PAQUETES INSTALADOS")
packages = [
    "fastapi",
    "uvicorn",
    "twilio",
    "supabase",
    "google.generativeai",
    "telegram",
    "routeros_api",
    "python-dotenv",
]

for package in packages:
    try:
        if package == "google.generativeai":
            __import__("google.generativeai")
        elif package == "python-dotenv":
            __import__("dotenv")
        elif package == "routeros_api":
            __import__("routeros_api")
        else:
            __import__(package)
        check(True, f"{package}")
    except ImportError:
        check(False, f"{package} NO INSTALADO")
print()

# 4. Verificar estructura de archivos
print("📌 4. ESTRUCTURA DE ARCHIVOS")
files_to_check = [
    "main.py",
    "requirements.txt",
    ".env",
    "app/core/config.py",
    "app/routers/webhook_wa.py",
    "app/routers/webhook_tg.py",
    "app/services/whatsapp.py",
    "app/services/telegram.py",
    "app/services/chatgpt.py",  # Reemplaza a gemini.py
    "app/services/mikrotik.py",
    "app/services/supabase.py",
]

for file in files_to_check:
    check(os.path.exists(file), f"{file}")
print()

# 5. Test de importación de módulos
print("📌 5. IMPORTACIÓN DE MÓDULOS")
try:
    from app.core.config import settings
    check(True, "app.core.config")
    
    from app.services.whatsapp import enviar_mensaje_whatsapp
    check(True, "app.services.whatsapp")
    
    from app.services.telegram import enviar_alerta_pago
    check(True, "app.services.telegram")
    
    # ChatGPT en lugar de Gemini
    from app.services.chatgpt import obtener_respuesta_chatgpt
    check(True, "app.services.chatgpt")
    
    from app.services.mikrotik import crear_usuario_hotspot
    check(True, "app.services.mikrotik")
    
    from app.services.supabase import guardar_venta_pendiente
    check(True, "app.services.supabase")
    
except Exception as e:
    check(False, f"Error de importación: {e}")
print()

# 6. Verificar conexión a Supabase
print("📌 6. CONEXIÓN A SUPABASE")
try:
    from app.services.supabase import supabase
    # Intenta hacer una consulta simple
    response = supabase.table("ventas").select("*").limit(1).execute()
    check(True, "Conectado a Supabase correctamente")
except Exception as e:
    check(False, f"Error de conexión a Supabase: {str(e)[:50]}")
print()

print("="*60)
if all_ok:
    print(f"{GREEN}✅ SISTEMA LISTO PARA OPERAR{RESET}")
else:
    print(f"{YELLOW}⚠️  REVISA LOS ERRORES ANTES DE CONTINUAR{RESET}")
print("="*60)
print()
print("📋 PRÓXIMOS PASOS:")
print("1. Ejecuta: uvicorn main:app --reload")
print("2. En otra terminal: ngrok http 8000")
print("3. Copia la URL de ngrok y configúrala en Twilio")
print("4. Envía un mensaje de prueba desde WhatsApp")
print()
