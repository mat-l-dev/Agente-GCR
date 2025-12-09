# 🎯 CONFIGURACIÓN DE PLANES EN MIKROTIK USERMAN

## ⚠️ IMPORTANTE

El código en `app/services/mikrotik.py` usa los siguientes nombres de planes:
- `1Dia` - Plan de 1 día
- `3Dias` - Plan de 3 días (bono de bienvenida)
- `1Semana` - Plan de 7 días
- `1Mes` - Plan de 30 días

**Debes crear estos planes en tu MikroTik Userman ANTES de que el bot funcione.**

---

## 📋 Cómo Crear Planes en Userman (WinBox)

### Paso 1: Abrir Userman

1. Conectar a MikroTik con WinBox
2. Click en **`User Manager`** (menú lateral)

---

### Paso 2: Crear Perfil (Profile)

1. Ir a **`Profiles`** tab
2. Click **`Add New`** (+)

3. **Configurar perfil para 1 día:**
   ```
   Name: 1Dia
   Name for Users: Plan 1 Día
   Price: 1.00
   Validity: 1d 00:00:00
   
   Session Timeout: none
   Idle Timeout: none
   
   Rate Limit (RX/TX): 1M/1M  (ajusta según tu velocidad)
   
   Shared Users: 1  (dispositivos simultáneos)
   ```

4. Click **`OK`**

5. **Repetir para otros planes:**

   **Plan 3 Días (Bono):**
   ```
   Name: 3Dias
   Validity: 3d 00:00:00
   Rate Limit: 1M/1M
   ```

   **Plan 1 Semana:**
   ```
   Name: 1Semana
   Validity: 7d 00:00:00
   Rate Limit: 1M/1M
   ```

   **Plan 1 Mes:**
   ```
   Name: 1Mes
   Validity: 30d 00:00:00
   Rate Limit: 1M/1M
   ```

---

### Paso 3: Verificar Planes

1. Ir a **`Profiles`** tab
2. Deberías ver:
   - ✅ 1Dia
   - ✅ 3Dias
   - ✅ 1Semana
   - ✅ 1Mes

---

## 🔧 Ajustar Nombres en el Código (Opcional)

Si tus planes tienen nombres diferentes, edita `app/services/mikrotik.py`:

```python
# Línea ~85-95 en mikrotik.py

if dias == 1:
    plan_name = "TU_PLAN_1DIA"  # Cambia aquí
elif dias == 3:
    plan_name = "TU_PLAN_3DIAS"  # Cambia aquí
elif dias == 7:
    plan_name = "TU_PLAN_1SEMANA"  # Cambia aquí
elif dias == 30:
    plan_name = "TU_PLAN_1MES"  # Cambia aquí
```

---

## 🧪 Probar Creación Manual

Antes de usar el bot, prueba crear un usuario manualmente:

### En WinBox (Userman):

1. Ir a **`Users`** tab
2. Click **`Add New`**
3. **Configurar:**
   ```
   Username: testuser
   Password: 123456
   Profile: 1Dia
   Comment: Prueba manual
   ```
4. Click **`OK`**

### Verificar en Radius:

1. Ir a **`Radius`** (menú principal)
2. Debería aparecer `testuser` si Radius está activo

---

## 📊 Estructura Completa de Userman

```
User Manager
├── Routers (tu MikroTik local)
├── Profiles (planes: 1Dia, 3Dias, etc)
├── Users (clientes creados)
├── Sessions (conexiones activas)
└── Limitations (opcional: límites adicionales)
```

---

## ❓ Troubleshooting

### Error: "Profile not found"

**Causa:** El plan no existe en Userman

**Solución:**
1. Ve a Userman > Profiles
2. Crea el plan faltante
3. O ajusta el nombre en `mikrotik.py`

---

### Usuario creado pero no puede conectar

**Causa:** Radius no está activo

**Solución:**
1. Ir a **`Radius`**
2. Verificar que tu router esté en la lista
3. Status debe ser "Online"
4. Si no aparece:
   ```
   IP > Hotspot > Server Profiles
   Click en tu perfil → Tab "RADIUS"
   Use RADIUS: yes
   ```

---

### Usuario expira antes de tiempo

**Causa:** Validity mal configurado en el perfil

**Solución:**
1. Userman > Profiles > [tu plan]
2. Verificar campo **`Validity`**
3. Formato: `1d 00:00:00` (días horas:mins:segs)

---

## 🎉 Listo!

Una vez creados los planes, el bot podrá:
1. Crear usuarios automáticamente
2. Asignarles el plan correcto según días
3. Los usuarios se conectarán via Radius
4. Expirarán automáticamente según el plan

**Prueba final:** Ejecuta el bot y envía mensaje por WhatsApp para que cree un usuario.
