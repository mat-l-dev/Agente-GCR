import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Servidor
    PORT = int(os.getenv("PORT", 8000))
    ENV = os.getenv("ENV_STATE", "dev")
    
    # Twilio (WhatsApp)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")  # Ej: "whatsapp:+14155238886"
    
    # Telegram
    TG_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TG_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # ChatGPT (OpenAI)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Gemini (DESHABILITADO - Ver app/services/gemini.py.bak)
    # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # NO SE USA (limitaciones de API)
    
    # MikroTik - Configuración única (1 línea)
    MIKROTIK_HOST = os.getenv("MIKROTIK_HOST")
    MIKROTIK_PORT = int(os.getenv("MIKROTIK_PORT", 8443))
    MIKROTIK_USER = os.getenv("MIKROTIK_USER", "api_bot")
    MIKROTIK_PASS = os.getenv("MIKROTIK_PASS")
    
    # Plan inicial para clientes nuevos (perfil Userman)
    PLAN_INICIAL_NUEVO = os.getenv("PLAN_INICIAL_NUEVO", "3Dias")

    # Precio por día (referencia comercial)
    PRECIO_POR_DIA = float(os.getenv("PRECIO_POR_DIA", 1.0))
    
    def __init__(self):
        """Valida que las variables críticas existan"""
        critical_vars = [
            ("TWILIO_ACCOUNT_SID", self.TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", self.TWILIO_AUTH_TOKEN),
            ("TWILIO_FROM_NUMBER", self.TWILIO_FROM_NUMBER),
            ("TG_BOT_TOKEN", self.TG_BOT_TOKEN),
            ("TG_ADMIN_ID", self.TG_ADMIN_ID),
            ("SUPABASE_URL", self.SUPABASE_URL),
            ("SUPABASE_KEY", self.SUPABASE_KEY),
        ]
        
        missing = [name for name, value in critical_vars if not value]
        
        if missing:
            raise ValueError(
                f"⚠️ Variables de entorno faltantes en .env: {', '.join(missing)}"
            )

settings = Settings()
