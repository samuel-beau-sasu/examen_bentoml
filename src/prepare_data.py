# src/prepare_data.py

import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
from loguru import logger


# charger les données

# Dossier courant / racine du projet
input_filepath = Path.cwd() / "data" / "raw"
output_filepath = Path.cwd() / "data" / "processed"
input_filepath_admission = input_filepath / "admission.csv"

df_users = pd.read_csv(input_filepath_admission, sep=",")



# check data
def check_data(df):
    df = df_users
    # 1. Aperçu général
    print("SHAPE:", df.shape)
    print(df.head())
    print(df.info())
    print("\n" + "="*50 + "\n")

    # 2. Statistiques descriptives
    print("STATS NUMÉRIQUES:")
    print(df.describe())
    print("\n" + "="*50 + "\n")

    # 3. Vérifier valeurs manquantes
    print("VALEURS MANQUANTES:")
    print(df.isnull().sum())
    print("\n" + "="*50 + "\n")
    
    #logger.success(f"Data propres ")
    logger.info(f"Data propres ")

check_data(df_users)

# nettoyer es données

# diviser en un jeu d'entraînement et un jeu de test

def build_feature(df):

    # Séparer features (X) et cible (y)
    X = df.drop('Chance of Admit ', axis=1)  # toutes les colonnes sauf la cible
    y = df['Chance of Admit ']               # colonne cible

    # Diviser 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2,           # 20% test
        random_state=42,         # reproductible
        shuffle=True             # mélange avant division
    )
    
    # Sauvegarder X_train, X_test, y_train, y_test
    X_train.to_csv("data/processed/X_train.csv", index=False)
    X_test.to_csv("data/processed/X_test.csv", index=False)
    y_train.to_csv("data/processed/y_train.csv", index=False)
    y_test.to_csv("data/processed/y_test.csv", index=False)
    
    logger.success(f"Jeu d'entraînement et un jeu de test prêt")
    

build_feature(df_users)

X_train = pd.read_csv(output_filepath / "X_train.csv", sep=",")
X_test = pd.read_csv(output_filepath / "X_test.csv", sep=",")

# Vérification
print(f"Train: {X_train.shape[0]} échantillons")
print(f"Test:  {X_test.shape[0]} échantillons")
print(f"Total: {len(df_users)} échantillons")


# sauvegarder X_train, X_test, y_train, y_test dans le dossier data/processed.

