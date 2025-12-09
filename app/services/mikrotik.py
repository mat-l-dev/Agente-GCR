"""
Servicio de MikroTik para gestión de usuarios ISP Hotspot.

FUNCIONES PRINCIPALES:
  1. obtener_planes_disponibles() - Lee los planes desde Userman
  2. buscar_usuario_existente(usuario) - Busca si existe el usuario
  3. crear_usuario_userman(usuario, password, nombre, plan) - Crea nuevo usuario
  4. actualizar_usuario_plan(usuario, nuevo_plan) - Cambia plan del usuario
"""

try:
    import routeros_api
except ImportError:
    print("⚠️ Advertencia: routeros_api no está instalado.")
    routeros_api = None

import random
import string
import socket
from typing import Tuple, Optional, Dict, List
from app.core.config import settings


def generar_credenciales() -> Tuple[str, str]:
    """Genera usuario y contraseña aleatorios de 6 caracteres"""
    letras = string.ascii_lowercase + string.digits
    usuario = ''.join(random.choice(letras) for _ in range(6))
    password = ''.join(random.choice(letras) for _ in range(6))
    return usuario, password


def conectar_mikrotik(timeout_secs: int = 10):
    """
    Conecta a MikroTik y retorna (conexión, api).
    
    Returns:
        (conexión, api) o (None, None) si falla
    """
    if not routeros_api:
        print("⚠️ routeros_api no disponible")
        return None, None
    
    try:
        # Verificar conectividad antes de intentar
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_secs)
        result = sock.connect_ex((settings.MIKROTIK_HOST, settings.MIKROTIK_PORT))
        sock.close()
        
        if result != 0:
            print(f"❌ MikroTik {settings.MIKROTIK_HOST}:{settings.MIKROTIK_PORT} no accesible")
            return None, None
        
        # Conectar
        connection = routeros_api.RouterOsApiPool(
            host=settings.MIKROTIK_HOST,
            username=settings.MIKROTIK_USER,
            password=settings.MIKROTIK_PASS,
            port=settings.MIKROTIK_PORT,
            plaintext_login=True
        )
        
        api = connection.get_api()
        return connection, api
        
    except Exception as e:
        print(f"❌ Error conectando a MikroTik: {e}")
        return None, None


def obtener_planes_disponibles() -> List[Dict]:
    """
    Obtiene la lista de planes (profiles) disponibles en Userman.
    
    Returns:
        Lista de dicts con:
          - nombre: Nombre del plan (ej: "1Dia", "3Dias")
          - precio: Precio del plan
          - validez: Duración (ej: "1d 00:00:00")
          - velocidad: Rate limit
          - usuarios_compartidos: Número de usuarios simultáneos
    """
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        print("⚠️ No se puede conectar a MikroTik para obtener planes")
        return []
    
    try:
        # Obtener perfiles de Userman
        profiles = api.get_resource('/tool/user-manager/profile').get()
        connection.disconnect()
        
        planes = []
        for profile in profiles:
            planes.append({
                "nombre": profile.get('name'),
                "precio": profile.get('price'),
                "validez": profile.get('validity'),
                "velocidad": profile.get('rate-limit'),
                "usuarios_compartidos": profile.get('shared-users'),
            })
        
        print(f"✅ Planes obtenidos: {len(planes)} disponibles")
        for plan in planes:
            print(f"   - {plan['nombre']}: {plan['validez']} | ${plan['precio']}")
        
        return planes
        
    except Exception as e:
        print(f"❌ Error obteniendo planes: {e}")
        try:
            connection.disconnect()
        except:
            pass
        return []


def buscar_usuario_existente(usuario: str) -> Optional[Dict]:
    """
    Busca un usuario existente en Userman.
    
    Args:
        usuario: Nombre de usuario a buscar
    
    Returns:
        Dict con datos del usuario o None si no existe:
          - nombre: nombre del usuario
          - disabled: si está desactivado
          - comment: comentario/info del usuario
    """
    print(f"🔍 Buscando usuario '{usuario}' en MikroTik...")
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        print(f"❌ No se pudo conectar a MikroTik para buscar usuario")
        return None
    
    try:
        users = api.get_resource('/tool/user-manager/user').get()
        
        for user in users:
            # El campo correcto en Userman es 'username'
            username = user.get('username')
            
            if username == usuario:
                print(f"✅ Usuario '{usuario}' encontrado en MikroTik")
                connection.disconnect()
                return {
                    "nombre": user.get('username'),
                    "disabled": user.get('disabled'),
                    "customer": user.get('customer'),
                }
        
        print(f"❌ Usuario '{usuario}' no encontrado en MikroTik")
        connection.disconnect()
        return None
        
    except Exception as e:
        print(f"❌ Error buscando usuario: {e}")
        import traceback
        traceback.print_exc()
        try:
            connection.disconnect()
        except:
            pass
        return None


