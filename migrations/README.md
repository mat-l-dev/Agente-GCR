# Migraciones de Base de Datos

## 📋 Descripción

Las migraciones están organizadas por versiones. Cada archivo SQL contiene:
- Creación de tablas
- Índices para optimización
- Triggers para automatización
- Data inicial

## 🚀 Cómo ejecutar

### Opción 1: Desde Supabase (Recomendado)

1. Abre tu proyecto en [supabase.com](https://supabase.com)
2. Ve a **SQL Editor**
3. Haz clic en **"New Query"**
4. Copia todo el contenido de `001_initial_schema.sql`
5. Ejecuta el SQL (botón **"Run"**)

### Opción 2: Desde la terminal

Si tienes `psql` instalado:

```bash
psql -h tu_host.supabase.co -U postgres -d postgres -f migrations/001_initial_schema.sql
```

## 📊 Schema Completo

### Tablas principales:

| Tabla | Propósito |
|-------|-----------|
| `clientes` | Registro de clientes |
| `planes` | Planes disponibles |
| `campamentos` | Zonas/ubicaciones |
| `ventas` | Histórico de compras |
| `pruebas` | Períodos de prueba (1 día) |
| `activaciones` | Historial de activaciones |
| `transacciones` | Movimientos de dinero |

### Flujo del cliente:

```
1. Cliente pide: "Activame internet en Campamento Cocha"
   ↓
2. Bot ofrece PRUEBA de 1 día
   ↓
3. Cliente activa y usa la prueba
   ↓
4. Cliente dice: "Ya está, yapéame 5 días"
   ↓
5. Bot crea venta pendiente y envía comprobante
   ↓
6. Cliente paga y manda captura
   ↓
7. Tú haces clic "APROBAR" en Telegram
   ↓
8. Bot crea usuario en MikroTik por 5 días
   ↓
9. Cliente recibe credenciales por WhatsApp
```

## 🔐 Seguridad

Las tablas están preparadas para **Row Level Security (RLS)** en Supabase:

- `clientes.whatsapp_id` es `UNIQUE` y actúa como clave
- `ventas` tiene FK a `clientes`
- Se registra `aprobado_por` para auditoría
- Triggers actualizan `updated_at` automáticamente

## 📝 Próximas migraciones

- `002_rls_policies.sql` - Configurar Row Level Security
- `003_storage_buckets.sql` - Configurar buckets para imágenes
- `004_realtime_subscriptions.sql` - Configurar subscripciones en tiempo real

## ⚠️ Nota importante

Si necesitas **revertir a un estado anterior**, tienes dos opciones:

1. **Dejar las tablas y hacer limpieza**:
   ```sql
   DELETE FROM transacciones;
   DELETE FROM activaciones;
   DELETE FROM pruebas;
   DELETE FROM ventas;
   DELETE FROM clientes;
   DELETE FROM planes;
   DELETE FROM campamentos;
   ```

2. **Borrar todo y recrear** (desarrolladores):
   ```sql
   DROP TABLE IF EXISTS transacciones CASCADE;
   DROP TABLE IF EXISTS activaciones CASCADE;
   DROP TABLE IF EXISTS pruebas CASCADE;
   DROP TABLE IF EXISTS ventas CASCADE;
   DROP TABLE IF EXISTS clientes CASCADE;
   DROP TABLE IF EXISTS planes CASCADE;
   DROP TABLE IF EXISTS campamentos CASCADE;
   ```
   Luego ejecutar `001_initial_schema.sql` nuevamente.
