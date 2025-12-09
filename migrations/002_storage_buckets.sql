-- ============================================================================
-- MIGRATION 002: Storage Buckets Configuration
-- ============================================================================
-- Nota: Este archivo es informativo. Los buckets se crean desde el dashboard
--       de Supabase o mediante la API de Storage.
-- ============================================================================

-- 📁 BUCKETS A CREAR EN SUPABASE:

-- 1. Bucket: "comprobantes-pago"
--    - Para guardar fotos de comprobantes de pago
--    - Políticas: Solo admins pueden ver todos, usuarios ven sus propios
--    - Max size: 10MB

-- 2. Bucket: "usuarios-hotspot"
--    - Información de usuarios creados en MikroTik
--    - Backup de credenciales (encriptadas)
--    - Max size: 1MB

-- 3. Bucket: "logs"
--    - Logs de operaciones
--    - Auditoría de cambios
--    - Max size: Ilimitado

-- ============================================================================
-- RLS POLICIES PARA STORAGE
-- ============================================================================

-- Para comprobantes-pago: El cliente ve solo sus propios comprobantes
-- INSERT: Solo usuarios autenticados pueden subir
-- SELECT: Solo el dueño y admins
-- DELETE: Solo admins

-- Para usuarios-hotspot: Solo admins pueden acceder
-- INSERT: Solo durante aprobación de venta
-- SELECT: Solo admins
-- DELETE: Solo admins (después de cierto tiempo)

-- ============================================================================
-- COMO CREAR LOS BUCKETS (Desde Supabase Dashboard)
-- ============================================================================

/*
1. Ve a Storage en tu dashboard de Supabase
2. Haz clic en "New Bucket"
3. Crear:

BUCKET 1: "comprobantes-pago"
- Public: OFF (privado)
- File size limit: 10MB

BUCKET 2: "usuarios-hotspot"
- Public: OFF (privado)
- File size limit: 1MB

BUCKET 3: "logs"
- Public: OFF (privado)
- File size limit: Sin límite

4. Configurar RLS Policies en cada bucket
*/

-- ============================================================================
-- EJEMPLO DE URL DE SUBIDA (desde código Python)
-- ============================================================================

/*
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Subir comprobante
file_data = open('comprobante.jpg', 'rb').read()
response = supabase.storage.from_('comprobantes-pago').upload(
    path=f'venta_{venta_id}.jpg',
    file=file_data,
    file_options={"cacheControl": "3600", "upsert": "false"}
)

# Obtener URL pública (si es público)
public_url = supabase.storage.from_('comprobantes-pago').get_public_url(f'venta_{venta_id}.jpg')
*/
