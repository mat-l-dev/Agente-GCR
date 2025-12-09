# Flujo Completo de Activación - Diagrama y Ejemplo

## 1. Mensaje → Texto

```
Cliente: "Hola, quiero internet"
        ↓
webhook_wa.py recibe mensaje
        ↓
procesar_texto(numero, "Hola, quiero internet")
        ↓
Estado: "inicio" → "esperando_tipo"
plan_solicitado: None (aún no menciona días)
        ↓
Bot: "👋 Hola! ¿Eres usuario nuevo o ya tienes cuenta?"
```

---

## 2. Cliente elige tipo

```
Cliente: "Soy nuevo"
        ↓
procesar_texto(numero, "Soy nuevo")
        ↓
Estado: "esperando_tipo" → "esperando_nombre"
es_nuevo: True
        ↓
Bot: "📝 OK, eres nuevo. ¿Cuál es tu nombre completo?"
```

---

## 3. Cliente proporciona nombre

```
Cliente: "Ricardo García"
        ↓
procesar_texto(numero, "Ricardo García")
        ↓
Estado: "esperando_nombre" → "esperando_usuario"
nombre: "Ricardo García"
        ↓
Bot: "👤 Gracias. ¿Cuál va a ser tu usuario? (ej: ricky3)"
```

---

## 4. Cliente proporciona usuario

```
Cliente: "ricky3"
        ↓
procesar_texto(numero, "ricky3")
        ↓
Estado: "esperando_usuario" → "esperando_zona"
usuario: "ricky3"
        ↓
Bot: "📍 ¿De qué zona eres? (Centro, Goza, Cocha, etc)"
```

---

## 5. Cliente proporciona zona

```
Cliente: "Centro"
        ↓
procesar_texto(numero, "Centro")
        ↓
Estado: "esperando_zona" → "esperando_plan"
zona: "Centro"
plan_solicitado: None (aún no preguntó por días)
        ↓
Bot: "📅 ¿Cuántos días quieres? (1 dia, 3 dias, 1 semana, 1 mes)"
```

---

## 6. Cliente solicita plan

```
Cliente: "3 dias"
        ↓
detectar_plan_del_mensaje("3 dias") → "3dias"
        ↓
plan_solicitado: "3dias"
Estado: "esperando_plan" → crear_o_buscar_usuario()
        ↓
ES NUEVO → crear_usuario_userman()
        ↓
obtener_planes_disponibles() 
  ↓ MikroTik
  ↓ /tool/user-manager/profile
  ← [1Dia, 3Dias, 1Semana, 1Mes]
        ↓
crear usuario en MikroTik:
  • usuario: "ricky3"
  • password: "abc123" (aleatorio)
  • nombre_completo: "Ricardo García"
  • plan: "3Dias" (BONO GRATIS)
        ↓
Estado: "esperando_plan" → "inicio" (reset)
        ↓
Bot: "✅ ¡Bienvenido! Usuario creado con 3 días gratis
     👤 Usuario: ricky3
     🔑 Contraseña: abc123
     🎁 Plan: 3Dias (prueba gratis)
     
     Conéctate y disfruta! Cuando se acaben los días, escríbeme para recargar."
```

---

## 7. Cliente envía comprobante (imagen)

```
Cliente: [FOTO DEL COMPROBANTE]
        ↓
webhook_wa.py detecta num_media > 0
        ↓
guardar_venta_pendiente(numero, "3dias", media_url)
  ↓ Supabase
  ↓ INSERT INTO ventas_pendientes
  ← venta_id
        ↓
enviar_alerta_pago(venta_id, numero, "3dias", media_url)
  ↓ Telegram Bot API
  ↓ "Nuevo pago de +51999999999"
  ↓ "Plan: 3dias"
  ↓ [FOTO del comprobante]
        ↓
Bot al cliente: "✅ Comprobante recibido. Un agente lo validará en breve. Gracias!"
        ↓
ESPERA APROBACIÓN DEL ADMIN
```

---

## 8. Admin aprueba en Telegram

```
Admin: "Veo el pago de +51999999999"
Admin: /approve_51999999999_3dias
        ↓
Telegram webhook recibe comando
        ↓
handler_telegram_approval()
  • numero: "+51999999999"
  • plan: "3dias" → "3Dias" (nombre en MikroTik)
  • usuario: "ricky3" (buscado de Supabase)
        ↓
actualizar_usuario_plan("ricky3", "3Dias")
  ↓ MikroTik API
  ↓ SET /tool/user-manager/user[name="ricky3"] profile="3Dias"
  ← OK
        ↓
enviar_mensaje_whatsapp(numero, "✅ ¡Activado!")
"Tu plan de 3 días está activo.
Usuario: ricky3
Contraseña: abc123
Disfruta tu conexión!")
```

---

## 9. Cliente se conecta a Internet

```
Cliente conecta a MikroTik Hotspot
        ↓
ricky3 / abc123
        ↓
MikroTik Radius verifica en Userman
        ↓
Usuario ricky3 existe + plan 3Dias asignado
        ↓
✅ CONECTADO 🎉
```

---

## Variables de CLIENTE_ESTADO en cada etapa

