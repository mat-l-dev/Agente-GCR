# 🤖 Bot ISP - Sistema Automatizado de Ventas de Internet

**Bot inteligente para WhatsApp/Telegram que automatiza la venta de internet en MikroTik**

---

## ⚡ CAMBIO IMPORTANTE (Diciembre 2024)

✅ **Ahora el bot lee planes DINÁMICAMENTE desde MikroTik**
- NO hay planes hardcodeados en Python
- Los planes se crean/editan en **MikroTik Userman (WinBox)**
- El bot siempre usa planes actualizados automáticamente

📖 **Lee**: `docs/ARQUITECTURA_DINAMICA.md`

---

## 📂 Estructura del Proyecto

```
bot_isp/
├── 📄 main.py                 ← PUNTO DE ENTRADA (Ejecutar esto)
├── 📄 requirements.txt        ← Dependencias
├── 📄 .env.example            ← Template de .env
├── 📄 .gitignore              ← Archivos a ignorar
│
├── 📁 app/                    ← Código principal
│   ├── core/                  ← Configuración centralizada
│   ├── models/                ← Modelos Pydantic (vacío)
│   ├── routers/               ← Webhooks FastAPI
│   └── services/              ← Lógica de negocio
│
├── 📁 migrations/             ← Scripts SQL de base de datos
│   ├── 001_initial_schema.sql ← Tablas principales (EJECUTAR PRIMERO)
│   ├── 002_storage_buckets.sql
│   ├── README.md
│   └── run_migrations.py
│
├── 📁 tests/                  ← Scripts de prueba
│   ├── test_webhook.py
│   ├── test_telegram_button.py
│   ├── test_telegram_debug.py
│   ├── debug_telegram.py
│   └── verificar_sistema.py
│
└── 📁 docs/                       ← DOCUMENTACIÓN COMPLETA
    ├── README.md                  ← Este archivo
    ├── SEGURIDAD.md               ← Guía de RLS y auditoría ⭐ NUEVO
    ├── SEGURIDAD_PYTHON.md        ← Módulo security.py listo ⭐ NUEVO
    ├── IMPLEMENTACION_SEGURIDAD.md ← Resumen implementación ⭐ NUEVO
    ├── MIGRACIONES_REFERENCIA.md  ← Cheat sheet migraciones ⭐ NUEVO
    ├── ESTRUCTURA.md              ← Mapa del proyecto
    ├── FLUJO_COMPLETO.md          ← Flujo del cliente
    ├── CONTABILIDAD.md            ← Sistema de S/1 por día
    ├── ACTUALIZACION_TARIFAS.md   ← Cambios en schema
    ├── MIGRACION_CHECKLIST.md     ← Cómo migrar BD
    ├── REORGANIZACION_COMPLETADA.md
    └── RESUMEN.md
```

---

## 🚀 Inicio Rápido

### 1️⃣ Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
# Editar .env con tus credenciales
```

### 2️⃣ Ejecutar las Migraciones (BD)
```bash
# En Supabase Dashboard (SQL Editor):
# Ejecutar en este orden:
# 1. migrations/001_initial_schema.sql      ← Tablas principales
# 2. migrations/003_rls_policies.sql        ← Seguridad ⭐ NUEVO
# 3. migrations/005_indexes_optimization.sql ← Performance ⭐ NUEVO
# 4. migrations/006_audit_logging.sql       ← Auditoría ⭐ NUEVO

# Referencia rápida: docs/MIGRACIONES_REFERENCIA.md
```

### 3️⃣ Iniciar el Servidor
```bash
# Opción A: Python directo
python main.py

# Opción B: Con uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4️⃣ Probar
```bash
# Simular mensaje de WhatsApp con imagen
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:%2B51999888777&Body=&NumMedia=1&MediaUrl0=https://via.placeholder.com/500"
```

---

## 💰 Sistema de Tarifas

**Tarifa: S/1.00 por día**

Ejemplos:
- Cliente pide 1 día → **S/1.00**
- Cliente pide 5 días → **S/5.00**
- Cliente pide 7 días → **S/7.00**

**Cálculo automático en BD:**
```
monto = dias_solicitados × tarifa_diaria
5 × 1.00 = S/5.00
```

📖 Leer: `docs/CONTABILIDAD.md`

---

## 📱 Flujo del Cliente

```
1. Cliente: "Activame internet"
   ↓
2. Bot ofrece PRUEBA (1 día gratis)
   ↓
3. Cliente prueba y dice: "Dame 5 días"
   ↓
4. Bot: "Son S/5.00, yapea a +51988776655"
   ↓
5. Cliente yapea y manda captura
   ↓
6. Telegram te avisa: "NUEVA SOLICITUD"
   ↓
7. Tú clickeas: ✅ APROBAR
   ↓
8. Bot crea usuario en MikroTik (5 días)
   ↓
9. Cliente recibe credenciales por WhatsApp
   ↓
10. Cliente disfruta internet 🌐
```

📖 Leer: `docs/FLUJO_COMPLETO.md`

---

## 🗄️ Base de Datos

