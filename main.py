from fastapi import FastAPI
from app.routers import webhook_wa, webhook_tg

app = FastAPI(title="Bot ISP v1.0")

# Incluimos los routers (las "rutas" separadas)
app.include_router(webhook_wa.router)
app.include_router(webhook_tg.router)

@app.get("/")
def home():
    return {"status": "Sistema Operativo y Modularizado 🚀"}

if __name__ == "__main__":
    import uvicorn
    # Importante: Si estás en producción usa host="0.0.0.0"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)