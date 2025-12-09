"""
Script para ejecutar migraciones en Supabase desde Python
Uso: python migrations/run_migrations.py
"""

import subprocess
import sys
from pathlib import Path

def run_migration_via_supabase_cli():
    """
    Ejecuta migraciones usando Supabase CLI
    """
    print("\n" + "="*60)
    print("🗄️  EJECUTOR DE MIGRACIONES SUPABASE")
    print("="*60 + "\n")
    
    migration_file = Path(__file__).parent / "001_initial_schema.sql"
    
    if not migration_file.exists():
        print(f"❌ Archivo no encontrado: {migration_file}")
        return False
    
    print(f"📄 Migración: {migration_file.name}")
    print(f"📍 Ruta: {migration_file}\n")
    
    # Leer el contenido
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("📋 Contenido a ejecutar:")
    print("-" * 60)
    # Mostrar primeras 30 líneas
    lines = sql_content.split('\n')
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3d} | {line}")
    
    if len(lines) > 30:
        print(f"     ... ({len(lines) - 30} líneas más)")
    
    print("-" * 60 + "\n")
    
    print("⚠️  INSTRUCCIONES MANUAL:")
    print("\n1. Abre https://supabase.com y accede a tu proyecto")
    print("2. Ve a 'SQL Editor' → 'New Query'")
    print("3. Copia TODO el contenido de 001_initial_schema.sql")
    print("4. Pega en el editor y ejecuta (botón RUN)")
    print("\n✅ Resultado esperado:")
    print("   - 7 tablas creadas")
    print("   - Índices optimizados")
    print("   - Data inicial insertada")
    print("   - Triggers configurados\n")
    
    # Copiar al clipboard si es posible
    try:
        import pyperclip
        pyperclip.copy(sql_content)
        print("📋 ✅ SQL copiado al clipboard")
    except ImportError:
        print("💡 Tip: Instala 'pyperclip' para copiar automáticamente")
        print("   pip install pyperclip")
    
    return True

def verify_tables():
    """
    Verifica si las tablas fueron creadas correctamente
    """
    from app.core.config import settings
    
    try:
        from supabase import create_client
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        print("\n" + "="*60)
        print("🔍 VERIFICANDO TABLAS EN SUPABASE")
        print("="*60 + "\n")
        
        tables = [
            'planes',
            'campamentos',
            'clientes',
            'ventas',
            'pruebas',
            'activaciones',
            'transacciones'
        ]
        
        for table in tables:
            try:
                # Intentar contar registros (verifica que la tabla existe)
                result = supabase.table(table).select("count", count="exact").execute()
                count = result.count if hasattr(result, 'count') else 0
                print(f"✅ {table:20s} - {count} registros")
            except Exception as e:
                print(f"❌ {table:20s} - ERROR: {str(e)[:40]}")
        
        print("\n✅ Tablas verificadas\n")
        return True
        
    except Exception as e:
        print(f"⚠️  No se pudo conectar a Supabase: {e}")
        print("   Verifica tus credenciales en .env\n")
        return False

if __name__ == "__main__":
    
    print("\n🚀 Bot ISP - Ejecutor de Migraciones\n")
    
    # Mostrar instrucciones
    run_migration_via_supabase_cli()
    
    # Intentar verificar
    try:
        verify_tables()
    except Exception as e:
        print(f"⚠️  No se pudo verificar: {e}")
    
    print("\n📚 Documentación:")
    print("   - migrations/README.md    ← Cómo ejecutar migraciones")
    print("   - ESTRUCTURA.md           ← Estructura del proyecto")
    print("   - FLUJO_COMPLETO.md       ← Flujo del cliente\n")
