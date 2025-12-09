#!/usr/bin/env python
"""
Script de prueba para verificar la integración con MikroTik.
Prueba todas las funciones principales sin necesidad de MikroTik real.
"""

from app.services.mikrotik import (
    generar_credenciales,
    obtener_planes_disponibles,
    buscar_usuario_existente,
    crear_usuario_userman,
    actualizar_usuario_plan,
    conectar_mikrotik
)

def main():
    print("\n" + "="*70)
    print("🧪 TEST DE INTEGRACIÓN MIKROTIK")
    print("="*70 + "\n")
    
    # Test 1: Generar credenciales
    print("1️⃣  Probando generar_credenciales()...")
    usuario, password = generar_credenciales()
    print(f"   ✅ Usuario: {usuario}")
    print(f"   ✅ Contraseña: {password}\n")
    
    # Test 2: Conectar a MikroTik
    print("2️⃣  Probando conexión a MikroTik...")
    connection, api = conectar_mikrotik()
    if connection and api:
        print("   ✅ Conexión exitosa\n")
        connection.disconnect()
    else:
        print("   ⚠️  MikroTik no accesible (es OK si no está configurado)\n")
    
    # Test 3: Obtener planes disponibles
    print("3️⃣  Obteniendo planes disponibles...")
    if planes := obtener_planes_disponibles():
        print(f"   ✅ {len(planes)} planes encontrados:")
        for plan in planes:
            print(f"      - {plan['nombre']}: {plan['validez']} (${plan['precio']})")
    else:
        print("   ⚠️  No hay planes (MikroTik no disponible)\n")
    print()
    
    # Test 4: Buscar usuario existente
    print("4️⃣  Buscando usuario existente (test_usuario)...")
    if usuario_data := buscar_usuario_existente("test_usuario"):
        print(f"   ✅ Usuario encontrado: {usuario_data}")
    else:
        print("   ℹ️  Usuario no existe (es OK para primera prueba)\n")
    
    # Test 5: Crear usuario (simulado)
    print("5️⃣  Intentando crear usuario (será exitoso si MikroTik está disponible)...")
    nuevo_usuario, msg = crear_usuario_userman(
        usuario="testbot123",
        password="pass456",
        nombre_completo="Test User",
        plan="1Dia"
    )
    print(f"   Resultado: {msg}\n")
    
    # Test 6: Actualizar plan (simulado)
    print("6️⃣  Intentando actualizar plan...")
    exito, msg = actualizar_usuario_plan("testbot123", "3Dias")
    print(f"   Resultado: {msg}\n")
    
    print("="*70)
    print("✅ TESTS COMPLETADOS")
    print("="*70)
    print("\nℹ️  PROXIMOS PASOS:")
    print("   1. Conectar MikroTik (ver GUIA_MIKROTIK_SETUP.md)")
    print("   2. Crear planes en Userman (1Dia, 3Dias, 1Semana, 1Mes)")
    print("   3. Ejecutar este script nuevamente para verificar conexión")
    print("   4. Probar webhook de WhatsApp\n")

if __name__ == "__main__":
    main()
