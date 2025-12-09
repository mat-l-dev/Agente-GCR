-- ============================================================================
-- MIGRATION 005: Indexes y Optimización de Performance
-- ============================================================================
-- Descripción: Índices para queries rápidas y eficientes
-- Ejecutar DESPUÉS de 003_rls_policies.sql
-- ============================================================================

-- ============================================================================
-- 1. ÍNDICES EN TABLA: clientes
-- ============================================================================

-- Búsqueda rápida por WhatsApp ID
CREATE INDEX idx_clientes_whatsapp_id ON clientes(whatsapp_id);

-- Búsqueda rápida por nombre
CREATE INDEX idx_clientes_nombre ON clientes(nombre);

-- Búsqueda por nombre para autocomplete (case-insensitive)
CREATE INDEX idx_clientes_nombre_lower ON clientes(LOWER(nombre));

-- Índice para buscar clientes de un campamento
CREATE INDEX idx_clientes_campamento_id ON clientes(campamento_id);

-- ============================================================================
-- 2. ÍNDICES EN TABLA: ventas
-- ============================================================================

-- Búsqueda rápida de ventas por cliente
CREATE INDEX idx_ventas_whatsapp_id ON ventas(whatsapp_id);

-- Búsqueda de ventas en un rango de fechas
CREATE INDEX idx_ventas_fecha_creacion ON ventas(fecha_creacion DESC);

-- Búsqueda de ventas por estado (pendiente, aprobada, rechazada)
CREATE INDEX idx_ventas_estado ON ventas(estado);

-- Búsqueda combinada: cliente + estado
CREATE INDEX idx_ventas_whatsapp_estado ON ventas(whatsapp_id, estado);

-- Búsqueda de ventas por plan
CREATE INDEX idx_ventas_plan_id ON ventas(plan_id);

-- Búsqueda de ventas por campamento
CREATE INDEX idx_ventas_campamento_id ON ventas(campamento_id);

-- Búsqueda de ventas por rango de fechas + estado (muy común)
CREATE INDEX idx_ventas_fecha_estado ON ventas(fecha_creacion DESC, estado);

-- ============================================================================
-- 3. ÍNDICES EN TABLA: pruebas
-- ============================================================================

-- Búsqueda de pruebas por cliente
CREATE INDEX idx_pruebas_whatsapp_id ON pruebas(whatsapp_id);

-- Búsqueda de pruebas por fecha
CREATE INDEX idx_pruebas_fecha_creacion ON pruebas(fecha_creacion DESC);

-- Búsqueda de pruebas por estado
CREATE INDEX idx_pruebas_estado ON pruebas(estado);

-- Búsqueda de pruebas por venta (para verificar aprovación)
CREATE INDEX idx_pruebas_venta_id ON pruebas(venta_id);

-- ============================================================================
-- 4. ÍNDICES EN TABLA: activaciones
-- ============================================================================

-- Búsqueda rápida de activaciones por venta
CREATE INDEX idx_activaciones_venta_id ON activaciones(venta_id);

-- Búsqueda de activaciones por fecha
CREATE INDEX idx_activaciones_fecha ON activaciones(fecha_creacion DESC);

-- Búsqueda de activaciones por estado
CREATE INDEX idx_activaciones_estado ON activaciones(estado);

-- ============================================================================
-- 5. ÍNDICES EN TABLA: transacciones (AUDITORÍA)
-- ============================================================================

-- Búsqueda de transacciones por cliente
CREATE INDEX idx_transacciones_whatsapp_id ON transacciones(whatsapp_id);

-- Búsqueda de transacciones por fecha
CREATE INDEX idx_transacciones_fecha ON transacciones(fecha DESC);

-- Búsqueda de transacciones por tipo (ingreso, egreso, etc)
CREATE INDEX idx_transacciones_tipo ON transacciones(tipo);

-- Búsqueda combinada para reportes financieros
CREATE INDEX idx_transacciones_fecha_tipo ON transacciones(fecha DESC, tipo);

-- ============================================================================
-- 6. ÍNDICES EN TABLA: planes
-- ============================================================================

-- Búsqueda de planes por estado
CREATE INDEX idx_planes_activo ON planes(activo);

-- ============================================================================
-- 7. ÍNDICES EN TABLA: campamentos
-- ============================================================================

