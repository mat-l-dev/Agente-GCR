# ==========================================
# Script de inicio del Bot ISP
# ==========================================

Write-Host ""
Write-Host "🚀 BOT ISP - Sistema de Automatización" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: Ejecuta este script desde la carpeta bot_isp" -ForegroundColor Red
    exit 1
}

# Verificar archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: No se encontró el archivo .env" -ForegroundColor Red
    Write-Host "📝 Copia .env.example a .env y configura las variables" -ForegroundColor Yellow
    exit 1
}

# Activar entorno virtual si existe
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🔄 Activando entorno virtual..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  No se encontró entorno virtual (.venv)" -ForegroundColor Yellow
    $crear = Read-Host "¿Deseas crearlo ahora? (s/n)"
    if ($crear -eq "s") {
        Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
        python -m venv .venv
        & .venv\Scripts\Activate.ps1
        Write-Host "📥 Instalando dependencias..." -ForegroundColor Yellow
        pip install -r requirements.txt
    } else {
        exit 1
    }
}

# Menú de opciones
Write-Host ""
Write-Host "Selecciona una opción:" -ForegroundColor Cyan
Write-Host "1. 🧪 Verificar sistema"
Write-Host "2. 🚀 Iniciar servidor (localhost)"
Write-Host "3. 🌐 Iniciar servidor + ngrok"
Write-Host "4. 🧪 Ejecutar tests"
Write-Host "5. ❌ Salir"
Write-Host ""

$opcion = Read-Host "Opción"

switch ($opcion) {
    "1" {
        Write-Host ""
        Write-Host "🔍 Verificando sistema..." -ForegroundColor Yellow
        python verificar_sistema.py
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 Iniciando servidor en http://localhost:8000" -ForegroundColor Green
        Write-Host "Presiona CTRL+C para detener" -ForegroundColor Yellow
        Write-Host ""
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    }
    "3" {
        Write-Host ""
        Write-Host "🌐 Iniciando sistema completo..." -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 INSTRUCCIONES:" -ForegroundColor Cyan
        Write-Host "1. El servidor se iniciará en este terminal"
        Write-Host "2. Abre OTRA terminal y ejecuta: ngrok http 8000"
        Write-Host "3. Copia la URL de ngrok (https://xxx.ngrok.io)"
        Write-Host "4. Configúrala en Twilio Console"
        Write-Host ""
        Write-Host "Presiona CTRL+C para detener" -ForegroundColor Yellow
        Write-Host ""
        Start-Sleep -Seconds 2
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    }
    "4" {
        Write-Host ""
        Write-Host "🧪 Ejecutando tests..." -ForegroundColor Yellow
        Write-Host "Asegúrate de que el servidor esté corriendo en otra terminal" -ForegroundColor Yellow
        Write-Host ""
        python test_webhook.py
    }
    "5" {
        Write-Host "👋 Hasta luego!" -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "❌ Opción inválida" -ForegroundColor Red
        exit 1
    }
}
