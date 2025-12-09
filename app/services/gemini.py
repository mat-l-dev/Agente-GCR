"""
ARCHIVO DESHABILITADO - Usar ChatGPT en su lugar

Este archivo usaba Google Gemini pero la API no permite compras en el plan actual.
Se ha reemplazado por ChatGPT que tiene más flexibilidad en pagos.

Para una próxima migración a Gemini con acceso a API pagada, 
restaurar este archivo desde: gemini.py.bak
"""

# import google.generativeai as genai
# from app.core.config import settings

# # Configurar la API Key
# genai.configure(api_key=settings.GOOGLE_API_KEY)

# # Configuración del modelo
# generation_config = {
#     "temperature": 0.7, # Creatividad controlada
#     "top_p": 1,
#     "top_k": 1,
#     "max_output_tokens": 2048,
# }

# # El cerebro de la IA
# model = genai.GenerativeModel(
#     model_name="gemini-2.0-flash-exp", # Versión 2.0 más rápida
#     generation_config=generation_config,
#     system_instruction="""
#     Eres el asistente virtual amable de un ISP (Proveedor de Internet).
#     Tu nombre es 'Bot ISP'.
#     
#     Tus objetivos son:
#     1. Vender planes de internet (1 Hora, 1 Día, 1 Mes).
#     2. Resolver dudas básicas.
#     3. Si el cliente quiere comprar, dile que envíe una FOTO de su comprobante de pago o transferencia.
#     
#     Sé breve, directo y muy amable. No uses textos muy largos.
#     """
# )

# def obtener_respuesta_gemini(mensaje_usuario):
#     try:
#         # Iniciamos un chat sin historial por ahora (simple)
#         chat = model.start_chat(history=[])
#         response = chat.send_message(mensaje_usuario)
#         return response.text
#     except Exception as e:
#         print(f"❌ Error en Gemini: {e}")
#         return "Lo siento, tengo un problema técnico en mi cerebro ahora mismo."