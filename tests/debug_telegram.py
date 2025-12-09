"""
Script para verificar qué se guarda en Supabase y cómo se crea el callback_data
"""
from app.core.config import settings
from app.services.supabase import guardar_venta_pendiente, obtener_venta
from app.services.telegram import enviar_alerta_pago

# Test 1: Guardar una venta
print("\n🔍 TEST 1: Guardar venta en Supabase")
venta_id = guardar_venta_pendiente("+51999888777", "Plan Test", "https://via.placeholder.com/500")
print(f"   Venta ID retornado: {venta_id} (tipo: {type(venta_id)})")

if venta_id:
    # Test 2: Recuperar la venta
    print("\n🔍 TEST 2: Recuperar venta de Supabase")
    venta = obtener_venta(venta_id)
    print(f"   Venta recuperada: {venta}")
    
    # Test 3: Verificar formato del callback_data
    print("\n🔍 TEST 3: Verificar callback_data")
    callback_aprobar = f"aprobar_{venta_id}"
    callback_rechazar = f"rechazar_{venta_id}"
    print(f"   Callback APROBAR: {callback_aprobar} (largo: {len(callback_aprobar)})")
    print(f"   Callback RECHAZAR: {callback_rechazar} (largo: {len(callback_rechazar)})")
    
    # Test 4: Intentar enviar alerta a Telegram
    print("\n🔍 TEST 4: Enviando alerta a Telegram con callback_data correcto")
    try:
        enviar_alerta_pago(venta_id, "+51999888777", "Plan Test", "https://via.placeholder.com/500")
        print("   ✅ Alerta enviada a Telegram")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ❌ Error: venta_id es None, no se guardó correctamente")
