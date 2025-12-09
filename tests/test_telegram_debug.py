"""
Test más detallado para debugging del webhook de Telegram
"""
import json
import traceback
import requests

callback_query = {
    "update_id": 123456789,
    "callback_query": {
        "id": "5555555555555555555",
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Admin",
            "username": "admin_user",
            "language_code": "es"
        },
        "chat_instance": "1234567890123456",
        "data": "aprobar_7",
        "inline_message_id": "123"
    }
}

print("\n📨 Simulando clic en botón APROBAR de Telegram\n")

try:
    response = requests.post(
        "http://localhost:8000/telegram",
        json=callback_query,
        timeout=5
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print(f"\n❌ Error! Status code: {response.status_code}")
    else:
        try:
            data = response.json()
            print(f"\n✅ Respuesta JSON: {json.dumps(data, indent=2)}")
            
            if data.get("status") == "error":
                print(f"\n⚠️ El servidor devolvió un error:")
                print(f"  Mensaje: {data.get('message')}")
                print(f"\nVerifica que el webhook fue recargado correctamente")
        except:
            print(f"No se pudo parsear como JSON")
            
except requests.exceptions.ConnectionError:
    print("❌ No se pudo conectar al servidor en localhost:8000")
    print("Asegúrate de que uvicorn esté ejecutándose")
except requests.exceptions.Timeout:
    print("❌ El servidor tardó demasiado en responder (timeout)")
except Exception as ex:
    print(f"❌ Error: {ex}")
    traceback.print_exc()
