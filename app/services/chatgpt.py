"""
Servicio de ChatGPT para respuestas IA
Proporciona respuestas conversacionales para clientes con cache e historial
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict, List
from openai import OpenAI, RateLimitError, APIError
from app.core.config import settings

# Cliente OpenAI (API v1.0+)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ============================================================================
# FUNCIONES AUXILIARES PARA CACHE (Sin BD por ahora - comentadas para futuro)
# ============================================================================

def _generate_prompt_hash(prompt: str) -> str:
    """Genera hash SHA256 del prompt para caching."""
    return hashlib.sha256(prompt.encode()).hexdigest()


def _get_conversation_history(phone_number: str, limit: int = 5) -> List[Dict]:
    """
    Obtiene el historial de conversación reciente del cliente desde Supabase.
    Proporciona contexto a ChatGPT para respuestas más inteligentes.
    
    Args:
        phone_number: Número de teléfono del cliente
        limit: Cantidad de mensajes previos a recuperar (default 5)
    
    Returns:
        Lista de dicts con formato [{role: "user/assistant", content: "..."}]
    """
    try:
        from app.services.supabase import supabase
        
        # Obtener últimos mensajes del cache
        response = supabase.table("conversation_cache")\
            .select("user_message, ai_response, created_at")\
            .eq("phone_number", phone_number)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        if not response.data:
            return []
        
        # Convertir a formato ChatGPT (más reciente al final)
        history = []
        for msg in reversed(response.data):  # Invertir para orden cronológico
            history.append({"role": "user", "content": msg["user_message"]})
            history.append({"role": "assistant", "content": msg["ai_response"]})
        
        return history
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return []

def obtener_respuesta_chatgpt(mensaje_usuario: str, phone_number: str = None) -> dict:
    """
    Obtiene respuesta de ChatGPT para un mensaje del usuario.
    Usa function calling para detectar acciones técnicas.
    
    Args:
        mensaje_usuario: Texto del mensaje del cliente
        phone_number: Número de teléfono del cliente (opcional, para futuro cache)
    
    Returns:
        dict con: {
            "respuesta": str - Mensaje para el cliente,
            "accion": str | None - Acción a ejecutar ("crear_usuario", "buscar_usuario", None),
            "datos": dict | None - Datos para la acción
        }
    """
    try:
        # Sistema prompt para conversación natural con cliente
        system_prompt = """Eres asistente de ventas de internet ISP. Habla naturalmente como vendedor peruano.

PLANES: S/1 por día (ej: 5 días = S/5, 7 días = S/7, 30 días = S/30)

PRIMERO SIEMPRE PREGUNTA:
- Si el cliente NO menciona su usuario → Pregunta: "¿Ya eres cliente o eres nuevo?"
- Si dice que es NUEVO → Sigue flujo de nuevos
- Si dice que YA ES CLIENTE o menciona su usuario → Sigue flujo de existentes

FLUJO PARA NUEVOS CLIENTES:
1. Ya confirmó que es nuevo
2. Pregunta nombre completo
3. Pregunta usuario deseado (ej: ricky3)
4. Pregunta zona (Centro/Goza/Cocha)
5. Di: "Perfecto! Te creo tu usuario con 1 día GRATIS para que pruebes el servicio 🎁"
6. USA la función crear_usuario_nuevo con los datos

FLUJO PARA CLIENTES EXISTENTES (IMPORTANTE):
1. Si NO mencionó su usuario → Pregunta: "¿Cuál es tu usuario?"
2. Si SÍ mencionó usuario (ej: "mi usuario es pepa") → USA función buscar_usuario_existente
3. Después de encontrar usuario, pregunta: "¿Cuántos días quieres recargar?"
4. Cliente responde cantidad (ej: "5 días", "quiero 3", etc)
5. OBLIGATORIO: USA función registrar_pedido(usuario=X, dias=Y)
   - La función responderá automáticamente al cliente
   - NO respondas con texto, SOLO llama la función
6. Cliente envía foto → Sistema guarda automáticamente
7. Admin aprueba en Telegram → Se activan los días

CRÍTICO: Cuando cliente dice cantidad de días, SIEMPRE llamar registrar_pedido, NUNCA responder con texto.

REGLAS CRÍTICAS:
- USA registrar_pedido cuando el cliente dice cuántos días quiere
- NO actives internet automáticamente, solo registra el pedido
- Los días se activan SOLO cuando el admin aprueba el pago en Telegram
- Sé natural, cercano, usa emojis
- Máximo 3 líneas por respuesta

