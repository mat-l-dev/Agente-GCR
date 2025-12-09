"""
Script para simular un clic en el botón de Telegram
"""
import json
import requests

# Este es el JSON que Telegram envía cuando clickeas un botón inline
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
        "data": "aprobar_7",  # ← Este es el callback_data del botón
        "inline_message_id": "123"
    }
}

print("\n📨 Simulando clic en botón APROBAR de Telegram")
print(f"   Enviando: {json.dumps(callback_query, indent=2)}")

response = requests.post(
    "http://localhost:8000/telegram",
    json=callback_query,
    timeout=10
)

print(f"\n   Status: {response.status_code}")
print(f"   Response: {response.text}")