def crear_usuario_userman(
    usuario: str,
    password: str,
    nombre_completo: str,
    plan: str = None
) -> Tuple[bool, str]:
    """
    Crea un usuario en Userman.
    
    Args:
        usuario: Nombre de usuario (ej: ricky3)
        password: Contraseña
        nombre_completo: Nombre del cliente
        plan: Nombre del plan en Userman (ej: "3Dias"). Si es None, el usuario 
              se crea sin plan (debe configurarse después)
    
    Returns:
        (éxito, mensaje)
    """
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        return False, "No se puede conectar a MikroTik"
    
    try:
        print(f"📝 Creando usuario '{usuario}' en Userman...")
        
        # Crear usuario en /tool/user-manager/user
        api.get_resource('/tool/user-manager/user').add(
            name=usuario,
            password=password,
            disabled='no',
            comment=f"Bot: {nombre_completo}"
        )
        
        print(f"✅ Usuario {usuario} creado")
        
        # Si se especifica plan, asignarlo
        if plan:
            try:
                print(f"   Asignando plan '{plan}'...")
                api.get_resource('/tool/user-manager/user').set(
                    numbers=usuario,
                    profile=plan
                )
                print(f"✅ Plan {plan} asignado")
                mensaje = f"Usuario {usuario} creado con plan {plan}"
            except Exception as e:
                print(f"⚠️  No se pudo asignar plan: {e}")
                mensaje = f"Usuario {usuario} creado (plan pendiente)"
        else:
            mensaje = f"Usuario {usuario} creado (sin plan)"
        
        connection.disconnect()
        return True, mensaje
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        try:
            connection.disconnect()
        except:
            pass
        return False, f"Error: {e}"


def actualizar_usuario_plan(
    usuario: str,
    nuevo_plan: str
) -> Tuple[bool, str]:
    """
    Actualiza el plan de un usuario existente en User Manager (RouterOS 6).
    Usa el comando 'create-and-activate-profile' con los parámetros correctos.
    
    Args:
        usuario: Nombre del usuario
        nuevo_plan: Nombre del nuevo plan/perfil
    
    Returns:
        (éxito, mensaje)
    """
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        return False, "No se puede conectar a MikroTik"
    
    try:
        print(f"🔄 Actualizando usuario '{usuario}' al plan '{nuevo_plan}'...")
        
        # Buscar el usuario para obtener su ID y customer
        users = api.get_resource('/tool/user-manager/user').get()
        usuario_data = None
        
        for user in users:
            if user.get('username') == usuario or user.get('name') == usuario:
                usuario_data = user
                print(f"✅ Usuario encontrado: {user.get('username')}")
                break
        
        if not usuario_data:
            print(f"❌ Usuario '{usuario}' no encontrado en Userman")
            connection.disconnect()
            return False, f"Usuario {usuario} no existe"
        
        # Obtener datos necesarios
        usuario_id = usuario_data.get('id') or usuario_data.get('.id')
        customer = usuario_data.get('customer', 'admin')
        
        print(f"📌 ID: {usuario_id}, Customer: {customer}")
        
        # Verificar que el perfil existe
        profiles = api.get_resource('/tool/user-manager/profile').get()
        profile_exists = False
        
        for profile in profiles:
            if profile.get('name') == nuevo_plan:
                profile_exists = True
                print(f"✅ Perfil '{nuevo_plan}' encontrado")
                break
        
        if not profile_exists:
            print(f"❌ Perfil '{nuevo_plan}' no existe en Userman")
            # Listar perfiles disponibles para ayudar
            nombres = [p.get('name') for p in profiles]
            print(f"   Perfiles disponibles: {nombres}")
            connection.disconnect()
            return False, f"Plan {nuevo_plan} no existe"
        
        # En RouterOS 6 User Manager, el comando correcto es:
        # /tool/user-manager/user/create-and-activate-profile
        # Requiere: .id (ID del usuario), profile (nombre del perfil), customer
        user_resource = api.get_resource('/tool/user-manager/user')
        
        try:
            result = user_resource.call('create-and-activate-profile', {
                '.id': usuario_id,
                'profile': nuevo_plan,
                'customer': customer
            })
            print(f"✅ Resultado: {result}")
            print(f"✅ Usuario '{usuario}' actualizado al plan '{nuevo_plan}'")
            connection.disconnect()
            return True, f"Plan {nuevo_plan} activado para {usuario}"
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error en create-and-activate-profile: {e}")
            
            # Si falla, intentar habilitar el usuario
            if 'disabled' in usuario_data and usuario_data.get('disabled') == 'true':
                try:
                    print("🔄 Intentando habilitar usuario primero...")
                    user_resource.set(id=usuario_id, disabled='no')
                    
                    # Reintentar asignación
                    result = user_resource.call('create-and-activate-profile', {
                        '.id': usuario_id,
                        'profile': nuevo_plan,
                        'customer': customer
                    })
                    print(f"✅ Usuario habilitado y plan asignado")
                    connection.disconnect()
                    return True, f"Plan {nuevo_plan} activado para {usuario}"
                except Exception as e2:
                    print(f"❌ Error habilitando: {e2}")
            
            connection.disconnect()
            return False, f"Error: {error_msg}"
        
    except Exception as e:
        print(f"❌ Error actualizando usuario: {e}")
        try:
            connection.disconnect()
        except:
            pass
        return False, f"Error: {e}"


