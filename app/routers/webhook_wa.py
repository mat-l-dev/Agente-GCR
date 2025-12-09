from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
from app.services.chatgpt import obtener_respuesta_chatgpt, guardar_conversacion_cache
from app.services.whatsapp import enviar_mensaje_whatsapp
from app.services.supabase import (
    guardar_venta_pendiente,
    obtener_contexto_conversacion,
    guardar_contexto_conversacion,
)
from app.services.telegram import enviar_alerta_pago
from app.services.mikrotik import (
    buscar_usuario_existente,
    crear_usuario_userman,
)
from app.core.config import settings

router = APIRouter()


def inicializar_cliente(numero: str):
    """Obtiene el contexto del cliente desde Supabase (o crea uno nuevo)"""
    contexto = obtener_contexto_conversacion(numero)
    if not contexto:
        # Crear contexto nuevo en Supabase
        guardar_contexto_conversacion(numero, {
            "ultimo_usuario": None,
            "plan_solicitado": None,
        })
        contexto = {"ultimo_usuario": None, "plan_solicitado": None}
    return contexto


def ejecutar_accion_bot(accion: str, datos: dict, numero: str) -> str:
    """
    Ejecuta acciones técnicas que ChatGPT solicita.
    
    Args:
        accion: Nombre de la acción ("crear_usuario_nuevo", "buscar_usuario_existente")
        datos: Datos necesarios para la acción
        numero: Número del cliente
    
    Returns:
        Mensaje de respuesta para el cliente
    """
    cliente = inicializar_cliente(numero)
    
    if accion == "crear_usuario_nuevo":
        # ChatGPT tiene todos los datos, crear usuario con 3 días gratis
        import random, string
        password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        exito, msg = crear_usuario_userman(
            usuario=datos["usuario"],
            password=password,
            nombre_completo=datos["nombre_completo"],
            plan="3Dias"
        )
        
        if exito:
            # Guardar contexto actualizado en Supabase
            guardar_contexto_conversacion(numero, {
                "ultimo_usuario": datos["usuario"],
                "plan_solicitado": settings.PLAN_INICIAL_NUEVO,
            })
            return (
                f"✅ ¡Listo {datos['nombre_completo'].split()[0]}!\n\n"
                f"👤 Usuario: {datos['usuario']}\n"
                f"🔑 Contraseña: {password}\n"
                f"🎁 3 días GRATIS para probar\n\n"
                f"Conéctate ya! Cuando se acaben los días, me escribes para recargar 😊"
            )
        else:
            return f"❌ Error al crear usuario: {msg}"
    
    elif accion == "buscar_usuario_existente":
        usuario_data = buscar_usuario_existente(datos["usuario"])
        
        if usuario_data:
            # Guardar usuario en contexto
            guardar_contexto_conversacion(numero, {
                "ultimo_usuario": datos["usuario"],
                "dias_solicitados": None,
            })
            return (
                f"✅ Usuario {datos['usuario']} encontrado!\n"
                f"¿Cuántos días quieres recargar?"
            )
        else:
            return f"❌ Usuario '{datos['usuario']}' no encontrado. Verifica el nombre."
    
    elif accion == "registrar_pedido":
        # El cliente dijo cuántos días quiere - SOLO GUARDAR, NO ACTIVAR NADA
        usuario = datos.get("usuario")
        dias = datos.get("dias", 1)
        
        # Si no tenemos usuario, obtenerlo del contexto
        if not usuario:
            contexto = obtener_contexto_conversacion(numero)
            usuario = contexto.get("ultimo_usuario") if contexto else None
        
        if not usuario:
            return "❌ No tengo tu usuario guardado. ¿Cuál es tu usuario?"
        
        print(f"📝 Registrando pedido: {usuario} quiere {dias} días")
        
        # SOLO guardar en contexto, NO activar nada
        guardar_contexto_conversacion(numero, {
            "ultimo_usuario": usuario,
            "dias_solicitados": dias,
            "pendiente_pago": True,
        })
        
        return (
            f"Dale! Son S/{dias} por {dias} días 💰\n\n"
            f"Envíame tu comprobante de Yape/Plin y te activo al toque 😊"
        )
    
    return "❌ Acción desconocida"





