# 🔒 SEGURIDAD EN SUPABASE - Guía Completa

## 📋 Contenido

1. [Row Level Security (RLS)](#rls)
2. [Storage RLS](#storage)
3. [Auditoría y Logging](#auditoría)
4. [Checklist de Seguridad](#checklist)
5. [Cómo Ejecutar las Migraciones](#ejecución)
6. [Roles y Permisos](#roles)

---

## 🔐 <a name="rls"></a> Row Level Security (RLS)

### ¿Qué es RLS?

RLS permite que la base de datos **automáticamente** filtre filas según quién está usando la aplicación. En lugar de confiar en tu código Python, PostgreSQL garantiza que:

- ✅ Los clientes **solo ven sus propios datos**
- ✅ Los admins pueden ver **todo**
- ✅ El sistema (bot) tiene permisos específicos

### Ejemplo Visual

```
Usuario: cliente@whatsapp (ID: 51999888777)
  ↓
SELECT * FROM ventas;
  ↓
PostgreSQL filtra automáticamente:
  ↓
RESULTADO: Solo ventas donde whatsapp_id = '51999888777'
```

Sin RLS, si había un bug en Python, el cliente podría ver ventas de otros. **Con RLS, es imposible.**

### Políticas Implementadas

#### 1️⃣ Tabla `configuracion` (S/1.00/day)
```sql
-- Solo lectura para usuarios autenticados
SELECT: PERMITIDO (usuarios autenticados)
UPDATE: SOLO ADMINS
INSERT: SOLO ADMINS
```

**Por qué:** La tarifa no debe cambiar por un bug en Python.

#### 2️⃣ Tabla `planes` (Basic, Pro, Premium)
```sql
SELECT: PÚBLICO (no necesita login)
UPDATE/INSERT/DELETE: SOLO ADMINS
```

**Por qué:** Los planes son información pública. Solo admins los crean/modifican.

#### 3️⃣ Tabla `clientes` (Identidad)
```sql
SELECT: El cliente VE SU PROPIO REGISTRO
        + Admins VEN TODO
UPDATE: El cliente ACTUALIZA SU REGISTRO
        + Admins ACTUALIZAN TODO
INSERT: El cliente SE CREA A SÍ MISMO
DELETE: SOLO ADMINS
```

**Ejemplo:**
- Cliente con WhatsApp `51999888777` hace `SELECT * FROM clientes`
  - Resultado: Solo su registro
- Admin hace `SELECT * FROM clientes`
  - Resultado: Todos los clientes

#### 4️⃣ Tabla `ventas` (Pagos - CRÍTICA)
```sql
SELECT: El cliente VE SUS VENTAS
        + Admins VEN TODO
INSERT: El cliente CREA SUS PROPIAS VENTAS
UPDATE: SOLO ADMINS (para aprobar/rechazar)
DELETE: SOLO ADMINS
```

**Por qué es crítica:** Los clientes no deben poder modificar montos de pago.

#### 5️⃣ Tabla `transacciones` (Dinero - MÁS CRÍTICA)
```sql
SELECT: El cliente VE SUS TRANSACCIONES
        + Admins VEN TODO
INSERT: SOLO ADMIN/SERVICIO (bot)
UPDATE: SOLO ADMIN (auditoría)
DELETE: NUNCA (no se pueden borrar registros de dinero)
```

**Por qué:** Una transacción es un registro de dinero. No debe modificarse nunca.

---

## 💾 <a name="storage"></a> Storage RLS (Imágenes)

### Buckets en Supabase Storage

```
Proyecto Supabase
  ├── Storage
  │   ├── comprobantes/
  │   │   ├── 1/
  │   │   │   └── uuid.jpg (cliente subió prueba de pago)
  │   │   ├── 2/
  │   │   │   └── uuid.jpg
  │   │   └── 3/
  │   │       └── uuid.jpg
  │   │
  │   └── evidencias/
  │       ├── 101/
  │       │   └── uuid.jpg (evidencia de prueba de velocidad)
  │       ├── 102/
  │       └── uuid.jpg
```

### Políticas de Storage

#### Política 1: Subir comprobante
```
Ruta: comprobantes/{venta_id}/{filename}
Quién puede subir: El cliente que hizo la venta
Quién puede descargar: El cliente + Admins
```

**Implementación en Python:**
```python
# Solo paso nombres como: "42/comprobante.jpg"
# La política valida que el cliente hizo la venta 42
storage.from_("comprobantes").upload(
    "42/comprobante.jpg",  # ← RLS valida venta_id = 42
    file_bytes
)
```

#### Política 2: Descargar comprobante
```
Quién: El cliente propietario + Admins
```

---

## 📊 <a name="auditoría"></a> Auditoría y Logging

### Tabla `audit_log`

Cada cambio importante se registra automáticamente:

```sql
-- Cuando alguien aprueba una venta
INSERT INTO audit_log (
  tabla_nombre = 'ventas',
  registro_id = 42,
  tipo_operacion = 'UPDATE',
  usuario_id = 'admin-123',
  datos_anteriores = {estado: 'pendiente', monto: 5.00},
  datos_nuevos = {estado: 'aprobada', monto: 5.00},
  timestamp = 2025-12-08 15:30:00
);
```

### Cambios Críticos Detectados Automáticamente

| Cambio | Severidad | Acción |
|--------|-----------|--------|
| Modificar transacción (monto/tipo) | CRÍTICA | Alerta admin |
| Venta aprobada → rechazada | ALTA | Alerta admin |
| Cambiar tarifa (S/1.00) | ALTA | Alerta admin |
| Eliminar cliente | ALTA | Alerta admin |

### Vistas Útiles

**Ver quién aprobó cada venta:**
```sql
SELECT usuario_id, timestamp, datos_nuevos
FROM audit_log
WHERE tabla_nombre = 'ventas'
AND tipo_operacion = 'UPDATE'
AND datos_nuevos->>'estado' = 'aprobada'
ORDER BY timestamp DESC;
```

**Ver cambios sospechosos (últimas 7 días):**
```sql
SELECT * FROM v_critical_changes_recent
WHERE accion_requerida = true;
```

**Ver actividad por usuario (últimos 30 días):**
```sql
SELECT * FROM v_audit_by_user;
```

---

## ✅ <a name="checklist"></a> Checklist de Seguridad

### Antes de ir a Producción

- [ ] **RLS Habilitado**
  ```sql
  SELECT tablename, rowsecurity 
  FROM pg_tables 
  WHERE schemaname = 'public';
  -- Todos deben tener: rowsecurity = true
  ```

- [ ] **Índices Creados** (para performance)
  ```sql
  SELECT * FROM pg_indexes WHERE schemaname = 'public';
  -- Debe haber índices en: whatsapp_id, fecha, estado
  ```

- [ ] **Auditoría Funcionando**
  ```sql
  SELECT COUNT(*) FROM audit_log;
  -- Debe crecer con cada cambio
  ```

- [ ] **Storage RLS Configurado**
  - [ ] Bucket `comprobantes` creado
  - [ ] Bucket `evidencias` creado
  - [ ] Políticas RLS aplicadas

- [ ] **Usuarios Creados**
  - [ ] Admin user con role = 'admin'
  - [ ] Servicio bot con role = 'service'
  - [ ] Al menos un cliente de prueba

- [ ] **Contraseñas Seguras**
  - [ ] MikroTik: cambiar credenciales por defecto
  - [ ] Supabase: usar API key `anon` solo en cliente
  - [ ] Supabase: usar API key `service_role` solo en servidor

- [ ] **Environment Variables Protegidas**
  - [ ] `.env` NO está en GitHub
  - [ ] `.env.example` tiene placeholders
  - [ ] Server tiene `.env` seguro (no en contenedor)

- [ ] **Telegram Bot Token**
  - [ ] Almacenado en `.env`
  - [ ] No está en logs

- [ ] **WhatsApp Twilio Token**
  - [ ] Almacenado en `.env`
  - [ ] Webhook valida firma de Twilio

---

## 🚀 <a name="ejecución"></a> Cómo Ejecutar las Migraciones

### Orden de Ejecución

```
1. 001_initial_schema.sql     (YA HECHO)
2. 002_data_initialization.sql (Si lo tienes)
3. 003_rls_policies.sql       ← NUEVO
4. 004_storage_rls.sql        ← NUEVO (referencia)
5. 005_indexes_optimization.sql ← NUEVO
6. 006_audit_logging.sql      ← NUEVO
```

### En Supabase Dashboard

1. Ve a: **SQL Editor** (lado izquierdo)
2. Copia el contenido de `003_rls_policies.sql`
3. Pega en el editor
4. Click en **Run** (botón verde)
5. Espera confirmación: "Statements executed successfully"
6. Repite para 005 y 006

### Validation Queries

Después de cada migración, ejecuta para verificar:

```sql
-- Verificar RLS habilitado
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Verificar índices
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Verificar triggers de auditoría
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table;
```

---

## 👥 <a name="roles"></a> Roles y Permisos

### Roles en JWT

Cuando un usuario autentica, Supabase crea un JWT con `role`:

```json
{
  "sub": "user-id-123",
  "email": "cliente@whatsapp.com",
  "role": "authenticated_user",  // ← CLIENTE
  "whatsapp_id": "51999888777",   // ← ID del cliente
  "aud": "authenticated",
  "iat": 1702080600,
  "exp": 1702167000
}
```

### Cómo Configurar Roles en Supabase

1. **Para Cliente Normal:**
   - Ve a: Auth → Users
   - Edita usuario
   - Scroll a: **Raw App Metadata**
   - Agrega:
   ```json
   {
     "role": "authenticated_user",
     "whatsapp_id": "51999888777"
   }
   ```

2. **Para Admin:**
   - Mismo proceso
   - Metadata:
   ```json
   {
     "role": "admin"
   }
   ```

3. **Para Servicio (Bot):**
   - Crea usuario con email: `bot@internal.local`
   - Metadata:
   ```json
   {
     "role": "service"
   }
   ```

### Permisos por Rol

| Rol | Tabla | SELECT | INSERT | UPDATE | DELETE |
|-----|-------|--------|--------|--------|--------|
| **Cliente** | clientes | SÍ (propio) | SÍ (self) | SÍ (propio) | NO |
| | ventas | SÍ (propias) | SÍ | NO | NO |
| | transacciones | SÍ (propias) | NO | NO | NO |
| | planes | SÍ | NO | NO | NO |
| **Admin** | (todas) | SÍ | SÍ | SÍ | SÍ |
| **Service (Bot)** | ventas | SÍ | SÍ | SÍ | NO |
| | transacciones | SÍ | SÍ | SÍ | NO |
| | activaciones | SÍ | SÍ | SÍ | NO |

---

## 🐛 Debugging de RLS

### Problema: "Permission denied for schema public"

**Causa:** RLS bloqueando tu operación
**Solución:**
```sql
-- Ver políticas
SELECT * FROM pg_policies WHERE schemaname = 'public';

-- Disable RLS temporalmente (SOLO PARA DEBUG)
ALTER TABLE ventas DISABLE ROW LEVEL SECURITY;

-- Re-habilitar
ALTER TABLE ventas ENABLE ROW LEVEL SECURITY;
```

### Problema: Queries en Python lento

**Causa:** RLS agregando overhead
**Solución:**
```sql
-- Ver queries lentas
SELECT query, mean_time 
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
ORDER BY mean_time DESC
LIMIT 10;

-- Agregar índices (ya incluido en 005_indexes_optimization.sql)
```

### Problema: Auditoría no se registra

**Causa:** Trigger no disparando
**Solución:**
```sql
-- Ver triggers
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public';

-- Ver si audit_log recibe inserts
SELECT COUNT(*) FROM audit_log;

-- Ver último insert
SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 5;
```

---

## 📚 Referencias

- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Row Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [GDPR Compliance](https://gdpr-info.eu/)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0
