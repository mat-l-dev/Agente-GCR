-- ============================================================================
-- MIGRATION 003: Row Level Security (RLS) Policies
-- ============================================================================
-- Descripción: Configurar seguridad a nivel de fila en Supabase
-- Importante: Ejecutar DESPUÉS de 001_initial_schema.sql
-- ============================================================================

-- ============================================================================
-- 1. HABILITAR RLS EN TODAS LAS TABLAS
-- ============================================================================

ALTER TABLE configuracion ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE planes ENABLE ROW LEVEL SECURITY;
ALTER TABLE campamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE ventas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pruebas ENABLE ROW LEVEL SECURITY;
ALTER TABLE activaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE transacciones ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. TABLA: configuracion (SOLO ADMINS)
-- ============================================================================

-- Los usuarios autenticados pueden ver la configuración (lectura)
CREATE POLICY "configuracion_select_authenticated"
ON configuracion FOR SELECT
USING (auth.role() = 'authenticated_user');

-- Solo admins pueden actualizar
CREATE POLICY "configuracion_update_admin"
ON configuracion FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- Solo admins pueden insertar
CREATE POLICY "configuracion_insert_admin"
ON configuracion FOR INSERT
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 3. TABLA: planes (LECTURA PÚBLICA, ESCRITURA ADMIN)
-- ============================================================================

-- Cualquiera puede ver planes
CREATE POLICY "planes_select_public"
ON planes FOR SELECT
USING (true);

-- Solo admins pueden modificar
CREATE POLICY "planes_update_admin"
ON planes FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "planes_insert_admin"
ON planes FOR INSERT
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "planes_delete_admin"
ON planes FOR DELETE
USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 4. TABLA: campamentos (LECTURA PÚBLICA, ESCRITURA ADMIN)
-- ============================================================================

CREATE POLICY "campamentos_select_public"
ON campamentos FOR SELECT
USING (true);

CREATE POLICY "campamentos_update_admin"
ON campamentos FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "campamentos_insert_admin"
ON campamentos FOR INSERT
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "campamentos_delete_admin"
ON campamentos FOR DELETE
USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 5. TABLA: clientes
-- ============================================================================

-- Los clientes ven solo SUS PROPIOS registros
CREATE POLICY "clientes_select_own"
ON clientes FOR SELECT
USING (whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR auth.jwt() ->> 'role' = 'admin');

-- Los clientes pueden actualizar solo SU PROPIO registro
CREATE POLICY "clientes_update_own"
ON clientes FOR UPDATE
USING (whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR auth.jwt() ->> 'role' = 'admin')
WITH CHECK (whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR auth.jwt() ->> 'role' = 'admin');

-- Los clientes pueden insertarse a sí mismos
CREATE POLICY "clientes_insert_self"
ON clientes FOR INSERT
WITH CHECK (whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR auth.jwt() ->> 'role' = 'admin');

-- Solo admins pueden eliminar
CREATE POLICY "clientes_delete_admin"
ON clientes FOR DELETE
USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 6. TABLA: ventas
-- ============================================================================

-- Los clientes ven solo SUS PROPIAS ventas
CREATE POLICY "ventas_select_own"
ON ventas FOR SELECT
USING (
  whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR 
  auth.jwt() ->> 'role' = 'admin'
);

-- Los clientes pueden insertar sus propias ventas
CREATE POLICY "ventas_insert_own"
ON ventas FOR INSERT
WITH CHECK (
  whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR 
  auth.jwt() ->> 'role' = 'admin'
);

-- Solo admins pueden actualizar (aprobar/rechazar)
CREATE POLICY "ventas_update_admin"
ON ventas FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- Solo admins pueden eliminar
CREATE POLICY "ventas_delete_admin"
ON ventas FOR DELETE
USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 7. TABLA: pruebas
-- ============================================================================

-- Los clientes ven solo SUS PROPIAS pruebas
CREATE POLICY "pruebas_select_own"
ON pruebas FOR SELECT
USING (
  whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR 
  auth.jwt() ->> 'role' = 'admin'
);

-- Los clientes pueden insertar sus propias pruebas
CREATE POLICY "pruebas_insert_own"
ON pruebas FOR INSERT
WITH CHECK (
  whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR 
  auth.jwt() ->> 'role' = 'admin'
);

