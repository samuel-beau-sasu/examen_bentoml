# Examen BentoML

Ce repertoire contient l'architecture basique afin de rendre l'évaluation pour l'examen BentoML.

Vous êtes libres d'ajouter d'autres dossiers ou fichiers si vous jugez utile de le faire.

Voici comment est construit le dossier de rendu de l'examen:

```bash       
├── examen_bentoml          
│   ├── data       
│   │   ├── processed      
│   │   └── raw           
│   ├── models      
│   ├── src       
│   └── README.md
```

Afin de pouvoir commencer le projet vous devez suivre les étapes suivantes:

- Forker le projet sur votre compte github

- Cloner le projet sur votre machine

- Récuperer le jeu de données à partir du lien suivant: [Lien de téléchargement]( https://datascientest.s3-eu-west-1.amazonaws.com/examen_bentoml/admissions.csv)


Bon travail!

# 1.1. Préparation de l'environnement de travail
curl -O https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

uv init 

### Création de l'environnement virtuel

uv venv .venv
source .venv/bin/activate

# 1.2. Création du modèle

uv pip install pandas numpy scikit-learn bentoml PyJWT
uv pip install pytest
uv add pytest
uv add pydantic==2.11.7

uv add pytest --dev
uv add requests

uv remove pytest

## création du requirements.txt
python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))" > requirements.txt

# 


mv /Users/samuelbeau/Atelier/Datascientest/BentoML/BentoML_exam/bentoml/* ~/bentoml/

export BENTOML_HOME="/Users/samuelbeau/Atelier/Datascientest/BentoML/BentoML_exam/bentoml"

# 1.3. Mise en place de l'API de prédiction



PORT ?= 3001
SERVICE ?= src.service:RFClassifierService
http://127.0.0.1:3001

uv run bentoml serve src.service:RFClassifierService --port 3001

"user123": "password123",
"user456": "password456",

curl -s -X POST "http://127.0.0.1:3001/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTg4NzU5fQ.5hPU6qU9ZVV4202dgvpWK6RVv_PORjT0m3GJUxRoBNU" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo


# 1.4. Création d'un bento & conteneurisation avec Docker

#créer un Bento contenant notre modèle entraîné
uv run bentoml build

bentoml list
 Tag                                     Size       Model Size  Creation Time       
 rf_classifier_service:6izqvfan4cebilio  46.10 KiB  77.36 KiB   2026-02-19 23:18:41 

#Création de l'image Docker
bentoml containerize rf_classifier_service:yhdchzan4kt4dt4s

# 1.5 Tester/run l'image Docker

docker run --rm -p 3000:3000 rf_classifier_service:yhdchzan4kt4dt4s

http://127.0.0.1:3000

# Test curl

curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTQ0MjM1fQ._cfMq0jIoAFJEam37jqFFmzvxKNHeH3w2V1u6_f2ICM" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo

# 1.5. Tests unitaires

## Test de l'authentification JWT :
### Vérifiez que l'authentification échoue si le jeton JWT est manquant ou invalide.

curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9._cfMq0jIoAFJEam37jqFFmzvxKNHeH3w2V1u6_f2ICM" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo

### Vérifiez que l'authentification échoue si le jeton JWT a expiré.

curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTQ0MjM1fQ._cfMq0jIoAFJEam37jqFFmzvxKNHeH3w2V1u6_f2ICM" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo

### Vérifiez que l'authentification réussit avec un jeton JWT valide.

curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTg4NzU5fQ.5hPU6qU9ZVV4202dgvpWK6RVv_PORjT0m3GJUxRoBNU" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo

## Test de l'API de connexion :
### Vérifiez que l'API renvoie un jeton JWT valide pour des identifiants utilisateur corrects.

curl -X 'POST' \
  'http://127.0.0.1:3000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "credentials": {
    "username": "user123",
    "password": "password123"
  }
}'

### Vérifiez que l'API renvoie une erreur 401 pour des identifiants utilisateur incorrects.

curl -X 'POST' \
  'http://127.0.0.1:3000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "credentials": {
    "username": "userXXX",
    "password": "password123"
  }
}'

## Test de l'API de prédiction :
### Vérifiez que l'API renvoie une erreur 401 si le jeton JWT est manquant ou invalide.

curl -s -X POST "http://127.0.0.1:3001/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTg4NzU5fQ.5hPU6qU9ZVV4202dgvpWK6RVv_PORjT0m3GJUxRoBNU" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": A+, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo


### Vérifiez que l'API renvoie une prédiction valide pour des données d'entrée correctes.

curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTgxMTg0fQ.-8gIwEFbC2eslCpyRQM0i3gzzqnbyqUopdP0EjE7TI0" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo

### Vérifiez que l'API renvoie une erreur pour des données d'entrée invalides.

curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNTgxMTg0fQ.-8gIwEFbC2eslCpyRQM0i3gzzqnbyqUopdP0EjE7TI0" \
    -d '{"input_data": {"Serial_No": A+, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo