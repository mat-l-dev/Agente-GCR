"""
Script de prueba para verificar la conexión y comandos de MikroTik User Manager.
Ejecutar: python test_mikrotik_userman.py

Este script te ayudará a:
1. Verificar la conexión a MikroTik
2. Listar los planes/perfiles disponibles
3. Listar los usuarios existentes  
4. Probar la asignación de perfil a un usuario
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar routeros-api
try:
    import routeros_api
except ImportError:
    print("❌ Error: routeros-api no está instalado")
    print("   Ejecuta: pip install routeros-api")
    sys.exit(1)


def conectar():
    """Conecta a MikroTik y retorna (conexión, api)"""
    host = os.getenv("MIKROTIK_HOST")
    port = int(os.getenv("MIKROTIK_PORT", 8728))
    user = os.getenv("MIKROTIK_USER", "admin")
    password = os.getenv("MIKROTIK_PASS", "")
    
    print(f"🔌 Conectando a {host}:{port} como {user}...")
    
    try:
        connection = routeros_api.RouterOsApiPool(
            host=host,
            username=user,
            password=password,
            port=port,
            plaintext_login=True  # RouterOS 6.43+
        )
        api = connection.get_api()
        print("✅ Conectado exitosamente!\n")
        return connection, api
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None, None


def listar_perfiles(api):
    """Lista todos los perfiles/planes en User Manager"""
    print("="*60)
    print("📋 PERFILES/PLANES EN USER MANAGER")
    print("="*60)
    
    try:
        profiles = api.get_resource('/tool/user-manager/profile').get()
        
        if not profiles:
            print("⚠️ No hay perfiles configurados")
            return []
        
        for i, profile in enumerate(profiles, 1):
            print(f"\n{i}. {profile.get('name')}")
            print(f"   ID: {profile.get('id') or profile.get('.id')}")
            print(f"   Validez: {profile.get('validity', 'N/A')}")
            print(f"   Precio: {profile.get('price', 'N/A')}")
            print(f"   Rate Limit: {profile.get('rate-limit-rx', 'N/A')}/{profile.get('rate-limit-tx', 'N/A')}")
            print(f"   Usuarios compartidos: {profile.get('shared-users', 'N/A')}")
        
        print(f"\n✅ Total: {len(profiles)} perfiles")
        return profiles
        
    except Exception as e:
        print(f"❌ Error listando perfiles: {e}")
        return []


def listar_usuarios(api, limit=10):
    """Lista los usuarios en User Manager"""
    print("\n" + "="*60)
    print("👥 USUARIOS EN USER MANAGER")
    print("="*60)
    
    try:
        users = api.get_resource('/tool/user-manager/user').get()
        
        if not users:
            print("⚠️ No hay usuarios configurados")
            return []
        
        for i, user in enumerate(users[:limit], 1):
            print(f"\n{i}. Username: {user.get('username') or user.get('name')}")
            print(f"   ID: {user.get('id') or user.get('.id')}")
            print(f"   Customer: {user.get('customer', 'N/A')}")
            print(f"   Disabled: {user.get('disabled', 'N/A')}")
            print(f"   Last Seen: {user.get('last-seen', 'Nunca')}")
            # Mostrar todas las claves para depuración
            print(f"   [Claves: {list(user.keys())}]")
        
        if len(users) > limit:
            print(f"\n... y {len(users) - limit} usuarios más")
        
        print(f"\n✅ Total: {len(users)} usuarios")
        return users
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {e}")
        return []


def listar_user_profiles(api):
    """Lista las asignaciones usuario-perfil"""
    print("\n" + "="*60)
    print("🔗 ASIGNACIONES USUARIO-PERFIL")
    print("="*60)
    
    try:
        user_profiles = api.get_resource('/tool/user-manager/user-profile').get()
        
        if not user_profiles:
            print("⚠️ No hay asignaciones usuario-perfil")
            return []
        
        for i, up in enumerate(user_profiles[:10], 1):
            print(f"\n{i}. Usuario: {up.get('user')} -> Perfil: {up.get('profile')}")
            print(f"   Estado: {up.get('state', 'N/A')}")
            print(f"   End Time: {up.get('end-time', 'N/A')}")
        
        print(f"\n✅ Total: {len(user_profiles)} asignaciones")
        return user_profiles
        
    except Exception as e:
        print(f"❌ Error listando user-profiles: {e}")
        return []


def probar_asignar_perfil(api, usuario: str, perfil: str):
    """Prueba diferentes métodos para asignar un perfil a un usuario"""
    print("\n" + "="*60)
    print(f"🧪 PROBANDO ASIGNACIÓN DE PERFIL")
    print(f"   Usuario: {usuario}")
    print(f"   Perfil: {perfil}")
    print("="*60)
    
    user_resource = api.get_resource('/tool/user-manager/user')
    
    # Método 1: create-and-activate-profile
    print("\n📝 Método 1: create-and-activate-profile")
    try:
        result = user_resource.call('create-and-activate-profile', {
            'numbers': usuario,
            'profile': perfil
        })
        print(f"   ✅ Éxito! Resultado: {result}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Método 2: Agregar en user-profile
    print("\n📝 Método 2: Agregar en /tool/user-manager/user-profile")
    try:
        user_profile_resource = api.get_resource('/tool/user-manager/user-profile')
        result = user_profile_resource.add(
            user=usuario,
            profile=perfil
        )
        print(f"   ✅ Éxito! Resultado: {result}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Método 3: Usando call con add
    print("\n📝 Método 3: call('add') en user-profile")
    try:
        user_profile_resource = api.get_resource('/tool/user-manager/user-profile')
        result = user_profile_resource.call('add', {
            'user': usuario,
            'profile': perfil
        })
        print(f"   ✅ Éxito! Resultado: {result}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n⚠️ Ningún método funcionó. Revisa los nombres de usuario y perfil.")
    return False


def ver_comandos_disponibles(api):
    """Intenta listar comandos disponibles en user-manager"""
    print("\n" + "="*60)
    print("🔧 EXPLORANDO COMANDOS DISPONIBLES")
    print("="*60)
    
    rutas = [
        '/tool/user-manager',
        '/tool/user-manager/user',
        '/tool/user-manager/profile',
        '/tool/user-manager/user-profile',
        '/tool/user-manager/session',
    ]
    
    for ruta in rutas:
        print(f"\n📂 {ruta}")
        try:
            resource = api.get_resource(ruta)
            # Intentar print para ver métodos disponibles
            result = resource.get()
            print(f"   ✅ GET funciona - {len(result)} elementos")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")


def main():
    print("\n" + "🚀 TEST DE MIKROTIK USER MANAGER ".center(60, "=") + "\n")
    
    connection, api = conectar()
    if not api:
        return
    
    try:
        # 1. Listar perfiles disponibles
        perfiles = listar_perfiles(api)
        
        # 2. Listar usuarios
        usuarios = listar_usuarios(api, limit=5)
        
        # 3. Listar asignaciones
        listar_user_profiles(api)
        
        # 4. Ver comandos disponibles
        ver_comandos_disponibles(api)
        
        # 5. Probar asignación (interactivo)
        print("\n" + "="*60)
        print("🧪 PRUEBA DE ASIGNACIÓN")
        print("="*60)
        
        if usuarios and perfiles:
            print("\nUsuarios disponibles:")
            for u in usuarios[:5]:
                print(f"  - {u.get('username') or u.get('name')}")
            
            print("\nPerfiles disponibles:")
            for p in perfiles[:5]:
                print(f"  - {p.get('name')}")
            
            respuesta = input("\n¿Quieres probar asignar un perfil? (s/n): ").strip().lower()
            if respuesta == 's':
                usuario_test = input("Nombre de usuario a modificar: ").strip()
                perfil_test = input("Nombre del perfil a asignar: ").strip()
                
                if usuario_test and perfil_test:
                    probar_asignar_perfil(api, usuario_test, perfil_test)
        
    finally:
        connection.disconnect()
        print("\n✅ Conexión cerrada")


if __name__ == "__main__":
    main()