-- Búsqueda de campamentos por estado
CREATE INDEX idx_campamentos_activo ON campamentos(activo);

-- ============================================================================
-- 8. ÍNDICES COMPUESTOS (MULTI-COLUMN) - ADVANCED
-- ============================================================================

-- Para reportes: "Mostrar ventas por cliente en un rango de fechas"
CREATE INDEX idx_ventas_cliente_fecha ON ventas(whatsapp_id, fecha_creacion DESC)
WHERE estado = 'aprobada';

-- Para reportes: "Mostrar ingresos por día"
CREATE INDEX idx_transacciones_fecha_monto ON transacciones(DATE(fecha), tipo, monto);

-- ============================================================================
-- 9. VACUUM Y ANÁLISIS (mantenimiento)
-- ============================================================================

/*
-- Ejecutar mensualmente para optimizar:
VACUUM ANALYZE clientes;
VACUUM ANALYZE ventas;
VACUUM ANALYZE pruebas;
VACUUM ANALYZE activaciones;
VACUUM ANALYZE transacciones;

-- O para toda la base de datos:
VACUUM ANALYZE;
*/

-- ============================================================================
-- 10. ESTADÍSTICAS Y MONITOREO
-- ============================================================================

/*
-- Ver tamaño de índices:
SELECT
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_indexes
JOIN pg_class ON pg_class.relname = pg_indexes.indexname
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Ver queries lentas (si log_min_duration_statement = 1000):
SELECT
  query,
  calls,
  total_time,
  mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Ver tabla más grande:
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

*/

-- ============================================================================
-- 11. NOTAS DE PERFORMANCE
-- ============================================================================

/*
QUERIES OPTIMIZADAS POR ÍNDICES:

1. Listar ventas pendientes de un cliente
   SELECT * FROM ventas 
   WHERE whatsapp_id = '51999888777' 
   AND estado = 'pendiente'
   ORDER BY fecha_creacion DESC;
   → Usa: idx_ventas_whatsapp_estado

2. Reporte: Ingresos del día
   SELECT SUM(monto) FROM transacciones
   WHERE DATE(fecha) = CURRENT_DATE
   AND tipo = 'ingreso';
   → Usa: idx_transacciones_fecha_monto

3. Buscar cliente por nombre (autocomplete)
   SELECT * FROM clientes
   WHERE LOWER(nombre) LIKE LOWER('%carlos%')
   LIMIT 10;
   → Usa: idx_clientes_nombre_lower

4. Activaciones aprobadas de una venta
   SELECT * FROM activaciones
   WHERE venta_id = 42
   AND estado = 'aprobada';
   → Usa: idx_activaciones_venta_id

*/

-- ============================================================================
-- 12. MONITOREO EN SUPABASE
-- ============================================================================

/*
En Supabase dashboard:

1. Ir a Database → Query Performance
   - Ver queries lentas
   - Sugerir índices automáticamente

2. Ir a Database → Logs
   - Ver todas las queries ejecutadas
   - Filtrar por duración

3. Usar pgAdmin (si acceso):
   - Right-click tabla → Vacuum
   - Right-click tabla → Analyze
   - Ver table size gráficamente

*/

-- ============================================================================
-- 13. ANÁLISIS AUTOMÁTICO DE ÍNDICES
-- ============================================================================

/*
-- Crear vista para analizar índices no utilizados:
CREATE OR REPLACE VIEW v_unused_indexes AS
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Ver:
SELECT * FROM v_unused_indexes;

-- Eliminar índices no utilizados (después de 30+ días):
-- DROP INDEX idx_name;

*/

-- ============================================================================
-- 14. CONFIGURACIÓN RECOMENDADA EN PostgreSQL
-- ============================================================================

/*
Para Supabase, estos parámetros ya están optimizados.
Pero si usas PostgreSQL standalone:

-- shared_buffers = 256MB (25% de RAM del servidor)
-- effective_cache_size = 1GB (50% de RAM)
-- work_mem = 16MB
-- maintenance_work_mem = 64MB
-- random_page_cost = 1.1 (para SSD)
-- effective_io_concurrency = 200 (para SSD)

Luego: systemctl restart postgresql
*/

-- ============================================================================
-- PRÓXIMAS MIGRACIONES
-- ============================================================================

/*
006_audit_logging.sql: Tabla de auditoría para cambios sensibles
007_views.sql: Vistas útiles para reportes
*/
