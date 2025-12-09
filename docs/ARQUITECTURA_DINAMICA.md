# 🔄 Arquitectura Bot → MikroTik (Dinámica)

## Cambio Principal
**Antes**: Bot tenía planes hardcodeados (`planes.py`)  
**Ahora**: Bot **lee los planes directamente de MikroTik**

---

## Flujo de Activación

```
Cliente             Bot (FastAPI)          MikroTik (Userman)
   │                    │                         │
   ├─ "Hola"           │                         │
   ├──────────────────>│                         │
   │                   │ 1. Obtener planes ──────>│
   │                   │<────── (lista dinám) ────│
   │                   │                         │
   │                   │ 2. ¿Nuevo o existente?  │
   │<─────────────────┤                         │
   │  "Soy nuevo"      │                         │
   ├──────────────────>│                         │
   │                   │ 3. Crear usuario ──────>│
   │                   │    (plan=3Dias gratis)  │
   │                   │<─ OK + usuario/pass ────│
   │  "¡Usuario listo!"│                         │
   │  "3 días gratis"  │                         │
   │<─────────────────┤                         │
   │  (conecta)        │                         │
   ├──────────────────────────────────────────>│
   │                   │                         │
   │  (días terminan)  │                         │
   │  "Quiero 1 sem"   │                         │
   ├──────────────────>│                         │
   │  "Envía pago"     │                         │
   │<─────────────────┤                         │
   │  [COMPROBANTE]    │                         │
   ├──────────────────>│                         │
   │                   │ 4. Guardar en Supabase  │
   │                   │ 5. Alerta Telegram      │
   │                   │ (admin espera)          │
   │                   │                         │
   │  (admin aprueba)  │ 6. Actualizar plan ──┐  │
   │                   │    (1Semana) ────────┼─>│
   │                   │<──── OK ───────────────┘
   │  "¡Activado!"     │                         │
   │<─────────────────┤                         │
   │  (conectar)       │                         │
   ├──────────────────────────────────────────>│
   │                   │                         │
```

---

## Funciones Principales

### 1. `obtener_planes_disponibles()`
Lee **dinámicamente** los planes desde MikroTik:

```python
from app.services.mikrotik import obtener_planes_disponibles

planes = obtener_planes_disponibles()
# Retorna: [
#   {"nombre": "1Dia", "validez": "1d", "precio": 1.0, ...},
#   {"nombre": "3Dias", "validez": "3d", "precio": 3.0, ...},
# ]
```

**¿Por qué es importante?**  
- No hay que actualizar Python si cambias los planes
- Los planes se administran en MikroTik Userman (WinBox)
- El bot siempre usa planes actualizados

---

### 2. `buscar_usuario_existente(usuario: str)`
Busca si un usuario ya existe:

```python
from app.services.mikrotik import buscar_usuario_existente

user = buscar_usuario_existente("ricky3")
if user:
    print(f"Usuario {user['nombre']} encontrado")
else:
    print("Usuario no existe")
```

---

### 3. `crear_usuario_userman(usuario, password, nombre_completo, plan=None)`
Crea un nuevo usuario:

```python
from app.services.mikrotik import crear_usuario_userman

exito, msg = crear_usuario_userman(
    usuario="ricky3",
    password="abc123",
    nombre_completo="Ricardo García",
    plan="1Dia"  # Plan de prueba
)

if exito:
    print(f"✅ {msg}")  # Usuario ricky3 creado con plan 1Dia
else:
    print(f"❌ {msg}")
```

**Nota**: Si `plan=None`, el usuario se crea sin plan (puede pagar después).

---

### 4. `actualizar_usuario_plan(usuario: str, nuevo_plan: str)`
Después que el admin aprueba el pago, actualiza el plan:

```python
from app.services.mikrotik import actualizar_usuario_plan

exito, msg = actualizar_usuario_plan("ricky3", "3Dias")

if exito:
    print(f"✅ {msg}")  # Plan actualizado a 3Dias
else:
    print(f"❌ {msg}")
```

