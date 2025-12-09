"""
Script de prueba para simular mensajes de Twilio localmente
Útil para probar sin necesidad de enviar mensajes reales desde WhatsApp
"""

import requests

# URL de tu servidor local
BASE_URL = "http://localhost:8000"

def test_webhook_get():
    """Prueba el endpoint GET del webhook"""
    print("\n" + "="*60)
    print("🧪 TEST 1: GET /webhook (Verificación)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/webhook")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Endpoint GET funcionando\n")

def test_mensaje_texto():
    """Simula un mensaje de texto desde Twilio"""
    print("\n" + "="*60)
    print("🧪 TEST 2: POST /webhook - Mensaje de texto")
    print("="*60)
    
    data = {
        "From": "whatsapp:+51999888777",
        "Body": "Hola, quiero información sobre planes de internet",
        "NumMedia": "0"
    }
    
    response = requests.post(f"{BASE_URL}/webhook", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Mensaje de texto procesado\n")

def test_mensaje_imagen():
    """Simula un mensaje con imagen (comprobante de pago)"""
    print("\n" + "="*60)
    print("🧪 TEST 3: POST /webhook - Mensaje con imagen")
    print("="*60)
    
    data = {
        "From": "whatsapp:+51999888777",
        "Body": "",
        "NumMedia": "1",
        "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/AC.../Messages/MM.../Media/ME..."
    }
    
    response = requests.post(f"{BASE_URL}/webhook", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Mensaje con imagen procesado\n")

def test_home():
    """Prueba el endpoint principal"""
    print("\n" + "="*60)
    print("🧪 TEST 0: GET / (Home)")
    print("="*60)
    
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Servidor funcionando\n")

if __name__ == "__main__":
    print("\n🚀 INICIANDO SUITE DE PRUEBAS")
    print("Asegúrate de que el servidor esté corriendo: uvicorn main:app --reload")
    input("Presiona ENTER para continuar...")
    
    try:
        test_home()
        test_webhook_get()
        
        print("\n⚠️  Los siguientes tests intentarán enviar mensajes reales:")
        print("- Llamarán a ChatGPT (OpenAI API)")
        print("- Intentarán guardar en Supabase")
        print("- Enviarán alertas a Telegram")
        
        continuar = input("\n¿Continuar con las pruebas completas? (s/n): ")
        
        if continuar.lower() == 's':
            test_mensaje_texto()
            
            print("\n⚠️  El siguiente test guardará datos en Supabase")
            continuar2 = input("¿Probar mensaje con imagen? (s/n): ")
            if continuar2.lower() == 's':
                test_mensaje_imagen()
        
        print("\n" + "="*60)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor")
        print("Asegúrate de ejecutar: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
