from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def guardar_venta_pendiente(whatsapp_id, plan, foto_url, usuario_mikrotik=None, plan_solicitado=None, dias_solicitados=1):
    """
    Guarda una venta pendiente de aprobación.
    
    Args:
        whatsapp_id: Número de WhatsApp del cliente
        plan: Nombre del plan (para referencia)
        foto_url: URL del comprobante de pago
        usuario_mikrotik: Usuario en MikroTik Hotspot
        plan_solicitado: Nombre del plan solicitado
        dias_solicitados: Cantidad de días a activar
    """
    data = {
        "whatsapp_id": whatsapp_id,
        "dias_solicitados": dias_solicitados,
        "estado": "pendiente",
        "foto_comprobante": foto_url,
        "usuario_mikrotik": usuario_mikrotik,
        "plan_solicitado": plan_solicitado or plan
    }
    
    try:
        # Insertamos en la tabla 'ventas'
        response = supabase.table("ventas").insert(data).execute()
        
        # Devolvemos el ID de la venta para usarlo en Telegram
        return response.data[0]['id'] if response.data else None
    except Exception as e:
        print(f"❌ Error guardando venta: {e}")
        return None

def obtener_venta(venta_id):
    response = supabase.table("ventas").select("*").eq("id", venta_id).execute()
    return response.data[0] if response.data else None

def actualizar_estado_venta(venta_id, nuevo_estado):
    supabase.table("ventas").update({"estado": nuevo_estado}).eq("id", venta_id).execute()


def obtener_contexto_conversacion(phone_number: str) -> dict:
    """Obtiene el contexto de conversación desde Supabase"""
    try:
        response = supabase.table("conversation_context")\
            .select("context_data")\
            .eq("phone_number", phone_number)\
            .execute()
        
        if response.data:
            return response.data[0].get("context_data", {})
        return None
    except Exception as e:
        print(f"Error obteniendo contexto: {e}")
        return None


def guardar_contexto_conversacion(phone_number: str, context_data: dict):
    """Guarda o actualiza el contexto de conversación en Supabase"""
    try:
        # Usar upsert con on_conflict para insertar o actualizar basado en phone_number
        supabase.table("conversation_context").upsert({
            "phone_number": phone_number,
            "context_data": context_data,
            "current_topic": "idle"
        }, on_conflict="phone_number").execute()
    except Exception as e:
        print(f"Error guardando contexto: {e}")