def habilitar_usuario(usuario: str) -> Tuple[bool, str]:
    """
    Habilita un usuario deshabilitado en User Manager.
    
    Args:
        usuario: Nombre del usuario
    
    Returns:
        (éxito, mensaje)
    """
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        return False, "No se puede conectar a MikroTik"
    
    try:
        print(f"🔄 Habilitando usuario '{usuario}'...")
        
        users = api.get_resource('/tool/user-manager/user').get()
        usuario_data = None
        
        for user in users:
            if user.get('username') == usuario or user.get('name') == usuario:
                usuario_data = user
                break
        
        if not usuario_data:
            connection.disconnect()
            return False, f"Usuario {usuario} no existe"
        
        usuario_id = usuario_data.get('id') or usuario_data.get('.id')
        user_resource = api.get_resource('/tool/user-manager/user')
        user_resource.set(id=usuario_id, disabled='no')
        
        print(f"✅ Usuario '{usuario}' habilitado")
        connection.disconnect()
        return True, f"Usuario {usuario} habilitado"
        
    except Exception as e:
        print(f"❌ Error habilitando usuario: {e}")
        try:
            connection.disconnect()
        except:
            pass
        return False, f"Error: {e}"


def eliminar_perfiles_usuario(usuario: str) -> Tuple[bool, str]:
    """
    Elimina TODOS los perfiles asignados a un usuario en User Manager (RouterOS 6).
    
    En RouterOS 6 User Manager, los perfiles activos están en:
    /tool/user-manager/user -> expandir "All profiles" del usuario
    
    Args:
        usuario: Nombre del usuario
    
    Returns:
        (éxito, mensaje con cantidad eliminados)
    """
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        return False, "No se puede conectar a MikroTik"
    
    try:
        print(f"🗑️ Eliminando perfiles de usuario '{usuario}'...")
        
        # En RouterOS 6, primero buscamos el usuario
        users = api.get_resource('/tool/user-manager/user').get()
        usuario_data = None
        
        for user in users:
            if user.get('username') == usuario or user.get('name') == usuario:
                usuario_data = user
                break
        
        if not usuario_data:
            connection.disconnect()
            return False, f"Usuario {usuario} no encontrado"
        
        usuario_id = usuario_data.get('id') or usuario_data.get('.id')
        
        # Usar el comando remove-user-from-profile para cada perfil activo
        # Primero obtenemos los perfiles del sistema
        profiles = api.get_resource('/tool/user-manager/profile').get()
        profile_names = [p.get('name') for p in profiles]
        
        print(f"   Perfiles del sistema: {profile_names}")
        
        # Intentar remover el usuario de todos los perfiles conocidos
        user_resource = api.get_resource('/tool/user-manager/user')
        eliminados = 0
        
        # En RouterOS 6 Userman, usamos "remove-profile-from-user" 
        for profile_name in profile_names:
            try:
                # Intentar remover este perfil del usuario
                result = user_resource.call('remove-profile-from-user', {
                    '.id': usuario_id,
                    'profile': profile_name
                })
                print(f"   ✅ Removido perfil '{profile_name}' de usuario")
                eliminados += 1
            except Exception as e:
                # Si no tiene ese perfil, ignorar
                error_str = str(e).lower()
                if 'no such' in error_str or 'not found' in error_str or 'does not have' in error_str:
                    pass  # Normal, el usuario no tiene ese perfil
                else:
                    print(f"   ⚠️ Error removiendo '{profile_name}': {e}")
        
        connection.disconnect()
        
        if eliminados > 0:
            return True, f"{eliminados} perfiles eliminados"
        else:
            return True, "Sin perfiles previos"
        
    except Exception as e:
        print(f"❌ Error eliminando perfiles: {e}")
        try:
            connection.disconnect()
        except:
            pass
        return False, f"Error: {e}"


