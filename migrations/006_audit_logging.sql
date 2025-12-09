-- ============================================================================
-- MIGRATION 006: Auditoría y Logging de Cambios Sensibles
-- ============================================================================
-- Descripción: Tabla de auditoría para rastrear cambios en datos críticos
-- Ejecutar DESPUÉS de 005_indexes_optimization.sql
-- ============================================================================

-- ============================================================================
-- 1. TABLA DE AUDITORÍA
-- ============================================================================

CREATE TABLE audit_log (
  audit_id BIGSERIAL PRIMARY KEY,
  tabla_nombre TEXT NOT NULL,
  registro_id BIGINT,
  usuario_id TEXT,
  tipo_operacion TEXT NOT NULL, -- INSERT, UPDATE, DELETE
  datos_anteriores JSONB,       -- valor anterior (para UPDATE y DELETE)
  datos_nuevos JSONB,           -- valor nuevo (para INSERT y UPDATE)
  ip_address TEXT,
  user_agent TEXT,
  timestamp TIMESTAMP DEFAULT now(),
  
  -- Índices para búsqueda rápida
  CONSTRAINT audit_log_tabla_check 
    CHECK (tabla_nombre IN ('clientes', 'ventas', 'pruebas', 'activaciones', 'transacciones', 'configuracion'))
);

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. ÍNDICES PARA AUDITORÍA
-- ============================================================================

CREATE INDEX idx_audit_log_tabla ON audit_log(tabla_nombre);
CREATE INDEX idx_audit_log_usuario ON audit_log(usuario_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_registro ON audit_log(tabla_nombre, registro_id);

-- ============================================================================
-- 3. POLÍTICAS RLS PARA AUDITORÍA
-- ============================================================================

-- Solo admins pueden ver logs de auditoría
CREATE POLICY "audit_log_select_admin"
ON audit_log FOR SELECT
USING (auth.jwt() ->> 'role' = 'admin');

-- Solo el sistema puede insertar logs
CREATE POLICY "audit_log_insert_system"
ON audit_log FOR INSERT
WITH CHECK (auth.jwt() ->> 'role' = 'admin' OR auth.jwt() ->> 'role' = 'service');

-- ============================================================================
-- 4. FUNCIÓN PARA REGISTRAR CAMBIOS (TRIGGER)
-- ============================================================================

CREATE OR REPLACE FUNCTION register_audit_log()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (
    tabla_nombre,
    registro_id,
    tipo_operacion,
    datos_anteriores,
    datos_nuevos,
    usuario_id,
    timestamp
  ) VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id, NEW.venta_id, OLD.venta_id, NEW.cliente_id, OLD.cliente_id),
    TG_OP,
    CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
    CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
    auth.uid()::text,
    now()
  );
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 5. TRIGGERS PARA TABLA: ventas (más importante)
-- ============================================================================

CREATE TRIGGER trigger_audit_ventas_insert
AFTER INSERT ON ventas
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

CREATE TRIGGER trigger_audit_ventas_update
AFTER UPDATE ON ventas
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

CREATE TRIGGER trigger_audit_ventas_delete
AFTER DELETE ON ventas
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

-- ============================================================================
-- 6. TRIGGERS PARA TABLA: transacciones (dinero - CRÍTICA)
-- ============================================================================

CREATE TRIGGER trigger_audit_transacciones_insert
AFTER INSERT ON transacciones
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

CREATE TRIGGER trigger_audit_transacciones_update
AFTER UPDATE ON transacciones
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

CREATE TRIGGER trigger_audit_transacciones_delete
AFTER DELETE ON transacciones
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

-- ============================================================================
-- 7. TRIGGERS PARA TABLA: activaciones (seguridad)
-- ============================================================================

CREATE TRIGGER trigger_audit_activaciones_insert
AFTER INSERT ON activaciones
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

CREATE TRIGGER trigger_audit_activaciones_update
AFTER UPDATE ON activaciones
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

-- ============================================================================
-- 8. TRIGGERS PARA TABLA: clientes (identidad)
-- ============================================================================

