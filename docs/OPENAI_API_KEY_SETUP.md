# 🔑 CÓMO OBTENER API KEY DE OPENAI

## ⚠️ Error Actual
```
Error code: 401 - Incorrect API key provided: sk-sk-pr...
```

**Problema:** La API Key en tu `.env` es incorrecta o tiene formato inválido.

---

## ✅ Solución Paso a Paso

### 1. Crear Cuenta en OpenAI (si no tienes)
```
1. Ve a: https://platform.openai.com
2. Sign up (crear cuenta)
3. Verifica tu email
```

### 2. Agregar Método de Pago
```
⚠️  CRÍTICO: OpenAI requiere cuenta PAGADA para usar API

1. Ve a: https://platform.openai.com/account/billing/overview
2. Click "Add payment method"
3. Agrega tarjeta de crédito/débito
4. Agrega crédito inicial (mínimo $5 USD)
```

**Sin método de pago = API no funciona** ❌

### 3. Crear API Key
```
1. Ve a: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Dale un nombre: "Bot ISP"
4. Click "Create secret key"
5. COPIA LA KEY (se verá así):
   
   sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   o
   
   sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

⚠️  IMPORTANTE: Cópiala AHORA, no la podrás ver de nuevo
```

### 4. Actualizar `.env`
```bash
# Abre tu archivo .env
# Busca la línea:
OPENAI_API_KEY=sk-sk-pr...

# Reemplázala con tu nueva key:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Reiniciar el bot
```bash
# Detener el servidor (Ctrl+C)
# Iniciar de nuevo:
python main.py
```

---

## 🔍 Verificar que funciona

### Opción 1: Test rápido en Python
```python
from openai import OpenAI

client = OpenAI(api_key="sk-proj-tu_key_aqui")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hola"}]
)

print(response.choices[0].message.content)
# Debe imprimir: respuesta de ChatGPT ✅
```

### Opción 2: Test desde WhatsApp
```
1. Asegúrate de que el bot esté corriendo (python main.py)
2. Envía mensaje a WhatsApp: "Hola"
3. Deberías recibir respuesta de ChatGPT ✅
```

---

## 💰 Costos

### gpt-3.5-turbo (RECOMENDADO)
- **Input:** $0.0005 por 1K tokens (~750 palabras)
- **Output:** $0.0015 por 1K tokens
- **Para este bot:** ~$0.50-2 USD/mes (bajo volumen)

### gpt-4 (MÁS CARO)
- **Input:** $0.03 por 1K tokens
- **Output:** $0.06 por 1K tokens
- **Para este bot:** ~$10-30 USD/mes

**Recomendación:** Usar `gpt-3.5-turbo` (es suficiente y muy barato)

---

## 🐛 Troubleshooting

### Error: "Incorrect API key"
```
Causa: Key incorrecta o formato inválido
Solución: Crear nueva key en OpenAI dashboard
```

### Error: "You exceeded your current quota"
```
Causa: No tienes crédito en tu cuenta
Solución: Agregar más crédito en Billing
```

### Error: "Rate limit exceeded"
```
Causa: Demasiadas solicitudes
Solución: Esperar 1 minuto y reintentar
```

### Error: "Invalid request"
```
Causa: Código mal configurado
Solución: Verificar que chatgpt.py usa API v1.0+
```

---

## 📋 Checklist

- [ ] Cuenta creada en OpenAI
- [ ] Método de pago agregado
- [ ] Crédito inicial agregado ($5 USD mínimo)
- [ ] API Key creada
- [ ] API Key copiada
- [ ] `.env` actualizado con nueva key
- [ ] Bot reiniciado
- [ ] Test exitoso (Python o WhatsApp)

---

## 🔗 Links Útiles

- **Dashboard:** https://platform.openai.com
- **API Keys:** https://platform.openai.com/api-keys
- **Billing:** https://platform.openai.com/account/billing/overview
- **Pricing:** https://openai.com/pricing
- **Docs:** https://platform.openai.com/docs/api-reference

---

## ⚡ Alternativa GRATIS (si no quieres pagar)

Si no quieres pagar OpenAI, puedes:

1. **Usar Ollama (local, gratis):**
   - Instalar Ollama: https://ollama.ai
   - Ejecutar modelo local: `ollama run llama2`
   - Modificar `chatgpt.py` para usar Ollama API

2. **Usar respuestas predefinidas:**
   - Crear diccionario de respuestas
   - Sin IA, pero funcional

3. **Esperar a que Gemini permita compras:**
   - Revisar Google Gemini periódicamente
   - Restaurar código de `gemini.py.bak`

---

**Próximo paso:** Obtener API Key válida de OpenAI y actualizar `.env` 🔑