def reemplazar_plan_usuario(usuario: str, nuevo_plan: str) -> Tuple[bool, str]:
    """
    REEMPLAZA el plan de un usuario: elimina perfiles anteriores y asigna el nuevo.
    
    Este es el flujo correcto para cuando el admin aprueba un pago:
    1. Eliminar el perfil temporal (1 día de prueba)
    2. Asignar el plan completo que el cliente pagó
    
    Args:
        usuario: Nombre del usuario
        nuevo_plan: Nombre del nuevo plan (ej: "1User5Dia")
    
    Returns:
        (éxito, mensaje)
    """
    print(f"🔄 REEMPLAZANDO plan de '{usuario}' a '{nuevo_plan}'...")
    
    # Paso 1: Eliminar perfiles existentes
    exito_eliminar, msg_eliminar = eliminar_perfiles_usuario(usuario)
    if not exito_eliminar:
        print(f"⚠️ Error al eliminar perfiles previos: {msg_eliminar}")
        # Continuar de todas formas, puede que no tenga perfiles
    else:
        print(f"   {msg_eliminar}")
    
    # Paso 2: Asignar el nuevo plan
    exito_asignar, msg_asignar = actualizar_usuario_plan(usuario, nuevo_plan)
    
    if exito_asignar:
        print(f"✅ Plan reemplazado exitosamente: {nuevo_plan}")
        return True, f"Plan {nuevo_plan} activado (reemplazó anterior)"
    else:
        print(f"❌ Error al asignar nuevo plan: {msg_asignar}")
        return False, msg_asignar


def obtener_info_usuario(usuario: str) -> Optional[Dict]:
    """
    Obtiene información detallada de un usuario en User Manager.
    Incluye perfil activo, tiempo restante, etc.
    
    Args:
        usuario: Nombre del usuario
    
    Returns:
        Dict con información del usuario o None
    """
    connection, api = conectar_mikrotik()
    
    if not connection or not api:
        return None
    
    try:
        print(f"🔍 Obteniendo info de usuario '{usuario}'...")
        
        users = api.get_resource('/tool/user-manager/user').get()
        usuario_data = None
        
        for user in users:
            if user.get('username') == usuario or user.get('name') == usuario:
                usuario_data = user
                break
        
        if not usuario_data:
            connection.disconnect()
            return None
        
        # Obtener perfiles activos del usuario
        try:
            user_profiles = api.get_resource('/tool/user-manager/user-profile').get()
            perfiles_usuario = [p for p in user_profiles if p.get('user') == usuario]
            usuario_data['perfiles_activos'] = perfiles_usuario
        except:
            usuario_data['perfiles_activos'] = []
        
        connection.disconnect()
        return usuario_data
        
    except Exception as e:
        print(f"❌ Error obteniendo info: {e}")
        try:
            connection.disconnect()
        except:
            pass
        return None