CREATE TRIGGER trigger_audit_clientes_update
AFTER UPDATE ON clientes
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

-- ============================================================================
-- 9. TRIGGERS PARA TABLA: configuracion (crítica)
-- ============================================================================

CREATE TRIGGER trigger_audit_configuracion_update
AFTER UPDATE ON configuracion
FOR EACH ROW
EXECUTE FUNCTION register_audit_log();

-- ============================================================================
-- 10. TABLA DE CAMBIOS CRÍTICOS (para alertas)
-- ============================================================================

CREATE TABLE critical_changes (
  change_id BIGSERIAL PRIMARY KEY,
  audit_id BIGINT REFERENCES audit_log(audit_id),
  severidad TEXT NOT NULL, -- 'baja', 'media', 'alta', 'crítica'
  descripcion TEXT,
  accion_requerida BOOLEAN DEFAULT false,
  timestamp TIMESTAMP DEFAULT now()
);

ALTER TABLE critical_changes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "critical_changes_select_admin"
ON critical_changes FOR SELECT
USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 11. FUNCIÓN PARA DETECTAR CAMBIOS CRÍTICOS
-- ============================================================================

CREATE OR REPLACE FUNCTION detect_critical_changes()
RETURNS TRIGGER AS $$
DECLARE
  v_severity TEXT;
  v_description TEXT;
BEGIN
  -- Cambios críticos en transacciones
  IF TG_TABLE_NAME = 'transacciones' AND TG_OP = 'UPDATE' THEN
    IF (OLD.monto != NEW.monto) OR (OLD.tipo != NEW.tipo) THEN
      v_severity := 'crítica';
      v_description := 'Transacción modificada: monto o tipo cambiado';
      INSERT INTO critical_changes (audit_id, severidad, descripcion, accion_requerida)
      SELECT audit_id, v_severity, v_description, true
      FROM audit_log
      WHERE tabla_nombre = 'transacciones'
      ORDER BY audit_id DESC LIMIT 1;
    END IF;
  END IF;
  
  -- Cambios en venta aprobada
  IF TG_TABLE_NAME = 'ventas' AND TG_OP = 'UPDATE' THEN
    IF (OLD.estado = 'aprobada' AND NEW.estado != 'aprobada') THEN
      v_severity := 'alta';
      v_description := 'Venta aprobada fue desaprobada o rechazada';
      INSERT INTO critical_changes (audit_id, severidad, descripcion, accion_requerida)
      SELECT audit_id, v_severity, v_description, true
      FROM audit_log
      WHERE tabla_nombre = 'ventas'
      ORDER BY audit_id DESC LIMIT 1;
    END IF;
  END IF;
  
  -- Cambios en tarifa
  IF TG_TABLE_NAME = 'configuracion' AND TG_OP = 'UPDATE' THEN
    v_severity := 'alta';
    v_description := 'Configuración del sistema modificada';
    INSERT INTO critical_changes (audit_id, severidad, descripcion, accion_requerida)
    SELECT audit_id, v_severity, v_description, true
    FROM audit_log
    WHERE tabla_nombre = 'configuracion'
    ORDER BY audit_id DESC LIMIT 1;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para detectar cambios críticos
CREATE TRIGGER trigger_detect_critical
AFTER INSERT ON audit_log
FOR EACH ROW
EXECUTE FUNCTION detect_critical_changes();

-- ============================================================================
-- 12. VISTAS PARA REPORTES DE AUDITORÍA
-- ============================================================================

-- Vista: Últimos cambios por tabla
CREATE OR REPLACE VIEW v_audit_recent_changes AS
SELECT
  audit_id,
  tabla_nombre,
  registro_id,
  usuario_id,
  tipo_operacion,
  timestamp,
  CASE 
    WHEN tipo_operacion = 'INSERT' THEN 'Creado'
    WHEN tipo_operacion = 'UPDATE' THEN 'Modificado'
    WHEN tipo_operacion = 'DELETE' THEN 'Eliminado'
  END AS accion
FROM audit_log
ORDER BY timestamp DESC
LIMIT 100;

