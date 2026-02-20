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

# Listes de commandes 

### Création de l'environnement virtuel
uv venv
source .venv/bin/activate
uv pip sync requirements.txt

### lancer le service avec docker
docker run --rm -p 3000:3000 rf_classifier_service:yhdchzan4kt4dt4s

#### pour afficher le swagger
http://127.0.0.1:3000

#### Identification et création du token 
"user123": "password123",
"user456": "password456",

#### on met le token dans une variable 
token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzcxNjA1NjcwfQ.wl1-v9BmxHkxH2TBN6nFS4ZKN4WZZ5K3ABWaCLyhJjs"

#### On test une prediction
curl -s -X POST "http://127.0.0.1:3000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"input_data": {"Serial_No": 362, "GRE_Score": 334, "TOEFL_Score": 116, "University_Rating": 4, "SOP": 4.0, "LOR": 3.5, "CGPA": 9.54, "Research": 1}}'; \
echo

### lancer les tests

#### Ajout de la librairie de test
uv add pytest --dev

#### On joue les tests
pytest -v