---

## Integración en webhook_wa.py

El webhook ahora maneja el flujo completo:

```python
@router.post("/webhook")
async def receive_message_twilio(request: Request):
    # 1. Recibe mensaje de cliente
    # 2. Llama a procesar_texto() que detecta estado
    # 3. Si es nuevo: crea usuario con crear_usuario_userman()
    # 4. Si es existente: busca con buscar_usuario_existente()
    # 5. Espera comprobante (imagen)
    # 6. Después de pago: actualiza_usuario_plan()
```

---

## Estado del Cliente (En Memoria)

```python
CLIENTE_ESTADO = {
    "+51999999999": {
        "estado": "esperando_zona",  # inicio → esperando_tipo → esperando_nombre → ...
        "es_nuevo": True,
        "nombre": "Ricardo García",
        "usuario": "ricky3",
        "zona": "Centro",
        "plan_solicitado": "3dias",
    }
}
```

**Estados posibles**:
1. `inicio` - Primer contacto
2. `esperando_tipo` - Esperando si es nuevo o existente
3. `esperando_nombre` - (solo nuevos) Pide nombre
4. `esperando_usuario` - Pide usuario
5. `esperando_zona` - Pide zona
6. `esperando_plan` - Pide cuántos días
7. `pendiente_pago` - Esperando comprobante

---

## Ya NO Necesitas

❌ `app/services/planes.py` - **ELIMINADO**  
❌ `from app.services.planes import obtener_estado_cliente` - **NO NECESARIO**

---

## ¿Por Qué Esto es Mejor?

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Planes** | Hardcodeados en Python | Dinámicos desde MikroTik |
| **Mantenimiento** | Modificar código | Cambiar en WinBox |
| **Escalabilidad** | Limitado | Ilimitado |
| **Conexión Real** | Simulada | Real a MikroTik |

---

## Próximos Pasos

1. **Conectar MikroTik** (ver `GUIA_MIKROTIK_SETUP.md`)
2. **Crear planes en Userman**:
   - Accede a WinBox
   - Ve a `Tools → User Manager → Profiles`
   - Crea:
     - `1Dia` - 1 día - $1
     - `3Dias` - 3 días - $3
     - `1Semana` - 7 días - $7
     - `1Mes` - 30 días - $30
3. **Prueba el script**:
   ```bash
   python test_mikrotik_integration.py
   ```
4. **Verifica conexión** - Debe mostrar los planes creados

---

## Troubleshooting

### "MikroTik no accesible"
- Verificar IP en config
- Verificar puerto 8443
- Verificar firewall permite VPS

### "No hay planes (vacío)"
- Crear planes en WinBox (Tools → User Manager → Profiles)
- Verificar nombres: `1Dia`, `3Dias`, `1Semana`, `1Mes` (exactamente así)

### "Usuario creado pero sin plan"
- Plan no existe en MikroTik
- Crear el plan en WinBox
- Intentar de nuevo

---

## Integración Telegram (Admin Approval)

Cuando cliente envía comprobante:

```
Cliente: [FOTO del comprobante]
  ↓
Bot guarda en Supabase
  ↓
Telegram → Admin: "Nuevo pago de +51999999999 para 3 dias"
  ↓
Admin: /approve_51999999999_3dias
  ↓
Bot: actualizar_usuario_plan("usuario", "3Dias")
  ↓
Cliente: "¡Activado! Disfruta tus 3 días"
```

*Nota: El handler de Telegram approval aún se debe completar*

---

## Resumen de Cambios

| Archivo | Cambio |
|---------|--------|
| `mikrotik.py` | ✅ **Reescrito** - Funciones dinámicas |
| `webhook_wa.py` | ✅ **Reescrito** - Flujo de estados |
| `planes.py` | ❌ **ELIMINADO** - Ya no necesario |
| `chatgpt.py` | ✅ **Anterior** - Sigue igual |
| `supabase.py` | ✅ **Anterior** - Sigue igual |
