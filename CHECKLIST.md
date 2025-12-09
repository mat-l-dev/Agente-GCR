# 📋 CHECKLIST - Qué hacer ahora

## ✅ COMPLETADO (por el Copilot)

- ✅ `mikrotik.py` reescrito - Funciones dinámicas para conectar con MikroTik
- ✅ `webhook_wa.py` reescrito - Flujo de estados cliente
- ✅ `planes.py` eliminado - Ya no necesario
- ✅ Documentación actualizada
- ✅ Test script creado

---

## 🔄 PASOS QUE DEBES HACER (en orden)

### 1️⃣ CONECTAR MIKROTIK (Crítico)
**Tiempo estimado**: 30 minutos  
**Documentación**: `docs/GUIA_MIKROTIK_SETUP.md`

```bash
# Lo que necesitas hacer:
- [ ] Acceder a MikroTik con admin
- [ ] Activar API SSL (puerto 8443)
- [ ] Crear usuario "api_bot" para el bot
- [ ] Configurar firewall (whitelist VPS IP)
- [ ] Obtener IP pública de MikroTik
```

**Variables .env a actualizar**:
```bash
MIKROTIK_PRIMARY_HOST=190.xxx.xxx.x        # IP pública
MIKROTIK_PRIMARY_PORT=8443
MIKROTIK_PRIMARY_USER=api_bot
MIKROTIK_PRIMARY_PASS=tu_contraseña
```

---

### 2️⃣ CREAR PLANES EN USERMAN (Crítico)
**Tiempo estimado**: 15 minutos  
**Documentación**: `docs/PLANES_USERMAN.md`

```bash
# Lo que necesitas hacer:
- [ ] Acceder a MikroTik WinBox
- [ ] Ir a: Tools → User Manager → Profiles
- [ ] Crear 4 perfiles (EXACTAMENTE estos nombres):
      - [ ] 1Dia      - Duración: 1 día   - Precio: $1
      - [ ] 3Dias     - Duración: 3 días  - Precio: $3
      - [ ] 1Semana   - Duración: 7 días  - Precio: $7
      - [ ] 1Mes      - Duración: 30 días - Precio: $30
```

⚠️ **IMPORTANTE**: Los nombres deben ser EXACTOS:
- ✗ "1 Dia" (con espacio)
- ✗ "un_dia" (con guión)
- ✓ "1Dia" (así)

---

### 3️⃣ INSTALAR DEPENDENCIAS (si no lo hiciste)
**Tiempo estimado**: 5 minutos

```bash
cd bot_isp
pip install -r requirements.txt
```

**Verificar que incluye**:
- [ ] `routeros-api` - Para conectar con MikroTik
- [ ] `fastapi` - Backend
- [ ] `python-dotenv` - Variables de entorno

---

### 4️⃣ PROBAR INTEGRACIÓN
**Tiempo estimado**: 10 minutos

```bash
# Ejecutar el script de prueba:
python test_mikrotik_integration.py
```

**Esperar ver**:
```
✅ Planes obtenidos: 4 disponibles
   - 1Dia: 1d | $1
   - 3Dias: 3d | $3
   - 1Semana: 7d | $7
   - 1Mes: 30d | $30
```

Si ves esto → ✅ **MikroTik está conectado correctamente**

---

### 5️⃣ CONFIGURAR VARIABELES DE ENTORNO
**Tiempo estimado**: 5 minutos

```bash
# Copiar template
cp .env.example .env

# Editar .env y llenar:
MIKROTIK_PRIMARY_HOST=190.xxx.xxx.x
MIKROTIK_PRIMARY_PORT=8443
MIKROTIK_PRIMARY_USER=api_bot
MIKROTIK_PRIMARY_PASS=contraseña

OPENAI_API_KEY=sk-...        # Token de OpenAI
TWILIO_ACCOUNT_SID=ACxxxxx   # De Twilio
TWILIO_AUTH_TOKEN=xxxxx      # De Twilio
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=xxxxx
```

---

### 6️⃣ PROBAR FLUJO COMPLETO (Recomendado)
**Tiempo estimado**: 30 minutos

```bash
# Iniciar bot
python main.py

# En otra terminal, simular un cliente:
# (O usar Postman/curl)

# 1. Cliente envía mensaje de texto
POST /webhook
From: whatsapp:+51999999999
Body: Hola, quiero internet

# 2. Respuesta esperada
"👋 Hola! ¿Eres usuario nuevo o ya tienes cuenta?"

# 3. Cliente responde
Body: Soy nuevo

# 4. Continuar el flujo...
```

---

### 7️⃣ (OPCIONAL) PERSISTENCIA DE ESTADO
**Tiempo estimado**: 2 horas  
**Prioridad**: MEDIA (el bot funciona sin esto, pero pierde estados si se reinicia)

**TODO**:
- [ ] Guardar CLIENTE_ESTADO en Supabase
- [ ] Cargar estado al iniciar
- [ ] Usar tabla `cliente_estados` con campos:
  - `numero` (PK)
  - `estado` (texto)
  - `es_nuevo` (bool)
  - `nombre` (texto)
  - `usuario` (texto)
  - `zona` (texto)
  - `plan_solicitado` (texto)
  - `created_at`
  - `updated_at`

**Código aproximado**:
```python
# En webhook_wa.py
async def obtener_estado_cliente(numero: str):
    # SELECT FROM supabase donde numero = numero
    # Si no existe, crear nuevo
    # Retornar dict con estado
```

---

### 8️⃣ (OPCIONAL) ADMIN APPROVAL VIA TELEGRAM
**Tiempo estimado**: 1 hora  
**Prioridad**: MEDIA (el pago se registra, pero admin no ve alertas sin esto)

