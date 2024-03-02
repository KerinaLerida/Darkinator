# Utilisation de l'image python:latest comme base
FROM python:3.11
LABEL authors="keren"

# Copie des fichiers de votre projet dans le répertoire de travail du conteneur
COPY . /app

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances nécessaires
RUN pip install -r requirements.txt

# Définir le script de démarrage comme commande par défaut
CMD ["python", "main.py"]
