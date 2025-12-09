# 📚 Bot ISP - Documentación Completa

Sistema automatizado de gestión de clientes ISP con WhatsApp, ChatGPT y MikroTik.

---

## 📖 Documentación Ordenada

### 🚀 Para Empezar (Lee primero)
| # | Archivo | Descripción |
|---|---------|-------------|
| 1 | **README.md** | 👈 Estás aquí - Guía general y inicio rápido |
| 2 | **OPENAI_API_KEY_SETUP.md** | Cómo obtener tu API key de ChatGPT |
| 3 | **GUIA_MIKROTIK_SETUP.md** | Configurar MikroTik paso a paso |
| 4 | **PLANES_USERMAN.md** | Crear perfiles 1Dia/3Dias/1Semana/1Mes |

### 🏗️ Arquitectura y Flujo
| # | Archivo | Descripción |
|---|---------|-------------|
| 5 | **ARQUITECTURA_DINAMICA.md** | Cómo funciona: ChatGPT + MikroTik dinámico |
| 6 | **FLUJO_COMPLETO_EJEMPLO.md** | Ejemplo paso a paso de conversación completa |

### 🔒 Seguridad y Costos
| # | Archivo | Descripción |
|---|---------|-------------|
| 7 | **SEGURIDAD.md** | Políticas RLS y seguridad de base de datos |
| 8 | **ANALISIS_COSTOS_IA.md** | Comparativa de costos ChatGPT vs alternativas |

---

## 🚀 Inicio Rápido

### 1. Configurar `.env`

```bash
cp .env.example .env
nano .env
```

**Variables críticas:**
```env
# OpenAI ChatGPT
OPENAI_API_KEY=sk-proj-xxxxx

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_FROM_NUMBER=whatsapp:+14155238886

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx

# MikroTik
MIKROTIK_HOST=190.123.45.67
MIKROTIK_PORT=8443
MIKROTIK_USER=api_bot
MIKROTIK_PASS=password_seguro

# Planes
PLAN_INICIAL_NUEVO=3Dias
PRECIO_POR_DIA=1.0
```

---

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

### 3. Ejecutar Migraciones SQL

En Supabase SQL Editor, ejecuta en orden:
1. `migrations/001_initial_schema.sql`
2. `migrations/002_storage_buckets.sql`
3. `migrations/003_rls_policies.sql`
4. `migrations/005_indexes_optimization.sql`
5. `migrations/006_audit_logging.sql`
6. `migrations/007_conversation_cache.sql`

---

### 4. Iniciar Bot

```bash
python main.py
```

Servidor: `http://0.0.0.0:8000`

---

## 🏗️ Arquitectura

```
Cliente WhatsApp
    ↓ (Twilio webhook)
Bot ISP (FastAPI + ChatGPT)
    ↓ (Supabase PostgreSQL)
    ↓ (MikroTik API SSL)
MikroTik Userman
    ↓ (Radius)
Cliente conectado a internet
```

---

## 📋 Flujo de Usuario

### Cliente Nuevo
```
1. Cliente: "Hola, venden internet?"
2. Bot: "¿Eres nuevo?"
3. Cliente: "Sí, Juan Pérez de Centro"
4. Bot crea cuenta con 3 días GRATIS en MikroTik
5. Envía credenciales por WhatsApp → Cliente conecta
6. (Cuando terminen los 3 días, cliente paga para recargar)
```

### Cliente Existente
```
1. Cliente: "Quiero 5 días"
2. Bot: "S/5. Envía comprobante"
3. Cliente envía foto
4. Notifica admin por Telegram
5. Admin aprueba → Bot activa en MikroTik
```

---

## 🗄️ Base de Datos

### Tablas Principales
- `clients` - Clientes (nombre, zona, teléfono)
- `sales` - Pagos y comprobantes
- `conversation_cache` - Historial chat
- `conversation_context` - Estado actual
- `ai_cost_tracking` - Costos IA

### Consulta Útil
```sql
SELECT name, phone_number, zona, created_at
FROM clients
WHERE is_active = true
ORDER BY created_at DESC;
```

---

## 💰 Costos Estimados (Mensual)

| Servicio | Costo | Notas |
|----------|-------|-------|
| Twilio WhatsApp | $5-10 | ~40 msgs/día |
| ChatGPT (optimizado) | $0.20 | Prompt comprimido |
| Supabase | $0 | Free tier |
| VPS Ubuntu | $5-20 | Según proveedor |
| **TOTAL** | ~$10-30 | |

**Ahorro:** Usar DeepSeek = $0.04/mes (en lugar de ChatGPT)

---

## 🔧 Comandos Útiles

### Verificar Estado
```bash
curl http://localhost:8000/
```

### Ver Logs
```bash
tail -f logs/bot.log
```

### Probar MikroTik
```bash
python test_mikrotik.py
```

---

## 🔒 Seguridad

✅ RLS activo en todas las tablas
✅ Usuario MikroTik API (no admin)
✅ Firewall solo permite IP VPS
✅ Puerto 8443 (no estándar)
✅ Logs de auditoría

Ver detalles: **SEGURIDAD.md**

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| Error 401 OpenAI | API key incorrecta → `OPENAI_API_KEY_SETUP.md` |
| Timeout MikroTik | Firewall bloqueando → `GUIA_MIKROTIK_SETUP.md` |
| Twilio no responde | Webhook mal configurado |

---

## 📝 Tecnologías

- **Backend:** Python 3.12 + FastAPI
- **IA:** OpenAI ChatGPT (gpt-3.5-turbo)
- **BD:** Supabase (PostgreSQL)
- **WhatsApp:** Twilio API
- **Alerts:** Telegram Bot API
- **Router:** MikroTik RouterOS (Userman + Radius)

---

## 🎯 Próximos Pasos

1. [ ] Obtener API key OpenAI válida
2. [ ] Configurar MikroTik (ver `GUIA_MIKROTIK_SETUP.md`)
3. [ ] Ejecutar migraciones SQL
4. [ ] Configurar webhook Twilio
5. [ ] Probar flujo completo

---

## 📞 Changelog

### v1.0 (Diciembre 2025)
- ✅ Migración Gemini → ChatGPT
- ✅ Prompt optimizado (83% menos tokens)
- ✅ Soporte multi-zona MikroTik
- ✅ Cache de conversaciones
- ✅ Userman con Radius
- ✅ Seguridad RLS completa