**TODO**:
- [ ] Completar handler en `telegram.py`
- [ ] Crear webhook para `/approve_` commands
- [ ] Integrar con `actualizar_usuario_plan()`
- [ ] Enviar confirmación al cliente

**Código base**:
```python
# app/services/telegram.py
def handler_telegram_approval(comando: str):
    # /approve_51999999999_3dias
    # Extraer: numero, plan
    # actualizar_usuario_plan(usuario, plan)
    # enviar_mensaje_whatsapp(numero, "¡Activado!")
```

---

### 9️⃣ (OPCIONAL) MULTIPLES ZONAS
**Tiempo estimado**: 1 hora  
**Prioridad**: BAJA (por ahora solo 1 zona configurada)

Si necesitas 5 zonas, agregar:
- [ ] `MIKROTIK_ZONE_2_HOST`, etc en `config.py`
- [ ] Router lógico en `webhook_wa.py` para detectar zona
- [ ] Crear usuario en zona correspondiente

**Código base**:
```python
# En procesar_texto(), al estado "esperando_zona":
zona = texto.lower()

if "centro" in zona:
    host = settings.MIKROTIK_PRIMARY_HOST
    user_count_in_zone = 1
elif "goza" in zona:
    host = settings.MIKROTIK_ZONE_2_HOST
    user_count_in_zone = 2
# etc...
```

---

### 🔟 (OPCIONAL) DEPLOYAR A VPS
**Tiempo estimado**: 1 hora  
**Prioridad**: BAJA (test local primero)

```bash
# Ver documentación (cuando esté lista)
# docs/DEPLOY_VPS.md

# Básicamente:
# 1. SSH a VPS Ubuntu 16GB
# 2. Clone repo
# 3. pip install -r requirements.txt
# 4. Configure .env
# 5. gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

---

## 📊 ORDEN RECOMENDADO

```
1. MIKROTIK (CRÍTICO)
   └─→ 2. CREAR PLANES (CRÍTICO)
       └─→ 3. INSTALAR DEPS
           └─→ 4. PROBAR INTEGRACIÓN
               └─→ 5. CONFIGURAR .env
                   └─→ 6. PROBAR FLUJO COMPLETO
                       └─→ 7. PERSISTENCIA (OPCIONAL)
                           └─→ 8. TELEGRAM APPROVAL (OPCIONAL)
                               └─→ 9. MÚLTIPLES ZONAS (OPCIONAL)
                                   └─→ 10. DEPLOY VPS (OPCIONAL)
```

---

## ✅ CHECKLIST DE PRUEBA FINAL

Antes de decir "¡listo!":

```bash
# 1. Test script pasa
- [ ] python test_mikrotik_integration.py → ✅

# 2. Bot inicia sin errores
- [ ] python main.py → "Iniciado en 0.0.0.0:8000"

# 3. Webhook responde
- [ ] curl http://localhost:8000/webhook → {"status": "success"}

# 4. Cliente nuevo flujo completo
- [ ] Cliente dice "Hola"
- [ ] Bot pregunta nuevo/existente
- [ ] Cliente dice "nuevo"
- [ ] Bot pide nombre
- [ ] Cliente dice nombre
- [ ] Bot pide usuario
- [ ] Cliente dice usuario
- [ ] Bot pide zona
- [ ] Cliente dice zona
- [ ] Bot pide cuántos días
- [ ] Cliente dice "3 dias"
- [ ] Bot crea usuario en MikroTik
- [ ] Bot pide comprobante de pago
- [ ] (Usuario intenta conectarse con credenciales)

# 5. Cliente existente flujo completo
- [ ] Cliente dice "Tengo cuenta"
- [ ] Bot pide usuario
- [ ] Cliente dice usuario
- [ ] Bot busca y encuentra en MikroTik
- [ ] Bot pide comprobante de pago
```

---

## 🆘 TROUBLESHOOTING

### Problema: "MikroTik no accesible"
```
Soluciones:
1. Verificar IP en .env (MIKROTIK_PRIMARY_HOST)
2. Verificar puerto 8443 activo en MikroTik
3. Verificar firewall permite VPS IP
4. Verificar usuario "api_bot" existe
5. Probar: telnet 190.xxx.xxx.x 8443
```

### Problema: "No hay planes"
```
Soluciones:
1. Crear planes en WinBox (Tools → User Manager → Profiles)
2. Verificar nombres EXACTOS: 1Dia, 3Dias, 1Semana, 1Mes
3. Re-ejecutar test script
```

### Problema: "Usuario creado pero sin plan"
```
Soluciones:
1. Plan especificado no existe en MikroTik
2. Crear el plan en WinBox
3. Ejecutar de nuevo
```

### Problema: "Bot no responde a mensajes"
```
Soluciones:
1. Verificar webhook está registrado en Twilio
2. Verificar Twilio URL: https://tu-vps.com/webhook
3. Revisar logs del bot
4. Verificar Twilio credentials en .env
```

---

## 📞 RESUMEN

**Estado actual**: ✅ Código listo, arquitectura dinámica implementada

**Qué hace falta**: Configurar MikroTik (infraestructura)

**Próximo paso**: Ejecuta `python test_mikrotik_integration.py` después de configurar MikroTik

**Tiempo estimado para funcionar**: 1-2 horas (si tienes MikroTik accesible)

---

## 📚 DOCUMENTACIÓN DISPONIBLE

- `docs/ARQUITECTURA_DINAMICA.md` - Explicación de cambios
- `docs/FLUJO_COMPLETO_EJEMPLO.md` - Flujo paso a paso
- `docs/GUIA_MIKROTIK_SETUP.md` - Cómo configurar MikroTik
- `docs/PLANES_USERMAN.md` - Cómo crear planes
- `docs/README.md` - Guía general
- `docs/SEGURIDAD.md` - RLS y seguridad BD
