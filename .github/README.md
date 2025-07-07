# GitHub Actions - Docker Build and Push

Ce projet utilise GitHub Actions pour construire automatiquement l'image Docker et l'uploader vers GitHub Container Registry.

## Workflows disponibles

### 1. `docker-publish.yml`
Workflow complet avec attestation et support multi-plateforme :
- Se déclenche sur push vers `main`/`master` et sur les tags
- Construit pour `linux/amd64` et `linux/arm64`
- Génère des attestations de provenance
- Utilise la cache GitHub Actions

### 2. `docker-build.yml`
Workflow simplifié :
- Se déclenche sur push vers `main`/`master` et sur les tags
- Peut être déclenché manuellement
- Support multi-plateforme

## Configuration

### 1. Permissions du repository
Assurez-vous que votre repository a les permissions suivantes :
- `Settings` → `Actions` → `General` → `Workflow permissions` → `Read and write permissions`

### 2. GitHub Container Registry
Les workflows utilisent automatiquement `GITHUB_TOKEN` pour s'authentifier.

## Tags générés

Les images Docker sont taguées automatiquement :
- `main` → `ghcr.io/cohen-solutions/speedtest:main`
- `v1.0.0` → `ghcr.io/cohen-solutions/speedtest:v1.0.0`
- SHA commit → `ghcr.io/cohen-solutions/speedtest:sha-abc123`
- `latest` → pour la branche par défaut

## Utilisation

### 1. Déclencher un build
```bash
# Push vers main
git push origin main

# Créer un tag
git tag v1.0.0
git push origin v1.0.0

# Déclencher manuellement (docker-build.yml uniquement)
# Via l'interface GitHub ou GitHub CLI
gh workflow run docker-build.yml
```

### 2. Utiliser l'image
```bash
# Utiliser la dernière version
docker pull ghcr.io/cohen-solutions/speedtest:latest

# Utiliser une version spécifique
docker pull ghcr.io/cohen-solutions/speedtest:v1.0.0

# Lancer le container
docker run -d -p 8000:8000 ghcr.io/cohen-solutions/speedtest:latest
```

### 3. Avec docker-compose
```yaml
version: '3.8'
services:
  speedtest:
    image: ghcr.io/cohen-solutions/speedtest:latest
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
```

## Dépannage

### Erreur de permissions
Si vous obtenez une erreur 403 :
1. Vérifiez les permissions du repository
2. Assurez-vous que les packages sont publics dans les paramètres

### Build échoue
1. Vérifiez les logs dans l'onglet Actions
2. Assurez-vous que le Dockerfile est correct
3. Vérifiez que tous les fichiers nécessaires sont présents

## Sécurité

Les workflows utilisent :
- `GITHUB_TOKEN` automatique (pas besoin de secrets personnels)
- Attestations de provenance pour la sécurité
- Cache GitHub Actions pour optimiser les builds
- Support multi-plateforme pour la compatibilité
