# tests/test_service.py
import pytest
import jwt
from datetime import datetime, timedelta
from starlette.testclient import TestClient

# On importe le service BentoML
from src.service import RFClassifierService, JWT_SECRET_KEY, JWT_ALGORITHM

# ============================================================
# SETUP : créer le client de test
# ============================================================

# TestClient simule des requêtes HTTP sans lancer un vrai serveur
client = TestClient(RFClassifierService.to_asgi())

# ============================================================
# HELPERS : fonctions utilitaires pour les tests
# ============================================================

def obtenir_token_valide():
    """Fait un vrai appel /login et retourne le token"""
    response = client.post("/login", json={
        "credentials": {
            "username": "user123",
            "password": "password123"
        }
    })
    return response.json()["token"]

def creer_token_expire():
    """Crée manuellement un token déjà expiré"""
    payload = {
        "sub": "user123",
        "exp": datetime.utcnow() - timedelta(hours=1)  # ← dans le passé !
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# Données de prédiction valides réutilisées dans plusieurs tests
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

# ============================================================
# TESTS 1 : Authentification JWT (on teste le MIDDLEWARE)
# ============================================================

def test_jwt_token_manquant():
    """Le middleware doit bloquer si aucun token n'est envoyé"""
    response = client.post("/predict", json=DONNEES_VALIDES)
    # On vérifie le code HTTP
    assert response.status_code == 401
    # On vérifie le message d'erreur précis
    assert response.json()["detail"] == "Missing authentication token"

def test_jwt_token_invalide():
    """Le middleware doit bloquer si le token est corrompu"""
    response = client.post("/predict",
        headers={"Authorization": "Bearer tokenbidon123abc"},
        json=DONNEES_VALIDES
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_jwt_token_expire():
    """Le middleware doit bloquer si le token est expiré"""
    token_expire = creer_token_expire()
    response = client.post("/predict",
        headers={"Authorization": f"Bearer {token_expire}"},
        json=DONNEES_VALIDES
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"

def test_jwt_format_bearer_incorrect():
    """Le middleware doit bloquer si le format Bearer est absent"""
    token = obtenir_token_valide()
    response = client.post("/predict",
        headers={"Authorization": token},  # ← manque "Bearer "
        json=DONNEES_VALIDES
    )
    assert response.status_code == 401

# ============================================================
# TESTS 2 : Endpoint /login (on teste la FONCTIONNALITÉ login)
# ============================================================

def test_login_credentials_valides():
    """Login avec bons identifiants doit retourner un token"""
    response = client.post("/login", json={
        "credentials": {
            "username": "user123",
            "password": "password123"
        }
    })
    assert response.status_code == 200
    # Le token doit être présent dans la réponse
    assert "token" in response.json()
    # Le token ne doit pas être vide
    assert len(response.json()["token"]) > 0

def test_login_mauvais_password():
    """Login avec mauvais mot de passe doit retourner 401"""
    response = client.post("/login", json={
        "credentials": {
            "username": "user123",
            "password": "mauvaispassword"
        }
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_utilisateur_inexistant():
    """Login avec utilisateur inconnu doit retourner 401"""
    response = client.post("/login", json={
        "credentials": {
            "username": "hackerXXX",
            "password": "password123"
        }
    })
    assert response.status_code == 401

# ============================================================
# TESTS 3 : Endpoint /predict (on teste la FONCTIONNALITÉ predict)
# ============================================================

def test_predict_sans_token():
    """/predict sans token doit retourner 401"""
    response = client.post("/predict", json=DONNEES_VALIDES)
    assert response.status_code == 401

def test_predict_avec_token_valide():
    """/predict avec token valide doit retourner une prédiction"""
    token = obtenir_token_valide()
    response = client.post("/predict",
        headers={"Authorization": f"Bearer {token}"},
        json=DONNEES_VALIDES
    )
    assert response.status_code == 200
    # La réponse doit contenir "prediction"
    assert "prediction" in response.json()
    # La prédiction doit être un nombre entre 0 et 1
    prediction = response.json()["prediction"][0]
    assert 0.0 <= prediction <= 1.0

def test_predict_donnees_manquantes():
    """/predict avec données incomplètes doit retourner 422"""
    token = obtenir_token_valide()
    response = client.post("/predict",
        headers={"Authorization": f"Bearer {token}"},
        json={"input_data": {"Serial_No": 1}}  # ← champs manquants
    )
    assert response.status_code == 422  # Unprocessable Entity