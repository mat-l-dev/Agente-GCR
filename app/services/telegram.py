import requests
from app.core.config import settings

def enviar_alerta_pago(venta_id, whatsapp_id, plan, foto_url):
    """
    Envía una alerta a Telegram con botones inline cuando se recibe un comprobante de pago.
    
    Args:
        venta_id: ID de la venta en Supabase
        whatsapp_id: Número de WhatsApp del cliente
        plan: Nombre del plan contratado
        foto_url: URL pública de la imagen del comprobante (provista por Twilio)
    """
    mensaje = (
        f"🚨 <b>NUEVA SOLICITUD DE PAGO</b> 🚨\n\n"
        f"👤 <b>Cliente:</b> {whatsapp_id}\n"
        f"📦 <b>Plan:</b> {plan}\n"
        f"🖼 <b>Comprobante:</b> <a href='{foto_url}'>Ver imagen</a>\n\n"
        f"¿Aprobar y crear ficha?"
    )
    
    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"
    
    # Botones Inline
    teclado = {
        "inline_keyboard": [
            [
                {"text": "✅ APROBAR", "callback_data": f"aprobar_{venta_id}"},
                {"text": "❌ RECHAZAR", "callback_data": f"rechazar_{venta_id}"}
            ]
        ]
    }
    
    payload = {
        "chat_id": settings.TG_ADMIN_ID,
        "text": mensaje,
        "parse_mode": "HTML",
        "reply_markup": teclado
    }
    
    try:
        requests.post(url, json=payload)
        print("✅ Alerta enviada a Telegram")
    except Exception as e:
        print(f"❌ Error Telegram: {e}")