import requests

BASE_URL = "http://127.0.0.1:8000"

USERNAME = "neuer_testuser"
PASSWORD = "geheimespasswort"

# 1. Registrierung
print("--- Schritt 1: Registrierung ---")

register_response = requests.post(
    f"{BASE_URL}/users/",
    json={
        "username": USERNAME,
        "password": PASSWORD
    }
)

print("Status Code Registrierung:", register_response.status_code)

try:
    print("Registrierung Response:", register_response.json())
except Exception:
    print("Registrierung Response konnte nicht als JSON gelesen werden.")
    print(register_response.text)


# 2. Login / Token holen
print("\n--- Schritt 2: Login & Token Request ---")

login_data = {
    "username": USERNAME,
    "password": PASSWORD
}

token_response = requests.post(
    f"{BASE_URL}/token",
    data=login_data
)

print("Status Code Token Request:", token_response.status_code)

try:
    token_json = token_response.json()
    print("Token Response:", token_json)
except Exception:
    print("Token Response konnte nicht als JSON gelesen werden.")
    print(token_response.text)
    token_json = {}

token = token_json.get("access_token")

if not token:
    print("\nFEHLER: Kein Token erhalten. Login war nicht erfolgreich.")
    exit()


# 3. Produkte mit Token abrufen
print("\n--- Schritt 3: Produkte abrufen ---")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

get_response = requests.get(
    f"{BASE_URL}/products",
    headers=headers
)

print("Status Code Produkte:", get_response.status_code)

try:
    print("Produkte Liste:", get_response.json())
except Exception:
    print("Produktliste konnte nicht als JSON gelesen werden.")
    print(get_response.text)