#!/usr/bin/env python3
"""
Script de verificación del proyecto Bot ISP
Valida configuración, imports, sintaxis y estructura
"""

import sys
import os
from pathlib import Path

def check_env_example():
    """Verifica que .env.example tenga todas las variables necesarias"""
    print("🔍 Verificando .env.example...")
    
    required_vars = [
        "PORT",
        "ENV_STATE",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_NUMBER",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ADMIN_ID",
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "MIKROTIK_HOST",
        "MIKROTIK_PORT",
        "MIKROTIK_USER",
        "MIKROTIK_PASS",
        "PLAN_INICIAL_NUEVO",
        "PRECIO_POR_DIA"
    ]
    
    env_example = Path(".env.example")
    if not env_example.exists():
        print("❌ .env.example no existe")
        return False
    
    content = env_example.read_text(encoding='utf-8')
    missing = []
    
    for var in required_vars:
        if f"{var}=" not in content:
            missing.append(var)
    
    if missing:
        print(f"❌ Variables faltantes en .env.example: {', '.join(missing)}")
        return False
    
    print("✅ .env.example tiene todas las variables necesarias")
    return True


def check_python_syntax():
    """Verifica sintaxis de todos los archivos Python principales"""
    print("\n🔍 Verificando sintaxis Python...")
    
    files_to_check = [
        "main.py",
        "app/core/config.py",
        "app/routers/webhook_wa.py",
        "app/routers/webhook_tg.py",
        "app/services/chatgpt.py",
        "app/services/mikrotik.py",
        "app/services/supabase.py",
        "app/services/telegram.py",
        "app/services/whatsapp.py",
    ]
    
    errors = []
    
    for file_path in files_to_check:
        if not Path(file_path).exists():
            print(f"⚠️  {file_path} no existe")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"  ✅ {file_path}")
        except SyntaxError as e:
            errors.append(f"{file_path}: {e}")
            print(f"  ❌ {file_path}: {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} archivos con errores de sintaxis")
        return False
    
    print("✅ Todos los archivos Python tienen sintaxis correcta")
    return True


def check_imports():
    """Verifica que los imports principales funcionen"""
    print("\n🔍 Verificando imports principales...")
    
    try:
        from app.core.config import settings
        print("  ✅ app.core.config")
    except Exception as e:
        print(f"  ❌ app.core.config: {e}")
        return False
    
    try:
        from app.services import chatgpt, mikrotik, whatsapp, telegram, supabase
        print("  ✅ app.services.*")
    except Exception as e:
        print(f"  ❌ app.services.*: {e}")
        return False
    
    try:
        from app.routers import webhook_wa, webhook_tg
        print("  ✅ app.routers.*")
    except Exception as e:
        print(f"  ❌ app.routers.*: {e}")
        return False
    
    print("✅ Todos los imports funcionan correctamente")
    return True


def check_requirements():
    """Verifica que requirements.txt tenga los paquetes necesarios"""
    print("\n🔍 Verificando requirements.txt...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "twilio",
        "supabase",
        "openai",
        "python-telegram-bot",
        "RouterOS-api",
        "pyperclip"
    ]
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt no existe")
        return False
    
    content = req_file.read_text().lower()
    missing = []
    
    for pkg in required_packages:
        if pkg.lower() not in content:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Paquetes faltantes en requirements.txt: {', '.join(missing)}")
        return False
    
    print("✅ requirements.txt tiene todos los paquetes necesarios")
    return True


def check_structure():
    """Verifica la estructura de directorios del proyecto"""
    print("\n🔍 Verificando estructura del proyecto...")
    
    required_dirs = [
        "app",
        "app/core",
        "app/routers",
        "app/services",
        "migrations",
        "docs",
        "tests"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Directorios faltantes: {', '.join(missing)}")
        return False
    
    print("✅ Estructura de directorios correcta")
    return True


def main():
    """Ejecuta todas las verificaciones"""
    print("="*60)
    print("🤖 VERIFICACIÓN DEL PROYECTO BOT ISP")
    print("="*60)
    
    checks = [
        ("Estructura", check_structure),
        (".env.example", check_env_example),
        ("requirements.txt", check_requirements),
        ("Sintaxis Python", check_python_syntax),
        ("Imports", check_imports),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error en verificación de {name}: {e}")
            results[name] = False
    
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ¡Todas las verificaciones pasaron!")
        print("El proyecto está listo para usar.")
        return 0
    else:
        print("\n⚠️  Hay problemas que requieren atención.")
        print("Revisa los errores arriba y corrígelos.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