SOPORTE TÉCNICO:
- Si el cliente tiene problemas técnicos (no puede conectar, lento, etc)
- Dile: "Para soporte técnico escríbenos al +51987654321 📲"
- NO intentes resolver problemas técnicos, solo deriva al número
- Ejemplos de problemas: "no me conecta", "está lento", "se cae", "no carga" """

        # Definir funciones disponibles para ChatGPT
        functions = [
            {
                "name": "crear_usuario_nuevo",
                "description": "Crea un usuario nuevo en el sistema MikroTik con 3 días gratis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre_completo": {
                            "type": "string",
                            "description": "Nombre completo del cliente"
                        },
                        "usuario": {
                            "type": "string",
                            "description": "Nombre de usuario elegido (ej: ricky3)"
                        },
                        "zona": {
                            "type": "string",
                            "description": "Zona del cliente (Centro, Goza, Cocha, etc)"
                        }
                    },
                    "required": ["nombre_completo", "usuario", "zona"]
                }
            },
            {
                "name": "buscar_usuario_existente",
                "description": "Busca un usuario existente en el sistema",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "usuario": {
                            "type": "string",
                            "description": "Nombre de usuario a buscar"
                        }
                    },
                    "required": ["usuario"]
                }
            },
            {
                "name": "registrar_pedido",
                "description": "LLAMAR SIEMPRE cuando cliente dice cuántos días quiere (ej: '5 días', 'quiero 3', '7 dias'). Esta función guarda el pedido y responde automáticamente. NO respondas con texto después de llamar esta función.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dias": {
                            "type": "integer",
                            "description": "Cantidad de días que el cliente quiere comprar"
                        }
                    },
                    "required": ["dias"]
                }
            }
        ]
        
        # Construir mensajes con historial
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial de conversación si existe
        if phone_number:
            history = _get_conversation_history(phone_number, limit=5)
            if history:
                print(f"📚 Historial recuperado: {len(history)} mensajes previos")
            messages.extend(history)
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": mensaje_usuario})
        
        print(f"💬 Total mensajes a ChatGPT: {len(messages)} (system + historial + actual)")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=functions,
            function_call="auto",
            temperature=0.7,
            max_tokens=150,
        )
        
        message = response.choices[0].message
        
        # Si ChatGPT quiere llamar una función
        if message.function_call:
            import json
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            print(f"🤖 ChatGPT llama función: {function_name} con {function_args}")
            
            return {
                "respuesta": None,  # Se generará después de ejecutar la función
                "accion": function_name,
                "datos": function_args
            }
        
        # Respuesta normal sin función
        response_text = message.content
        print(f"✅ ChatGPT respondió: {response_text[:50]}...")
        
        return {
            "respuesta": response_text,
            "accion": None,
            "datos": None
        }
    
    except RateLimitError:
        print("❌ Rate limit de OpenAI excedido")
        return {
            "respuesta": "Estoy recibiendo muchas solicitudes. Intenta en un momento.",
            "accion": None,
            "datos": None
        }
    
    except APIError as e:
        print(f"❌ Error de API OpenAI: {e}")
        return {
            "respuesta": "Tengo un problema técnico. Intenta más tarde.",
            "accion": None,
            "datos": None
        }
    
    except Exception as e:
        print(f"❌ Error en ChatGPT: {e}")
        return {
            "respuesta": "Lo siento, tengo un problema técnico. Intenta de nuevo.",
            "accion": None,
            "datos": None
        }


def obtener_respuesta_chatgpt_streaming(mensaje_usuario: str):
    """
    Obtiene respuesta de ChatGPT con streaming (para futuro uso en WebSockets).
    Usa prompt optimizado igual que la versión no-streaming.
    
    Args:
        mensaje_usuario: Texto del mensaje del cliente
    
    Yields:
        Chunks de la respuesta
    """
    try:
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Eres Bot ISP, asistente de internet amable y breve.
Vende planes (hora, día, mes). Para compras, pide foto del comprobante.
Responde en 1-2 líneas máximo. Sé directo."""
                },
                {
                    "role": "user",
                    "content": mensaje_usuario
                }
            ],
            temperature=0.7,
            max_tokens=120,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    except RateLimitError:
        yield "❌ Estoy recibiendo muchas solicitudes. Intenta en un momento."
    except APIError as e:
        yield f"❌ Error técnico: {str(e)}"
    except Exception as e:
        yield f"❌ Error: {str(e)}"
    except Exception as e:
        print(f"❌ Error en ChatGPT streaming: {e}")
        yield "Lo siento, tengo un problema técnico."


def guardar_conversacion_cache(phone_number: str, user_message: str, ai_response: str, tokens_used: int = 0):
    """
    Guarda la conversación en Supabase para cache/historial.
    
    Args:
        phone_number: Número del cliente
        user_message: Mensaje del usuario
        ai_response: Respuesta de la IA
        tokens_used: Tokens consumidos (opcional)
    """
    try:
        from app.services.supabase import supabase
        
        supabase.table("conversation_cache").insert({
            "phone_number": phone_number,
            "user_message": user_message,
            "ai_response": ai_response,
            "tokens_used": tokens_used,
            "conversation_topic": "general"
        }).execute()
    except Exception as e:
        print(f"Error guardando cache de conversación: {e}")
