from twilio.rest import Client
from app.core.config import settings

def enviar_mensaje_whatsapp(numero, texto):
    """
    Envía un mensaje de WhatsApp usando Twilio API.
    
    Args:
        numero (str): Número del destinatario (puede venir como "+51999..." o "51999...")
        texto (str): Contenido del mensaje
    
    Returns:
        bool: True si se envió correctamente, False en caso de error
    """
    try:
        # Inicializar cliente de Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Formatear el número destino con prefijo "whatsapp:"
        # Si el número no empieza con "+", lo agregamos
        numero_formateado = numero if numero.startswith('+') else f'+{numero}'
        to_number = f"whatsapp:{numero_formateado}"
        
        # Enviar mensaje
        message = client.messages.create(
            body=texto,
            from_=settings.TWILIO_FROM_NUMBER,  # Ya debe venir como "whatsapp:+14155238886"
            to=to_number
        )
        
        print(f"✅ Mensaje enviado a {numero} (SID: {message.sid})")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje con Twilio: {e}")
        return False