### Etapa 1: Inicio
```python
CLIENTE_ESTADO["+51999999999"] = {
    "estado": "inicio",
    "es_nuevo": None,
    "nombre": None,
    "usuario": None,
    "zona": None,
    "plan_solicitado": None,
}
```

### Etapa 2: Nuevo
```python
{
    "estado": "esperando_tipo",
    "es_nuevo": True,
    "nombre": None,
    "usuario": None,
    "zona": None,
    "plan_solicitado": None,
}
```

### Etapa 3: Datos completos
```python
{
    "estado": "esperando_plan",
    "es_nuevo": True,
    "nombre": "Ricardo García",
    "usuario": "ricky3",
    "zona": "Centro",
    "plan_solicitado": None,
}
```

### Etapa 4: Solicita plan
```python
{
    "estado": "pendiente_pago",
    "es_nuevo": True,
    "nombre": "Ricardo García",
    "usuario": "ricky3",
    "zona": "Centro",
    "plan_solicitado": "3dias",
}
```

---

## Si cliente es EXISTENTE

```
Cliente: "Tengo cuenta"
        ↓
Estado: "esperando_tipo" → "esperando_usuario"
es_nuevo: False
        ↓
Bot: "🔍 OK, ya tienes cuenta. ¿Cuál es tu usuario?"
        ↓
Cliente: "ricky3"
        ↓
Estado: "esperando_usuario" → "esperando_zona"
usuario: "ricky3"
        ↓
Bot: "📍 ¿De qué zona eres?"
        ↓
Cliente: "Centro"
        ↓
Estado: "esperando_zona" → crear_o_buscar_usuario()
        ↓
ES EXISTENTE → buscar_usuario_existente("ricky3")
  ↓ MikroTik
  ↓ GET /tool/user-manager/user[name="ricky3"]
  ← {"nombre": "ricky3", "disabled": "no", "comment": "Bot: Ricardo García"}
        ↓
Bot: "✅ Usuario encontrado!
     👤 Usuario: ricky3
     Zona: Centro
     
     💰 Envía comprobante de pago para 3 dias."
        ↓
Estado: "pendiente_pago"
(igual al flujo anterior, espera comprobante)
```

---

## Tabla de estados

| Estado | Sig. Etapa | Si es Nuevo | Si es Existente |
|--------|-----------|------------|-----------------|
| `inicio` | `esperando_tipo` | - | - |
| `esperando_tipo` | `esperando_nombre` O `esperando_usuario` | ✓ | ✓ |
| `esperando_nombre` | `esperando_usuario` | ✓ | - |
| `esperando_usuario` | `esperando_zona` | ✓ | ✓ |
| `esperando_zona` | `esperando_plan` O `crear_usuario()` | ✓ | ✓ |
| `esperando_plan` | `crear_usuario()` | ✓ | - |
| `pendiente_pago` | `actualizar_plan()` (por admin) | ✓ | ✓ |

---

## Resumen de APIs MikroTik usadas

| Función | Ruta MikroTik | Acción |
|---------|---------------|--------|
| `obtener_planes_disponibles()` | `/tool/user-manager/profile` | GET |
| `crear_usuario_userman()` | `/tool/user-manager/user` | ADD |
| `buscar_usuario_existente()` | `/tool/user-manager/user` | GET + FILTER |
| `actualizar_usuario_plan()` | `/tool/user-manager/user` | SET profile |

---

## Resumen de Servicios usados

| Servicio | Función | Momento |
|----------|---------|---------|
| `mikrotik.py` | Crear/buscar/actualizar usuarios | Después de datos |
| `supabase.py` | Guardar venta pendiente | Cuando envía comprobante |
| `telegram.py` | Alerta al admin | Cuando envía comprobante |
| `whatsapp.py` | Enviar respuestas | Cada etapa |
| `chatgpt.py` | (OPCIONAL) Respuestas inteligentes | Podría usarse para responder preguntas |

---

## Error Handling

### Si MikroTik no está disponible
```
obtener_planes_disponibles() → []
Bot: "❌ No puedo conectar con MikroTik. Intenta más tarde."
Estado: Vuelve a "pendiente_pago" (re-intenta)
```

### Si usuario ya existe
```
crear_usuario_userman("ricky3", ...) → Exception
Bot: "❌ El usuario 'ricky3' ya existe. ¿Quizá tienes otra cuenta?"
```

### Si plan no existe
```
crear_usuario_userman(..., plan="5Dias") → 
  "Usuario creado (plan pendiente)" (sin asignar plan)
Bot: "⚠️ Plan no existe en MikroTik"
```

---

## Notas Importantes

1. **Plan de Trial**: Siempre se crea con `plan="1Dia"` (gratis 1 día para probar)
2. **Plan Real**: Se asigna DESPUÉS del pago aprobado por admin
3. **Estado en Memoria**: Si el bot se reinicia, se pierden los estados
   - **TODO**: Guardar estados en Supabase para persistencia
4. **Nombre de Planes**: DEBE ser exacto en MikroTik
   - `1Dia`, `3Dias`, `1Semana`, `1Mes` (mayúsculas exactas)
