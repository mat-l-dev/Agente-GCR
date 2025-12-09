# 🔧 GUÍA DE CONFIGURACIÓN MIKROTIK PARA BOT ISP

## 📋 Información General

**Objetivo:** Conectar tu VPS Ubuntu con 1 MikroTik usando API-SSL segura (puerto 8443)

**Arquitectura:**
```
VPS Ubuntu (Python Bot)
    ↓ Internet (SSL puerto 8443)
MikroTik (Userman + Radius)
    ↓ Red Local
Clientes (Hotspot)
```

---

## 🎯 PARTE 1: Preparar el MikroTik (WinBox)

### Paso 1: Habilitar API-SSL

1. **Abrir WinBox** y conectarte a tu MikroTik

2. **Ir a `IP > Services`**

3. **Buscar `api-ssl`** en la lista

4. **Configurar:**
   ```
   Enabled: ✅ (check)
   Port: 8443 (cambiar de 443 a 8443)
   Available From: [IP_DE_TU_VPS]
   Certificate: none (o tu certificado SSL)
   ```

5. **Click `OK`**

**¿Por qué puerto 8443 y no 443?**
- Los bots maliciosos escanean puerto 443 automáticamente
- Puerto 8443 es menos visible para ataques
- Es más seguro y raro

---

### Paso 2: Crear Usuario API (NO usar admin)

1. **Ir a `System > Users`**

2. **Click `Add New` (+)**

3. **Configurar:**
   ```
   Name: api_bot
   Group: full (o crea grupo "api" con permisos limitados)
   Password: [contraseña fuerte aleatoria, ej: Kj8#mP2$vN9@]
   
   Allowed Address: [IP_DE_TU_VPS]/32
   ```

4. **Click `OK`**

**Importante:** Guarda estas credenciales para tu `.env`

---

### Paso 3: Configurar Firewall (Whitelist IP del VPS)

#### 3.1. Agregar regla de ACCEPT para tu VPS

1. **Ir a `IP > Firewall > Filter Rules`**

2. **Tab `Input`**

3. **Click `Add New` (+)**

4. **Tab `General`:**
   ```
   Chain: input
   Protocol: tcp
   Dst. Port: 8443
   Src. Address: [IP_DE_TU_VPS]
   In. Interface: ether1 (tu WAN/Internet)
   ```

5. **Tab `Action`:**
   ```
   Action: accept
   ```

6. **Click `OK`**

7. **MOVER ESTA REGLA ARRIBA** (drag & drop) para que sea la primera

#### 3.2. Agregar regla de DROP para el resto

1. **Click `Add New` (+)** de nuevo

2. **Tab `General`:**
   ```
   Chain: input
   Protocol: tcp
   Dst. Port: 8443
   ```

3. **Tab `Action`:**
   ```
   Action: drop
   Comment: Bloquear API de todos excepto VPS
   ```

4. **Click `OK`**

**Resultado:** Solo tu VPS puede acceder al puerto 8443, el resto es bloqueado.

---

### Paso 4: Verificar que Userman está activo

1. **Ir a `User Manager`** (en el menú lateral)

2. **Si no aparece:** Ir a `System > Packages` y habilitar `user-manager`

3. **Verificar que `Radius` esté habilitado:**
   ```
   User Manager > Routers
   Debe aparecer tu router local con estado "Online"
   ```

4. **Si no está:** Ir a `Radius` y agregar tu MikroTik como cliente Radius

---

### Paso 5: Obtener IP Pública del MikroTik

#### Opción A: IP Pública Estática (Mejor)

1. **Ir a `IP > Addresses`**

2. **Buscar tu interfaz WAN (ether1 o similar)**

3. **Anotar la IP pública** (ej: 190.123.45.67)

4. **Esta IP va en tu `.env`:**
   ```
   MIKROTIK_PRIMARY_HOST=190.123.45.67
   ```

#### Opción B: DDNS (Si tu IP cambia)

1. **Ir a `IP > Cloud`**

2. **Habilitar `DDNS Enabled: yes`**

3. **Obtener tu dominio:**
   ```
   DNS Name: xxxxx.sn.mynetname.net
   ```

4. **Esta URL va en tu `.env`:**
   ```
   MIKROTIK_PRIMARY_HOST=xxxxx.sn.mynetname.net
   ```

---

## 🖥️ PARTE 2: Configurar el VPS Ubuntu

### Paso 1: Instalar Dependencias Python

```bash
# Conectar por SSH a tu VPS
ssh usuario@tu-vps-ip

# Ir a tu proyecto
cd /ruta/a/bot_isp

# Instalar paquete de MikroTik
pip install RouterOS-api

# Verificar instalación
python -c "import routeros_api; print('✅ RouterOS-api instalado')"
```

---

### Paso 2: Configurar Variables de Entorno

```bash
# Editar .env
nano .env
```

**Agregar:**
```dotenv
# MikroTik
MIKROTIK_HOST=190.123.45.67
MIKROTIK_PORT=8443
MIKROTIK_USER=api_bot
MIKROTIK_PASS=Kj8#mP2$vN9@

# Configuración de planes
BONO_DIAS_NUEVOS=3
PRECIO_POR_DIA=1.0
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Paso 3: Probar Conexión desde VPS

Crear archivo de prueba:

```bash
nano test_mikrotik.py
```

**Contenido:**
```python
#!/usr/bin/env python3
import routeros_api

# Configuración (usa tus valores reales)
HOST = "190.123.45.67"
PORT = 8443
USER = "api_bot"
PASS = "tu_contraseña"