**Tablas creadas:**
- `configuracion` - Configuración global (tarifa diaria)
- `clientes` - Registro de clientes
- `planes` - Planes disponibles (Basic, Pro, Premium)
- `campamentos` - Zonas de servicio
- `ventas` - Historial de compras
- `pruebas` - Período de prueba (1 día)
- `activaciones` - Historial de activaciones
- `transacciones` - Movimientos de dinero

📖 Leer: `docs/MIGRACION_CHECKLIST.md`

---

## ⚙️ Variables de Entorno (.env)

```bash
# TWILIO (WhatsApp)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=whatsapp:+1234567890

# TELEGRAM
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh
TELEGRAM_ADMIN_ID=123456789

# GOOGLE GEMINI (IA) - ⚠️ DESHABILITADO
# Usar ChatGPT (OpenAI) en su lugar
# GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxx

# OPENAI (ChatGPT)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SUPABASE
SUPABASE_URL=https://xxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJxxxxxxxxxxxxxxxxxxxxxxxxxx

# MIKROTIK
MK_HOST=190.xxx.xxx.xxx
MK_PORT=8799
MK_USER=admin
MK_PASS=password123

# NGROK (desarrollo)
NGROK_URL=https://hygrophytic-pseudoprosperous-arlinda.ngrok-free.dev
```

---

## 🔧 Servicios Integrados

| Servicio | Función | Estado |
|----------|---------|--------|
| **WhatsApp (Twilio)** | Recibir/enviar mensajes | ✅ Activo |
| **Telegram** | Alertas y botones de aprobación | ✅ Activo |
| **OpenAI (ChatGPT)** | Respuestas IA a clientes | ✅ Activo |
| **Supabase** | Base de datos PostgreSQL | ✅ Activo |
| **MikroTik RouterOS** | Crear usuarios hotspot | ✅ Listo |
| **Twilio Webhook** | Recibir fotos de comprobantes | ✅ Activo |

---

## 📊 Comandos Útiles

```bash
# Verificar sistema completo
python tests/verificar_sistema.py

# Simular clic en botón de Telegram
python tests/test_telegram_button.py

# Ver estructura del proyecto
tree /F

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

---

## 🔒 Seguridad

**El proyecto incluye seguridad a nivel de base de datos:**

- ✅ **RLS (Row Level Security)** - Clientes solo ven sus datos
- ✅ **Auditoría automática** - Todos los cambios se registran
- ✅ **Storage RLS** - Imágenes protegidas por política
- ✅ **Índices optimizados** - Queries rápidas y seguras
- ✅ **Cambios críticos alertados** - Detecta modificaciones sospechosas

📖 **Leer:** `docs/SEGURIDAD.md` para implementar

---

## 📚 Documentación Completa

1. **SEGURIDAD.md** ⭐ **NUEVO** - RLS, auditoría, checklist de seguridad
2. **ESTRUCTURA.md** - Mapa completo del proyecto y descripción de archivos
3. **FLUJO_COMPLETO.md** - Flujo detallado del cliente con ejemplos
4. **CONTABILIDAD.md** - Sistema de S/1 por día y reportes
5. **ACTUALIZACION_TARIFAS.md** - Cambios en el schema de BD
6. **MIGRACION_CHECKLIST.md** - Cómo migrar la BD
7. **REORGANIZACION_COMPLETADA.md** - Resumen de cambios

---

## ✅ Lo que Funciona

- ✅ Recibir mensajes de WhatsApp (Twilio)
- ✅ Procesar comprobantes de pago (imágenes)
- ✅ Alertas en Telegram con botones
- ✅ Aprobación/rechazo de pagos
- ✅ Crear usuarios en MikroTik
- ✅ Enviar credenciales por WhatsApp
- ✅ Registrar en base de datos
- ✅ Cálculo automático de montos
- ✅ Auditoría completa

---

## ⏳ Próximos Pasos

1. **Ejecutar migraciones en Supabase** (si no lo hiciste)
   - Copia: `migrations/001_initial_schema.sql`
   - SQL Editor → Pega y ejecuta

2. **Conectar MikroTik real**
   - Actualiza `.env` con tus credenciales

3. **Desplegar en VPS**
   - Sube código a GitHub
   - Clonar en VPS
   - Configurar `.env`
   - Ejecutar `python main.py`

---

## 🆘 Solución de Problemas

### El webhook no recibe mensajes
```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000/webhook

# Ver logs de uvicorn
python main.py
```

### No se actualiza Supabase
```bash
# Verificar credenciales
python -c "from app.core.config import settings; print(settings.SUPABASE_URL)"
```

### Botones de Telegram no funcionan
```bash
# Verificar webhook está configurado
curl https://api.telegram.org/bot[TG_TOKEN]/getWebhookInfo
```

---

## 📞 Soporte

- 📖 Lee la documentación en `docs/`
- 🐛 Revisa los logs del servidor
- 🧪 Ejecuta `python tests/verificar_sistema.py`

---

## 🎉 Estado del Proyecto

**FUNCIONAL Y LISTO PARA PRODUCCIÓN**

- Código modular y bien organizado
- Base de datos optimizada y auditada
- Documentación completa
- Tests incluidos
- Sistema de tarifas flexible

**Próxima fase:** Conectar MikroTik real y desplegar en VPS. 🚀
