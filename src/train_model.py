# src/train_model.py 
import pandas as pd
from pathlib import Path
from sklearn import ensemble
from sklearn.metrics import mean_squared_error, r2_score
import bentoml

# charger les données d'entraînement, de créer un modèle de régression et de l'entraîner.

intput_filepath = Path.cwd() / "data" / "processed"

X_train = pd.read_csv(intput_filepath / "X_train.csv", sep=",")
y_train = pd.read_csv(intput_filepath / "y_train.csv", sep=",").squeeze() # pour extraire la colonne cible sous forme de série ou d'array 1D 

X_test = pd.read_csv(intput_filepath / "X_test.csv", sep=",")
y_test = pd.read_csv(intput_filepath / "y_test.csv", sep=",").squeeze()

#print(f"X Train: {X_train.head()} ")
#print(f"y Test:  {y_train.head()} ")


gb_regressor = ensemble.GradientBoostingRegressor(
    n_estimators=50,
    learning_rate=0.1,
    max_depth=3,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    subsample=0.8,
    random_state=42
)


# Initialisation et entraînement
rf_regressor = ensemble.RandomForestRegressor(
    n_estimators=10,
    max_depth=1,
    min_samples_split=5,
    random_state=42
)

#--Train the model
gb_regressor.fit(X_train, y_train)

# testez et affichez ses performances sur les données de test. 
# ous pourrez utiliser la métrique de votre choix (R2, RMSE, MAE, ...).


# Prédictions et évaluation
y_pred = gb_regressor.predict(X_test)
print("MSE :", mean_squared_error(y_test, y_pred))
print("R² :", r2_score(y_test, y_pred))


# si les performances de votre modèle sont satisfaisantes suite aux tests successifs que vous aurez faits, 
# vous devez sauvegarder votre modèle dans le Model Store de BentoML.

if (r2_score(y_test, y_pred) > 0.8):
    model_ref = bentoml.sklearn.save_model("admission_gb", gb_regressor)
    #print(f"Modèle enregistré sous : {model_ref}")
    model = bentoml.sklearn.get("admission_gb:latest")
    print(f"check Modèle enregistré sous : {model}")
else:
    print(f"Modèle non enregisté car inférieur au seuil de performance :R² > 0.8)")

# Suite à la sauvegarde, vérifiez que votre modèle est bien enregistré

