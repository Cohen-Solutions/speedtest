# Speedtest avec Prometheus

Ce programme Python utilise speedtest-cli pour mesurer la vitesse de connexion internet et expose les métriques via Prometheus.

## Fonctionnalités

- **Test de débit automatique** : Mesure la vitesse de téléchargement, d'upload et le ping
- **Intégration Prometheus** : Expose les métriques pour monitoring
- **Logs détaillés** : Sauvegarde des résultats et erreurs
- **Mode continu ou unique** : Exécution ponctuelle ou monitoring continu
- **Sortie JSON** : Utilise speedtest-cli avec sortie JSON pour plus de précision

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Vérifier que speedtest-cli fonctionne :
```bash
speedtest-cli --version
```

## Utilisation

### Test unique
```bash
python src/main.py --single
```

### Mode continu (défaut)
```bash
python src/main.py
```

### Options disponibles
```bash
python src/main.py --help
```

- `--port PORT` : Port pour le serveur Prometheus (défaut: 8000)
- `--interval SECONDS` : Intervalle entre les tests (défaut: 300 secondes)
- `--single` : Exécuter un test unique
- `--no-prometheus` : Désactiver le serveur Prometheus

## Métriques Prometheus

Les métriques sont disponibles sur `http://localhost:8000/metrics` :

- `speedtest_download_speed_mbps` : Vitesse de téléchargement en Mbps
- `speedtest_upload_speed_mbps` : Vitesse d'upload en Mbps
- `speedtest_ping_ms` : Ping en millisecondes
- `speedtest_jitter_ms` : Jitter en millisecondes
- `speedtest_packet_loss_percent` : Perte de paquets en pourcentage
- `speedtest_tests_total` : Nombre total de tests effectués
- `speedtest_tests_failed` : Nombre de tests échoués
- `speedtest_server_info` : Informations sur le serveur de test
- `speedtest_isp_info` : Informations sur le fournisseur d'accès

## Logs

Les logs sont sauvegardés dans `speedtest.log` et affichés sur la console.

## Exemples

### Test unique avec affichage des résultats
```bash
python src/main.py --single
```

### Monitoring continu avec tests toutes les 10 minutes
```bash
python src/main.py --interval 600
```

### Test unique sans serveur Prometheus
```bash
python src/main.py --single --no-prometheus
```

## Intégration avec Grafana

Pour visualiser les métriques dans Grafana :

1. Configurer Prometheus pour scraper les métriques
2. Ajouter Prometheus comme source de données dans Grafana
3. Créer des dashboards avec les métriques speedtest

Exemple de configuration Prometheus (`prometheus.yml`) :
```yaml
scrape_configs:
  - job_name: 'speedtest'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 5m
```
