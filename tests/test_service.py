# tests/test_service.py
import pytest
import jwt
import time
import subprocess
import requests
from datetime import datetime, timedelta

from src.service import JWT_SECRET_KEY, JWT_ALGORITHM

# ============================================================
# SETUP : démarrer un vrai serveur BentoML pour les tests
# ============================================================

BASE_URL = "http://127.0.0.1:3099"  # port unique pour les tests

@pytest.fixture(scope="session", autouse=True)
def serveur_bentoml():
    """Démarre le serveur BentoML avant tous les tests, l'arrête après"""
    # Démarrer le serveur en arrière-plan
    process = subprocess.Popen(
        ["uv", "run", "bentoml", "serve", "src.service:RFClassifierService", "--port", "3099"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Attendre que le serveur soit prêt
    for _ in range(30):
        try:
            requests.get(f"{BASE_URL}/healthz", timeout=1)
            break
        except Exception:
            time.sleep(1)
    
    yield  # ← les tests s'exécutent ici
    
    # Arrêter le serveur après tous les tests
    process.terminate()
    process.wait()

# ============================================================
# HELPERS
# ============================================================

def obtenir_token_valide():
    response = requests.post(f"{BASE_URL}/login", json={
        "credentials": {"username": "user123", "password": "password123"}
    })
    return response.json()["token"]

def creer_token_expire():
    payload = {
        "sub": "user123",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

DONNEES_VALIDES = {
    "input_data": {
        "Serial_No": 1,
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 8.5,
        "Research": 1
    }
}

DONNEES_INVALIDES = {
    "input_data": {
        "Serial_No": 1,
        "GRE_Score": "pas_un_nombre",
        "TOEFL_Score": 110,
        "University_Rating": 1,
        "SOP": 4.5,
        "LOR": 4.0,
        "CGPA": 8.5,
        "Research": 1
    }
}

DONNEES_INCOMPLETES = {
    "input_data": {
        "Serial_No": 1,
        "GRE_Score": "pas_un_nombre",
        "TOEFL_Score": 110,
        "University_Rating": 1
    }
}

# ============================================================
# TESTS 1 : Authentification JWT
# ============================================================

def test_jwt_token_manquant():
    response = requests.post(f"{BASE_URL}/predict", json=DONNEES_VALIDES)
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication token"

def test_jwt_token_invalide():
    response = requests.post(f"{BASE_URL}/predict",
        headers={"Authorization": "Bearer tokenbidon123"},
        json=DONNEES_VALIDES
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_jwt_token_expire():
    token_expire = creer_token_expire()
    response = requests.post(f"{BASE_URL}/predict",
        headers={"Authorization": f"Bearer {token_expire}"},
        json=DONNEES_VALIDES
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"

# ============================================================
# TESTS 2 : Endpoint /login
# ============================================================

def test_login_credentials_valides():
    response = requests.post(f"{BASE_URL}/login", json={
        "credentials": {"username": "user123", "password": "password123"}
    })
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_mauvais_password():
    response = requests.post(f"{BASE_URL}/login", json={
        "credentials": {"username": "user123", "password": "mauvaispassword"}
    })
    assert response.status_code == 401

def test_login_utilisateur_inexistant():
    response = requests.post(f"{BASE_URL}/login", json={
        "credentials": {"username": "hackerXXX", "password": "password123"}
    })
    assert response.status_code == 401

# ============================================================
# TESTS 3 : Endpoint /predict
# ============================================================

def test_predict_sans_token():
    response = requests.post(f"{BASE_URL}/predict", json=DONNEES_VALIDES)
    assert response.status_code == 401

def test_predict_avec_token_valide():
    token = obtenir_token_valide()
    response = requests.post(f"{BASE_URL}/predict",
        headers={"Authorization": f"Bearer {token}"},
        json=DONNEES_VALIDES
    )
    assert response.status_code == 200
    assert "prediction" in response.json()
    prediction = response.json()["prediction"][0]
    assert 0.0 <= prediction <= 1.0

def test_predict_donnees_manquantes():
    token = obtenir_token_valide()
    response = requests.post(f"{BASE_URL}/predict",
        headers={"Authorization": f"Bearer {token}"},
        json=DONNEES_INCOMPLETES
    )
    assert response.status_code == 400
    
def test_predict_donnees_invalides():
    token = obtenir_token_valide()
    response = requests.post(f"{BASE_URL}/predict",
        headers={"Authorization": f"Bearer {token}"},
        json=DONNEES_INVALIDES
    )
    assert response.status_code == 400