try:
    print(f"🔍 Conectando a {HOST}:{PORT}...")
    
    connection = routeros_api.RouterOsApiPool(
        host=HOST,
        username=USER,
        password=PASS,
        port=PORT,
        plaintext_login=True,
        timeout=10
    )
    
    api = connection.get_api()
    
    # Obtener identidad del router
    identity = api.get_resource('/system/identity').get()
    print(f"✅ Conectado exitosamente!")
    print(f"Router: {identity[0]['name']}")
    
    # Listar usuarios de Userman
    print("\n📋 Usuarios en Userman:")
    users = api.get_resource('/tool/user-manager/user').get()
    print(f"Total: {len(users)} usuarios")
    
    for user in users[:5]:  # Mostrar primeros 5
        print(f"  - {user.get('name')}")
    
    connection.disconnect()
    print("\n✅ Prueba exitosa!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nVerifica:")
    print("1. Firewall del MikroTik permite tu IP")
    print("2. Puerto 8443 está abierto")
    print("3. Credenciales correctas")
```

**Ejecutar:**
```bash
python test_mikrotik.py
```

**Resultado esperado:**
```
🔍 Conectando a 190.123.45.67:8443...
✅ Conectado exitosamente!
Router: MikroTik-ZonaCentro

📋 Usuarios en Userman:
Total: 0 usuarios

✅ Prueba exitosa!
```

---

## 🔒 PARTE 3: Seguridad Adicional (Opcional pero Recomendado)

### Opción 1: Cambiar Puerto SSH del VPS

```bash
# Editar configuración SSH
sudo nano /etc/ssh/sshd_config

# Cambiar línea:
Port 22  →  Port 2222

# Reiniciar SSH
sudo systemctl restart sshd
```

**Ahora conectas con:**
```bash
ssh -p 2222 usuario@tu-vps-ip
```

---

### Opción 2: Instalar Fail2Ban (Protección contra fuerza bruta)

```bash
# Instalar Fail2Ban
sudo apt update
sudo apt install fail2ban -y

# Verificar estado
sudo systemctl status fail2ban
```

---

### Opción 3: Firewall UFW en VPS

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH (puerto 2222 si lo cambiaste)
sudo ufw allow 2222/tcp

# Permitir puerto del bot (8000)
sudo ufw allow 8000/tcp

# Ver reglas
sudo ufw status
```

---

## 📊 PARTE 4: Verificación Final

### Checklist de Configuración

**En MikroTik:**
- [x] API-SSL habilitado en puerto 8443
- [x] Usuario `api_bot` creado
- [x] Firewall permite solo IP del VPS
- [x] Userman activo
- [x] IP pública o DDNS configurado

**En VPS Ubuntu:**
- [x] Python 3.8+ instalado
- [x] `routeros_api` instalado
- [x] `.env` configurado con credenciales correctas
- [x] Test de conexión exitoso

**Seguridad:**
- [x] Puerto 8443 (no 443)
- [x] Usuario API (no admin)
- [x] Firewall whitelist activo
- [x] Contraseña fuerte

---

## 🐛 TROUBLESHOOTING

### Error: "Connection timeout"

**Causa:** MikroTik no accesible desde VPS

**Solución:**
```bash
# Desde el VPS, probar conexión:
telnet 190.123.45.67 8443

# Si dice "Connection refused": Firewall bloqueando
# Si dice "Connection timeout": IP o puerto incorrectos
```

**Verificar firewall del MikroTik:**
```
IP > Firewall > Filter Rules
Asegúrate de que la regla ACCEPT esté ANTES de DROP
```

---

### Error: "Authentication failed"

**Causa:** Credenciales incorrectas

**Solución:**
1. Verificar usuario en MikroTik: `System > Users`
2. Resetear contraseña del usuario `api_bot`
3. Actualizar `.env` con nueva contraseña

---

### Error: "No route to host"

**Causa:** IP del VPS cambió o firewall bloqueando

**Solución:**
```bash
# Obtener IP pública del VPS:
curl ifconfig.me

# Actualizar regla de firewall en MikroTik con nueva IP
```

---

### Error: "SSL certificate verify failed"

**Causa:** Certificado SSL del MikroTik no válido

**Solución:**
```python
# En test_mikrotik.py, usar:
plaintext_login=True  # ✅ Ya está configurado así
```

---

## 📝 COMANDOS ÚTILES

### Ver logs del MikroTik (WinBox)

```
Log > Topics: system,!debug
```

Busca eventos de API o autenticación.

---

### Ver conexiones activas al API (Terminal WinBox)

```
/ip service print
/log print where topics~"system"
```

---

### Backup de configuración MikroTik

```
/system backup save name=backup-antes-bot
/export file=config-backup
```

---

## 🎉 ¡LISTO!

Ahora tu MikroTik está configurado y listo para recibir conexiones del bot.

**Próximos pasos:**
1. ✅ Iniciar el bot en VPS: `python main.py`
2. ✅ Enviar mensaje de prueba por WhatsApp
3. ✅ Verificar que se cree usuario en Userman

**Estructura final:**
```
Cliente WhatsApp
    ↓
Bot ISP (VPS Ubuntu)
    ↓ API-SSL (puerto 8443)
MikroTik (Userman + Radius)
    ↓
Cliente conectado a internet
```

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs del bot: `tail -f logs/bot.log`
2. Revisa logs de MikroTik: `Log > System`
3. Verifica firewall: `IP > Firewall > Filter Rules`

**Recuerda:** La configuración es para **1 línea/zona** inicialmente. Agregar más zonas es copiar la misma config con diferentes IPs.