@router.get("/webhook")
async def webhook_verification():
    """Verificación de webhook"""
    return {"status": "Webhook activo", "service": "Twilio WhatsApp"}


@router.post("/webhook")
async def receive_message_twilio(request: Request):
    """
    Webhook para WhatsApp vía Twilio con ChatGPT conversacional.
    Flujo:
    1. Cliente conversa con ChatGPT naturalmente
    2. ChatGPT detecta intención y pide datos necesarios
    3. Cuando tiene todos los datos → llama función (crear_usuario_nuevo o buscar_usuario_existente)
    4. Bot ejecuta acción en MikroTik
    5. Cliente envía comprobante (foto) → Guarda y alerta admin
    6. Admin aprueba en Telegram → Bot actualiza plan
    """
    try:
        form_data = await request.form()
        
        from_number = form_data.get("From", "").replace("whatsapp:", "").strip()
        body_text = form_data.get("Body", "").strip()
        num_media = int(form_data.get("NumMedia", 0))
        media_url = form_data.get("MediaUrl0", "")
        
        print(f"\n{'='*60}")
        print(f"📩 MENSAJE DE {from_number}: {body_text}")
        print(f"{'='*60}\n")
        
        # ============= CASO 1: TEXTO =============
        if body_text and num_media == 0:
            # ChatGPT maneja la conversación y detecta acciones
            resultado = obtener_respuesta_chatgpt(body_text, from_number)
            
            # Si ChatGPT pide ejecutar una acción
            if resultado["accion"]:
                respuesta = ejecutar_accion_bot(resultado["accion"], resultado["datos"], from_number)
                
                # Guardar en cache con la respuesta de la acción
                guardar_conversacion_cache(
                    phone_number=from_number,
                    user_message=body_text,
                    ai_response=respuesta,
                    tokens_used=resultado.get("tokens_used", 0)
                )
            else:
                respuesta = resultado["respuesta"]
                
                # Guardar conversación normal en cache
                guardar_conversacion_cache(
                    phone_number=from_number,
                    user_message=body_text,
                    ai_response=respuesta,
                    tokens_used=resultado.get("tokens_used", 0)
                )
            
            enviar_mensaje_whatsapp(from_number, respuesta)
        
        # ============= CASO 2: IMAGEN (comprobante) =============
        elif num_media > 0 and media_url:
            print(f"📸 Comprobante de {from_number}")
            
            # Obtener contexto del cliente
            contexto = inicializar_cliente(from_number)
            
            # Obtener días solicitados del contexto (o default 1)
            dias_solicitados = contexto.get("dias_solicitados", 1)
            usuario_mikrotik = contexto.get("ultimo_usuario")
            
            print(f"   Usuario: {usuario_mikrotik}, Días solicitados: {dias_solicitados}")
            
            # Guardar en Supabase con usuario y días
            venta_id = guardar_venta_pendiente(
                whatsapp_id=from_number, 
                plan=f"{dias_solicitados} días",
                foto_url=media_url,
                usuario_mikrotik=usuario_mikrotik,
                plan_solicitado=f"1User{dias_solicitados}Dia",
                dias_solicitados=dias_solicitados
            )
            
            if venta_id:
                enviar_alerta_pago(venta_id, from_number, f"{dias_solicitados} días", media_url)
                respuesta = (
                    f"✅ Comprobante recibido!\n\n"
                    f"📋 Usuario: {usuario_mikrotik}\n"
                    f"📅 Días: {dias_solicitados}\n"
                    f"💰 Monto: S/{dias_solicitados}\n\n"
                    f"Un agente lo validará en breve. Gracias! 🙏"
                )
            else:
                respuesta = "❌ Error al procesar el comprobante. Intenta de nuevo o contacta al admin."
            
            enviar_mensaje_whatsapp(from_number, respuesta)
        
        return {"status": "success"}
    
    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error"}


# ============= Funciones antiguas eliminadas =============
# ChatGPT ahora maneja la conversación completa
# Las acciones técnicas se ejecutan vía function calling en ejecutar_accion_bot()
