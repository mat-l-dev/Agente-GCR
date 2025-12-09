import requests
from fastapi import APIRouter, Request
from app.core.config import settings
from app.services.supabase import obtener_venta, actualizar_estado_venta
from app.services.mikrotik import reemplazar_plan_usuario
from app.services.whatsapp import enviar_mensaje_whatsapp

router = APIRouter()

def responder_callback_telegram(callback_query_id: str, texto: str = "Procesado"):
    """
    Responde a Telegram para que el botón deje de mostrar 'cargando'
    """
    bot_token = settings.TG_BOT_TOKEN
    if not bot_token:
        print("⚠️ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id,
        "text": texto,
        "show_alert": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print("✅ Callback respondido a Telegram")
        else:
            print(f"⚠️ Error al responder callback: {response.text}")
    except Exception as err:
        print(f"❌ Error en answerCallbackQuery: {err}")


@router.post("/telegram")
async def receive_telegram(request: Request):
    """
    Webhook que recibe los clics de los botones de Telegram
    """
    # 🔍 PASO 1: LOGGING COMPLETO DEL JSON RECIBIDO
    try:
        data = await request.json()
        print("\n" + "="*60)
        print("📩 WEBHOOK TELEGRAM RECIBIDO:")
        print(f"JSON completo: {data}")
        print("="*60 + "\n")
    except Exception as err:
        print(f"❌ Error al parsear JSON de Telegram: {err}")
        return {"status": "error", "message": "JSON inválido"}
    
    # 🔍 PASO 2: VERIFICAR SI ES UN CALLBACK_QUERY
    if "callback_query" not in data:
        print("⚠️ No es un callback_query, ignorando...")
        return {"status": "ignored", "reason": "not_a_callback"}
    
    callback = data["callback_query"]
    callback_query_id = callback.get("id")
    data_btn = callback.get("data", "")
    
    print(f"🔘 Callback ID: {callback_query_id}")
    print(f"🔘 Data del botón: '{data_btn}'")
    
    # 🔍 PASO 3: VALIDAR FORMATO DEL CALLBACK_DATA
    try:
        if "_" not in data_btn:
            raise ValueError(f"Formato inválido: '{data_btn}' (esperado: 'accion_id')")
        
        accion, venta_id_str = data_btn.split("_", 1)  # split con maxsplit=1 por si el ID tiene guiones
        
        # Convertir venta_id a entero
        try:
            venta_id = int(venta_id_str)
        except ValueError:
            raise ValueError(f"ID de venta inválido: '{venta_id_str}' no es un número")
        
        print(f"🎯 Acción: {accion}, Venta ID: {venta_id} (tipo: {type(venta_id).__name__})")
        
    except ValueError as e:
        print(f"❌ Error al procesar callback_data: {e}")
        responder_callback_telegram(callback_query_id, "❌ Formato de datos inválido")
        return {"status": "error", "message": str(e)}
    
    # 🔍 PASO 4: BUSCAR LA VENTA EN LA BASE DE DATOS
    try:
        venta = obtener_venta(venta_id)
        if not venta:
            print(f"❌ Venta {venta_id} no encontrada en la base de datos")
            responder_callback_telegram(callback_query_id, "❌ Venta no encontrada")
            return {"status": "error", "message": "venta_no_encontrada"}
        
        cliente_wa = venta.get("whatsapp_id")
        print(f"📱 Cliente WhatsApp: {cliente_wa}")
        
    except Exception as err:
        print(f"❌ Error al consultar la venta: {err}")
        responder_callback_telegram(callback_query_id, "❌ Error de base de datos")
        return {"status": "error", "message": str(err)}
    
    # 🔍 PASO 5: PROCESAR LA ACCIÓN (APROBAR O RECHAZAR)
    try:
        if accion == "aprobar":
            print(f"✅ Procesando APROBACIÓN de venta {venta_id}...")
            
            # Obtener datos del cliente desde venta
            usuario = venta.get("usuario_mikrotik")  # Debe guardarse cuando ChatGPT crea usuario
            dias_solicitados = venta.get("dias_solicitados", 1)
            plan_solicitado = venta.get("plan_solicitado", f"1User{dias_solicitados}Dia")
            
            if not usuario:
                print(f"⚠️ Venta {venta_id} no tiene usuario asociado")
                responder_callback_telegram(callback_query_id, "⚠️ Sin usuario asociado")
                return {"status": "error", "message": "no_usuario"}
            
            # 1. REEMPLAZAR plan en MikroTik (elimina el temporal y pone el completo)
            exito, msg = reemplazar_plan_usuario(usuario, plan_solicitado)
            
            if exito:
                # 2. Actualizar estado en Supabase
                actualizar_estado_venta(venta_id, "aprobado")
                
                # 3. Notificar al cliente (SIN información técnica)
                mensaje = (
                    f"✅ ¡Pago Aprobado!\n\n"
                    f"🎉 Ya tienes {dias_solicitados} días de internet activados.\n\n"
                    f"¡Disfruta tu conexión! 🌐\n\n"
                    f"📲 Soporte: +51987654321"
                )
                enviar_mensaje_whatsapp(cliente_wa, mensaje)
                
                print(f"✅ Venta {venta_id} aprobada. {dias_solicitados} días activados para {usuario}")
                responder_callback_telegram(callback_query_id, f"✅ {usuario}: {dias_solicitados}d OK")
                
            else:
                # MikroTik no disponible, pero aprobar igual
                print(f"⚠️ MikroTik error: {msg}, pero aprobando venta {venta_id}")
                actualizar_estado_venta(venta_id, "aprobado")
                mensaje = (
                    f"✅ ¡Pago Aprobado!\n\n"
                    f"Estamos activando tu internet. Espera unos minutos.\n\n"
                    f"Si tienes problemas, escríbenos al +51987654321"
                )
                enviar_mensaje_whatsapp(cliente_wa, mensaje)
                responder_callback_telegram(callback_query_id, "✅ Aprobado (error MikroTik)")

        
        elif accion == "rechazar":
            print(f"🚫 Procesando RECHAZO de venta {venta_id}...")
            
            # 1. Actualizar estado en Supabase
            actualizar_estado_venta(venta_id, "rechazado")
            
            # 2. Notificar al cliente
            enviar_mensaje_whatsapp(cliente_wa, "❌ Tu pago fue rechazado. Por favor contacta a soporte.")
            
            print(f"🚫 Venta {venta_id} rechazada")
            responder_callback_telegram(callback_query_id, "🚫 Venta rechazada")
        
        else:
            print(f"⚠️ Acción desconocida: '{accion}'")
            responder_callback_telegram(callback_query_id, f"⚠️ Acción '{accion}' no reconocida")
            return {"status": "error", "message": f"unknown_action: {accion}"}
    
    except Exception as err:
        print(f"❌ Error al procesar la acción '{accion}': {err}")
        responder_callback_telegram(callback_query_id, "❌ Error al procesar")
        return {"status": "error", "message": str(err)}
    
    # ✅ TODO OK
    print(f"✅ Webhook de Telegram procesado exitosamente\n")
    return {"status": "success", "action": accion, "venta_id": venta_id}