-- Vista: Cambios por usuario
CREATE OR REPLACE VIEW v_audit_by_user AS
SELECT
  usuario_id,
  COUNT(*) AS total_cambios,
  COUNT(CASE WHEN tipo_operacion = 'INSERT' THEN 1 END) AS inserts,
  COUNT(CASE WHEN tipo_operacion = 'UPDATE' THEN 1 END) AS updates,
  COUNT(CASE WHEN tipo_operacion = 'DELETE' THEN 1 END) AS deletes,
  MAX(timestamp) AS último_cambio
FROM audit_log
WHERE timestamp > now() - interval '30 days'
GROUP BY usuario_id
ORDER BY total_cambios DESC;

-- Vista: Cambios críticos
CREATE OR REPLACE VIEW v_critical_changes_recent AS
SELECT
  c.change_id,
  c.severidad,
  c.descripcion,
  c.accion_requerida,
  a.tabla_nombre,
  a.usuario_id,
  a.timestamp
FROM critical_changes c
JOIN audit_log a ON c.audit_id = a.audit_id
WHERE c.timestamp > now() - interval '7 days'
ORDER BY c.timestamp DESC;

-- ============================================================================
-- 13. FUNCIÓN DE LIMPIEZA (eliminar logs viejos)
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(days_to_keep INT DEFAULT 90)
RETURNS INT AS $$
DECLARE
  deleted_count INT;
BEGIN
  DELETE FROM audit_log
  WHERE timestamp < now() - (days_to_keep || ' days')::interval;
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 14. QUERIES ÚTILES PARA AUDITORÍA
-- ============================================================================

/*
-- Ver quién aprobó una venta
SELECT usuario_id, timestamp, datos_nuevos->>'estado' as nuevo_estado
FROM audit_log
WHERE tabla_nombre = 'ventas'
AND registro_id = 42
AND tipo_operacion = 'UPDATE'
AND datos_nuevos->>'estado' = 'aprobada'
ORDER BY timestamp DESC
LIMIT 1;

-- Ver todos los cambios en una transacción
SELECT *
FROM audit_log
WHERE tabla_nombre = 'transacciones'
AND registro_id = 100
ORDER BY timestamp DESC;

-- Ver cambios en últimas 24 horas
SELECT *
FROM v_audit_recent_changes
WHERE timestamp > now() - interval '24 hours'
ORDER BY timestamp DESC;

-- Ver cambios críticos sin resolver
SELECT *
FROM v_critical_changes_recent
WHERE accion_requerida = true
ORDER BY timestamp DESC;

-- Limpiar logs mayores a 90 días
SELECT cleanup_old_audit_logs(90);

*/

-- ============================================================================
-- 15. NOTAS IMPORTANTES
-- ============================================================================

/*
BENEFICIOS DE AUDITORÍA:

1. Compliance / Regulatorio
   - Cumplir con GDPR, CCPA, leyes locales
   - Rastrear quién hizo qué y cuándo

2. Seguridad
   - Detectar cambios maliciosos
   - Alertar sobre transacciones sospechosas
   - Recuperar datos accidentalmente eliminados

3. Debugging
   - Entender cómo llegó un registro a cierto estado
   - Reproducir errores

4. Auditoría Financiera
   - Verificar integridad de transacciones
   - Rastrear quién aprobó pagos

LIMITACIONES:

1. Espacio en disco
   - audit_log crece rápidamente
   - Usar cleanup_old_audit_logs() mensualmente

2. Performance
   - Insertar en audit_log ralentiza transacciones
   - No es crítico, pero considerar
   - Usar UNLOGGED TABLE si necesario (pierdes auditoría en crash)

3. Privacidad
   - audit_log contiene datos sensibles (pagos, identidad)
   - Asegúrate de RLS correctamente
   - Considerá encriptación adicional

*/

-- ============================================================================
-- PRÓXIMAS MIGRACIONES
-- ============================================================================

/*
007_views.sql: Vistas útiles para reportes
008_functions.sql: Funciones de negocio
*/
