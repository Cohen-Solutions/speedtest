#!/usr/bin/env python3
"""
Programme de test de débit internet avec intégration Prometheus
Utilise speedtest-cli pour mesurer la vitesse de connexion et expose les métriques via Prometheus
"""

import json
import subprocess
import time
import logging
from prometheus_client import start_http_server, Gauge, Counter, Info
from datetime import datetime
import sys
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('speedtest.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Métriques Prometheus
download_speed_gauge = Gauge('speedtest_download_speed_mbps', 'Vitesse de téléchargement en Mbps')
upload_speed_gauge = Gauge('speedtest_upload_speed_mbps', 'Vitesse d\'upload en Mbps')
ping_gauge = Gauge('speedtest_ping_ms', 'Ping en millisecondes')
jitter_gauge = Gauge('speedtest_jitter_ms', 'Jitter en millisecondes')
packet_loss_gauge = Gauge('speedtest_packet_loss_percent', 'Perte de paquets en pourcentage')

# Compteurs pour les statistiques
tests_total = Counter('speedtest_tests_total', 'Nombre total de tests effectués')
tests_failed = Counter('speedtest_tests_failed', 'Nombre de tests échoués')

# Informations sur le serveur et l'ISP
server_info = Info('speedtest_server_info', 'Informations sur le serveur de test')
isp_info = Info('speedtest_isp_info', 'Informations sur le fournisseur d\'accès')

class SpeedtestManager:
    def __init__(self):
        self.last_test_time = None
        self.test_interval = 300  # 5 minutes par défaut
        
    def run_speedtest(self):
        """Exécute le test de débit et retourne les résultats en JSON"""
        try:
            logger.info("Début du test de débit...")
            
            # Exécuter speedtest-cli avec sortie JSON
            cmd = ['speedtest-cli', '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"Erreur lors du test de débit: {result.stderr}")
                tests_failed.inc()
                return None
            
            # Parser le JSON
            data = json.loads(result.stdout)
            logger.info("Test de débit terminé avec succès")
            
            return data
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout lors du test de débit")
            tests_failed.inc()
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du parsing JSON: {e}")
            tests_failed.inc()
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            tests_failed.inc()
            return None
    
    def update_prometheus_metrics(self, data):
        """Met à jour les métriques Prometheus avec les données du test"""
        try:
            # Conversion des vitesses en Mbps
            download_mbps = data.get('download', 0) / 1_000_000  # bits/s vers Mbps
            upload_mbps = data.get('upload', 0) / 1_000_000      # bits/s vers Mbps
            ping_ms = data.get('ping', 0)
            
            # Mise à jour des métriques
            download_speed_gauge.set(download_mbps)
            upload_speed_gauge.set(upload_mbps)
            ping_gauge.set(ping_ms)
            
            # Jitter et perte de paquets (si disponibles)
            if 'jitter' in data:
                jitter_gauge.set(data['jitter'])
            if 'packet_loss' in data:
                packet_loss_gauge.set(data['packet_loss'])
            
            # Informations sur le serveur
            if 'server' in data:
                server_data = data['server']
                server_info.info({
                    'name': server_data.get('name', 'Unknown'),
                    'sponsor': server_data.get('sponsor', 'Unknown'),
                    'country': server_data.get('country', 'Unknown'),
                    'host': server_data.get('host', 'Unknown'),
                    'id': str(server_data.get('id', 'Unknown'))
                })
            
            # Informations sur l'ISP
            if 'client' in data:
                client_data = data['client']
                isp_info.info({
                    'isp': client_data.get('isp', 'Unknown'),
                    'ip': client_data.get('ip', 'Unknown'),
                    'country': client_data.get('country', 'Unknown')
                })
            
            tests_total.inc()
            
            logger.info(f"Métriques mises à jour - Download: {download_mbps:.2f} Mbps, "
                       f"Upload: {upload_mbps:.2f} Mbps, Ping: {ping_ms:.2f} ms")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques: {e}")
    
    def log_results(self, data):
        """Affiche les résultats du test"""
        if not data:
            return
            
        try:
            download_mbps = data.get('download', 0) / 1_000_000
            upload_mbps = data.get('upload', 0) / 1_000_000
            ping_ms = data.get('ping', 0)
            
            timestamp = datetime.now().isoformat()
            
            print(f"\n{'='*60}")
            print(f"RÉSULTATS DU TEST DE DÉBIT - {timestamp}")
            print(f"{'='*60}")
            print(f"Vitesse de téléchargement: {download_mbps:.2f} Mbps")
            print(f"Vitesse d'upload:         {upload_mbps:.2f} Mbps")
            print(f"Ping:                     {ping_ms:.2f} ms")
            
            if 'server' in data:
                server = data['server']
                print(f"Serveur:                  {server.get('name', 'N/A')} ({server.get('sponsor', 'N/A')})")
                print(f"Localisation:             {server.get('country', 'N/A')}")
            
            if 'client' in data:
                client = data['client']
                print(f"FAI:                      {client.get('isp', 'N/A')}")
                print(f"IP externe:               {client.get('ip', 'N/A')}")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des résultats: {e}")
    
    def run_continuous(self, interval=300):
        """Lance des tests en continu à intervalles réguliers"""
        logger.info(f"Démarrage des tests continus (intervalle: {interval} secondes)")
        
        while True:
            try:
                # Exécuter le test
                data = self.run_speedtest()
                
                if data:
                    self.update_prometheus_metrics(data)
                    self.log_results(data)
                    self.last_test_time = datetime.now()
                
                # Attendre avant le prochain test
                logger.info(f"Attente de {interval} secondes avant le prochain test...")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {e}")
                time.sleep(30)  # Attente courte en cas d'erreur
    
    def run_single_test(self):
        """Exécute un test unique"""
        logger.info("Exécution d'un test unique")
        
        data = self.run_speedtest()
        
        if data:
            self.update_prometheus_metrics(data)
            self.log_results(data)
            return data
        else:
            print("Échec du test de débit")
            return None

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test de débit avec intégration Prometheus')
    parser.add_argument('--port', type=int, default=8000, 
                       help='Port pour le serveur Prometheus (défaut: 8000)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Intervalle entre les tests en secondes (défaut: 300)')
    parser.add_argument('--single', action='store_true',
                       help='Exécuter un test unique au lieu du mode continu')
    parser.add_argument('--no-prometheus', action='store_true',
                       help='Désactiver le serveur Prometheus')
    
    args = parser.parse_args()
    
    # Initialiser le gestionnaire de speedtest
    manager = SpeedtestManager()
    
    # Démarrer le serveur Prometheus si demandé
    if not args.no_prometheus:
        try:
            start_http_server(args.port)
            logger.info(f"Serveur Prometheus démarré sur le port {args.port}")
            print(f"Métriques Prometheus disponibles sur: http://localhost:{args.port}/metrics")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du serveur Prometheus: {e}")
            sys.exit(1)
    
    # Vérifier que speedtest-cli est disponible
    try:
        subprocess.run(['speedtest-cli', '--version'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        logger.error("speedtest-cli n'est pas installé ou non accessible")
        print("Veuillez installer speedtest-cli: pip install speedtest-cli")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("speedtest-cli n'est pas trouvé dans le PATH")
        print("Veuillez installer speedtest-cli: pip install speedtest-cli")
        sys.exit(1)
    
    # Exécuter selon le mode choisi
    if args.single:
        manager.run_single_test()
    else:
        try:
            manager.run_continuous(args.interval)
        except KeyboardInterrupt:
            logger.info("Programme arrêté par l'utilisateur")
            print("\nArrêt du programme...")

if __name__ == "__main__":
    main()