-- Solo admins pueden actualizar
CREATE POLICY "pruebas_update_admin"
ON pruebas FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 8. TABLA: activaciones (SOLO LECTURA Y ADMIN)
-- ============================================================================

-- Solo admins pueden ver activaciones
CREATE POLICY "activaciones_select_admin"
ON activaciones FOR SELECT
USING (auth.jwt() ->> 'role' = 'admin');

-- Solo admins pueden insertar
CREATE POLICY "activaciones_insert_admin"
ON activaciones FOR INSERT
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- Solo admins pueden actualizar
CREATE POLICY "activaciones_update_admin"
ON activaciones FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 9. TABLA: transacciones (AUDITORÍA)
-- ============================================================================

-- Los clientes ven solo SUS PROPIAS transacciones
CREATE POLICY "transacciones_select_own"
ON transacciones FOR SELECT
USING (
  whatsapp_id = auth.jwt() ->> 'whatsapp_id' OR 
  auth.jwt() ->> 'role' = 'admin'
);

-- Solo el sistema (servicio) puede insertar transacciones
CREATE POLICY "transacciones_insert_service"
ON transacciones FOR INSERT
WITH CHECK (auth.jwt() ->> 'role' = 'admin' OR auth.jwt() ->> 'role' = 'service');

-- Solo admins pueden actualizar (para auditoría)
CREATE POLICY "transacciones_update_admin"
ON transacciones FOR UPDATE
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- 10. COMENTARIOS SOBRE RLS
-- ============================================================================

/*
RESUMEN DE SEGURIDAD:

1. CONFIGURACION
   - SELECT: Usuarios autenticados
   - UPDATE/INSERT: Solo admins

2. PLANES y CAMPAMENTOS
   - SELECT: Público (no necesita login)
   - UPDATE/INSERT/DELETE: Solo admins

3. CLIENTES
   - SELECT: El cliente ve su registro + admins ven todo
   - UPDATE: El cliente actualiza su registro + admins pueden actualizar todo
   - INSERT: Los clientes se crean a sí mismos
   - DELETE: Solo admins

4. VENTAS
   - SELECT: El cliente ve sus ventas + admins ven todo
   - INSERT: El cliente crea sus propias ventas
   - UPDATE: Solo admins (para aprobar/rechazar)
   - DELETE: Solo admins

5. PRUEBAS
   - SELECT: El cliente ve sus pruebas + admins ven todo
   - INSERT: El cliente crea sus propias pruebas
   - UPDATE: Solo admins
   - DELETE: Solo admins (la eliminación es rara)

6. ACTIVACIONES
   - SELECT/INSERT/UPDATE: Solo admins (es auditoría)
   - DELETE: Nunca (mantener historial)

7. TRANSACCIONES
   - SELECT: El cliente ve sus transacciones
   - INSERT: Solo el servicio/admin (para auditoría)
   - UPDATE: Solo admins (para auditoría)
   - DELETE: Nunca (no se deben borrar registros de dinero)

ROLES EN JWT:
- 'authenticated_user': Cliente normal
- 'admin': Administrador del sistema
- 'service': Servicio interno (bot)

*/

-- ============================================================================
-- 11. USUARIOS DE PRUEBA (OPCIONAL - para testing)
-- ============================================================================

/*
-- Para testing, puedes crear usuarios con roles específicos
-- NOTA: Estos se crean desde Supabase Auth, no desde SQL

-- Cliente de prueba:
-- Email: cliente@test.com
-- Password: Test123!
-- JWT custom claims: {"role": "authenticated_user", "whatsapp_id": "+51999888777"}

-- Admin de prueba:
-- Email: admin@test.com
-- Password: Admin123!
-- JWT custom claims: {"role": "admin"}

-- En Supabase, ve a Authentication → Users → Editar usuario
-- Y agrega los custom claims en la sección JWT
*/

-- ============================================================================
-- PRÓXIMAS MIGRACIONES
-- ============================================================================

/*
004_storage_rls.sql: Configurar RLS para Storage (imágenes)
005_indexes_optimization.sql: Índices adicionales para optimización
006_audit_logging.sql: Tabla de auditoría para cambios sensibles
*/
