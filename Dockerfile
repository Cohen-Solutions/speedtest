FROM python:3.13-slim

# Métadonnées
LABEL org.opencontainers.image.title="Speedtest Prometheus Exporter"
LABEL org.opencontainers.image.description="Application Python pour tester la vitesse Internet et exposer les métriques via Prometheus"
LABEL org.opencontainers.image.vendor="speedtest-prometheus"
LABEL org.opencontainers.image.source="https://github.com/cohen-solutions/speedtest"

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/

# Exposer le port Prometheus
EXPOSE 8000

# Commande par défaut
CMD ["python", "src/main.py"]
