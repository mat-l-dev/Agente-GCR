-- ============================================================================
-- MIGRATION 004: Storage RLS (Imágenes de Comprobantes)
-- ============================================================================
-- Descripción: Configurar seguridad para archivos en Supabase Storage
-- ACTUALIZADO: Diciembre 2024 - Nueva UI de Supabase
-- ============================================================================

/*
================================================================================
PASO 1: CREAR BUCKET "comprobantes"
================================================================================

1. Ir a Supabase Dashboard → Storage (ícono de carpeta en el menú lateral)
2. Click en "New bucket"
3. Configurar:
   - Name: comprobantes
   - Public bucket: NO (desmarcar)
   - File size limit: 10MB
4. Click "Create bucket"

================================================================================
PASO 2: CREAR POLÍTICAS (Nueva UI de Supabase)
================================================================================

1. En Storage → click en el bucket "comprobantes"
2. Click en el tab "Policies" (arriba)
3. Click "New policy"

--- POLÍTICA 1: Permitir INSERT público (para que el bot suba comprobantes) ---

En el modal "Adding new policy to comprobantes":

  Policy name: allow_public_uploads
  
  Allowed operation: Marcar ☑️ INSERT
  
  Target roles: Dejarlo en "Defaults to all (public) roles if none selected"
  
  Policy definition:
    bucket_id = 'comprobantes'

  Click "Review" → "Save policy"

--- POLÍTICA 2: Permitir SELECT para admins (ver comprobantes) ---

Click "New policy" de nuevo:

  Policy name: allow_admin_select
  
  Allowed operation: Marcar ☑️ SELECT
  
  Target roles: Dejar default
  
  Policy definition:
    bucket_id = 'comprobantes'

  Click "Review" → "Save policy"

================================================================================
NOTA: Políticas Simplificadas
================================================================================

Para un bot de ISP pequeño, estas políticas básicas son suficientes:

1. INSERT público: Permite que el bot (sin autenticación) suba comprobantes
2. SELECT público: Permite ver los comprobantes (para el admin en Telegram)

Si necesitas más seguridad en el futuro:
- Usa autenticación con service_role key (ya la tienes en .env)
- Restringe por carpetas usando storage.foldername()

================================================================================
VERIFICAR QUE FUNCIONA
================================================================================

Después de crear las políticas, prueba subir una imagen:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")  # Usar service_role para bypass RLS
)

# Probar subida
with open("test.jpg", "rb") as f:
    result = supabase.storage.from_("comprobantes").upload(
        "test/prueba.jpg",
        f.read(),
        {"content-type": "image/jpeg"}
    )
print(result)
```

*/

-- ============================================================================
-- NOTAS TÉCNICAS
-- ============================================================================

/*
ESTRUCTURA DE ARCHIVOS RECOMENDADA:

comprobantes/
  ├── {venta_id}/
  │   └── {uuid}.jpg       # Comprobante de pago
  └── {whatsapp_id}/
      └── {fecha}_{uuid}.jpg

EJEMPLO:
  comprobantes/42/a1b2c3d4.jpg
  comprobantes/+51999888777/2024-01-15_xyz123.jpg

BUENAS PRÁCTICAS:
1. Usar UUIDs para nombres de archivo (evitar colisiones)
2. Validar tipo MIME antes de subir (solo image/jpeg, image/png)
3. Limitar tamaño a 10MB
4. El bot usa service_role key que bypasea RLS
*/
