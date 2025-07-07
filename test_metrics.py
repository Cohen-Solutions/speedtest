#!/usr/bin/env python3
"""
Script d'exemple pour tester les métriques Prometheus
"""

import requests
import time
import json

def test_prometheus_metrics(port=8000):
    """Teste les métriques Prometheus"""
    url = f"http://localhost:{port}/metrics"
    
    print(f"Test des métriques Prometheus sur {url}")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        print("✓ Serveur Prometheus accessible")
        print(f"✓ Code de statut: {response.status_code}")
        print(f"✓ Taille de la réponse: {len(response.text)} caractères")
        
        # Analyser les métriques
        metrics = response.text
        
        # Chercher les métriques speedtest
        speedtest_metrics = []
        for line in metrics.split('\n'):
            if 'speedtest_' in line and not line.startswith('#'):
                speedtest_metrics.append(line.strip())
        
        if speedtest_metrics:
            print(f"✓ {len(speedtest_metrics)} métriques speedtest trouvées:")
            for metric in speedtest_metrics:
                print(f"  - {metric}")
        else:
            print("⚠ Aucune métrique speedtest trouvée (peut-être qu'aucun test n'a été exécuté)")
        
        print("\n" + "=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("✗ Impossible de se connecter au serveur Prometheus")
        print("  Assurez-vous que le programme principal est en cours d'exécution")
    except requests.exceptions.Timeout:
        print("✗ Timeout lors de la connexion")
    except requests.exceptions.RequestException as e:
        print(f"✗ Erreur lors de la requête: {e}")
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")

def monitor_metrics(port=8000, interval=30):
    """Monitore les métriques en continu"""
    print(f"Monitoring des métriques toutes les {interval} secondes...")
    print("Appuyez sur Ctrl+C pour arrêter")
    
    try:
        while True:
            test_prometheus_metrics(port)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nArrêt du monitoring")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test des métriques Prometheus')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port du serveur Prometheus (défaut: 8000)')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitorer en continu')
    parser.add_argument('--interval', type=int, default=30,
                       help='Intervalle de monitoring en secondes (défaut: 30)')
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_metrics(args.port, args.interval)
    else:
        test_prometheus_metrics(args.port)
