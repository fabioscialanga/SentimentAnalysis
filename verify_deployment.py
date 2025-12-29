#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import subprocess
import requests
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    try:
        print(f"{Colors.GREEN}✓{Colors.RESET} {text}")
    except UnicodeEncodeError:
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")

def print_error(text: str):
    try:
        print(f"{Colors.RED}✗{Colors.RESET} {text}")
    except UnicodeEncodeError:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} {text}")

def print_warning(text: str):
    try:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")
    except UnicodeEncodeError:
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {text}")

def print_info(text: str):
    try:
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")
    except UnicodeEncodeError:
        print(f"{Colors.BLUE}[INFO]{Colors.RESET} {text}")

class DeploymentVerifier:
    def __init__(self):
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {}
        self.api_url = os.getenv('API_URL', 'http://localhost:5000')
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
        self.grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
        self.api_token = os.getenv('API_TOKEN')
        self.deployment_type = None  # 'docker', 'k8s', o 'local'
        
    def check_command(self, cmd: List[str]) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10,
                check=False
            )
            return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except FileNotFoundError:
            return False, f"Comando non trovato: {cmd[0]}"
        except Exception as e:
            return False, str(e)
    
    def detect_deployment_type(self) -> str:
        print_info("Rilevamento tipo di deployment...")
        
        success, _ = self.check_command(['kubectl', 'get', 'namespace', 'sentiment'])
        if success:
            self.deployment_type = 'k8s'
            print_success("Deployment Kubernetes rilevato")
            return 'k8s'
        
        success, _ = self.check_command(['docker-compose', 'ps'])
        if success:
            output = subprocess.run(
                ['docker-compose', 'ps', '--format', 'json'],
                capture_output=True,
                text=True
            ).stdout
            if 'sentiment-api' in output or 'sentiment' in output.lower():
                self.deployment_type = 'docker'
                print_success("Deployment Docker Compose rilevato")
                return 'docker'
        
        success, _ = self.check_command(['docker', 'ps', '--filter', 'name=sentiment'])
        if success:
            self.deployment_type = 'docker'
            print_success("Deployment Docker rilevato")
            return 'docker'
        
        self.deployment_type = 'local'
        print_warning("Nessun deployment containerizzato rilevato. Verifica locale.")
        return 'local'
    
    def verify_file_structure(self) -> bool:
        print_header("1. VERIFICA STRUTTURA FILE")
        
        required_files = [
            'api/app.py',
            'api/Dockerfile',
            'api/requirements.txt',
            'api/tests/test_app.py',
            'docker-compose.yml',
            'k8s/sentiment-stack.yaml',
            'monitoring/prometheus.yml',
            'monitoring/alerts.yml',
            'jenkins/Jenkinsfile',
            'README.md'
        ]
        
        all_present = True
        for file_path in required_files:
            if os.path.exists(file_path):
                print_success(f"File presente: {file_path}")
            else:
                print_error(f"File mancante: {file_path}")
                all_present = False
        
        return all_present
    
    def verify_unit_tests(self) -> bool:
        print_header("2. VERIFICA TEST UNITARI")
        
        try:
            original_dir = os.getcwd()
            os.chdir('api')
            
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/test_app.py', '-v'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                print_success("Tutti i test unitari passati")
                print_info(result.stdout)
                return True
            else:
                print_error("Alcuni test sono falliti")
                print_error(result.stdout)
                print_error(result.stderr)
                return False
        except Exception as e:
            print_error(f"Errore durante l'esecuzione dei test: {e}")
            return False
    
    def verify_api_endpoints(self) -> bool:
        print_header("3. VERIFICA ENDPOINT API")
        
        all_ok = True
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    print_success(f"Health check OK: {response.status_code}")
                else:
                    print_error(f"Health check: status non valido: {data}")
                    all_ok = False
            else:
                print_error(f"Health check fallito: {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print_error(f"Health check non raggiungibile: {e}")
            all_ok = False
        
        try:
            response = requests.get(f"{self.api_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics = response.text
                required_metrics = [
                    'request_count',
                    'request_latency_seconds',
                    'prediction_errors_total',
                    'auth_failures_total'
                ]
                missing = [m for m in required_metrics if m not in metrics]
                if not missing:
                    print_success("Endpoint /metrics OK con tutte le metriche")
                else:
                    print_warning(f"Metriche mancanti: {missing}")
            else:
                print_error(f"Metrics endpoint fallito: {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print_error(f"Metrics endpoint non raggiungibile: {e}")
            all_ok = False
        
        test_reviews = [
            ("This product is amazing!", "positive"),
            ("Terrible experience, very disappointed.", "negative"),
            ("It's okay, nothing special.", "neutral")
        ]
        
        headers = {}
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        for review, expected_sentiment in test_reviews:
            try:
                response = requests.post(
                    f"{self.api_url}/predict",
                    json={'review': review},
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'sentiment' in data and 'confidence' in data:
                        sentiment = data['sentiment']
                        confidence = data['confidence']
                        print_success(
                            f"Predict OK: '{review[:30]}...' -> {sentiment} "
                            f"(confidence: {confidence:.2f})"
                        )
                    else:
                        print_error(f"Risposta predict incompleta: {data}")
                        all_ok = False
                elif response.status_code == 401:
                    print_warning("Predict richiede autenticazione (401)")
                    response_no_auth = requests.post(
                        f"{self.api_url}/predict",
                        json={'review': review},
                        timeout=10
                    )
                    if response_no_auth.status_code == 401:
                        print_success("Autenticazione funzionante (401 senza token)")
                    else:
                        print_error("Autenticazione non funzionante correttamente")
                else:
                    print_error(f"Predict fallito: {response.status_code} - {response.text}")
                    all_ok = False
            except requests.exceptions.RequestException as e:
                print_error(f"Predict non raggiungibile: {e}")
                all_ok = False
        
        return all_ok
    
    def verify_docker_services(self) -> bool:
        print_header("4. VERIFICA SERVIZI DOCKER")
        
        if self.deployment_type != 'docker':
            print_info("Deployment Docker non rilevato, skip...")
            return True
        
        all_ok = True
        
        success, output = self.check_command(['docker-compose', 'ps'])
        if success:
            print_success("Docker Compose attivo")
            print_info(output)
            
            services = ['sentiment-api', 'prometheus', 'grafana']
            for service in services:
                result = subprocess.run(
                    ['docker-compose', 'ps', service],
                    capture_output=True,
                    text=True
                )
                if service in result.stdout and 'Up' in result.stdout:
                    print_success(f"Servizio {service} in esecuzione")
                else:
                    print_warning(f"Servizio {service} non trovato o non in esecuzione")
        else:
            print_error("Docker Compose non disponibile o non in esecuzione")
            all_ok = False
        
        return all_ok
    
    def verify_kubernetes_deployment(self) -> bool:
        print_header("5. VERIFICA DEPLOYMENT KUBERNETES")
        
        if self.deployment_type != 'k8s':
            print_info("Deployment Kubernetes non rilevato, skip...")
            return True
        
        all_ok = True
        
        success, output = self.check_command(['kubectl', 'get', 'namespace', 'sentiment'])
        if success:
            print_success("Namespace 'sentiment' presente")
        else:
            print_error("Namespace 'sentiment' non trovato")
            all_ok = False
        
        success, output = self.check_command([
            'kubectl', 'get', 'pods', '-n', 'sentiment', '--no-headers'
        ])
        if success:
            lines = [l for l in output.split('\n') if l.strip()]
            running_pods = [l for l in lines if 'Running' in l]
            print_success(f"Pod trovati: {len(running_pods)}/{len(lines)} in esecuzione")
            print_info(output)
        else:
            print_error("Impossibile verificare i pod")
            all_ok = False
        
        success, output = self.check_command([
            'kubectl', 'get', 'svc', '-n', 'sentiment'
        ])
        if success:
            print_success("Servizi Kubernetes presenti")
            print_info(output)
        else:
            print_warning("Impossibile verificare i servizi")
        
        return all_ok
    
    def verify_prometheus(self) -> bool:
        print_header("6. VERIFICA PROMETHEUS")
        
        all_ok = True
        
        # Verifica accessibilità
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            if response.status_code == 200:
                print_success("Prometheus raggiungibile")
            else:
                print_error(f"Prometheus non healthy: {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print_warning(f"Prometheus non raggiungibile: {e}")
            print_info("Assicurati che Prometheus sia in esecuzione e accessibile")
            return False
        
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/targets",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                targets = data.get('data', {}).get('activeTargets', [])
                up_targets = [t for t in targets if t.get('health') == 'up']
                print_success(f"Target Prometheus: {len(up_targets)}/{len(targets)} UP")
                
                for target in targets:
                    health = target.get('health', 'unknown')
                    job = target.get('labels', {}).get('job', 'unknown')
                    if health == 'up':
                        print_success(f"  - {job}: {health}")
                    else:
                        print_warning(f"  - {job}: {health}")
            else:
                print_warning("Impossibile verificare i target")
        except requests.exceptions.RequestException as e:
            print_warning(f"Errore nel controllo target: {e}")
        
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query?query=request_count",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print_success("Metriche raccolte da Prometheus")
                else:
                    print_warning("Nessuna metrica disponibile (normale se non ci sono state richieste)")
        except requests.exceptions.RequestException as e:
            print_warning(f"Errore nel controllo metriche: {e}")
        
        return all_ok
    
    def verify_grafana(self) -> bool:
        print_header("7. VERIFICA GRAFANA")
        
        all_ok = True
        
        # Verifica accessibilità
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('database') == 'ok':
                    print_success("Grafana raggiungibile e database OK")
                else:
                    print_warning(f"Grafana raggiungibile ma database: {data.get('database')}")
            else:
                print_error(f"Grafana non healthy: {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print_warning(f"Grafana non raggiungibile: {e}")
            print_info("Assicurati che Grafana sia in esecuzione e accessibile")
            return False
        
        print_info("Per verificare i datasource, accedi a Grafana manualmente")
        print_info(f"URL: {self.grafana_url}")
        print_info("Username: admin")
        print_info("Password: (controlla il file .env o il Secret Kubernetes)")
        
        return all_ok
    
    def verify_configurations(self) -> bool:
        print_header("8. VERIFICA CONFIGURAZIONI")
        
        all_ok = True
        
        if os.path.exists('.env'):
            print_success("File .env presente")
        else:
            print_warning("File .env non presente (usa env.example come template)")
        
        if os.path.exists('docker-compose.yml'):
            print_success("File docker-compose.yml presente")
            try:
                with open('docker-compose.yml', 'r') as f:
                    content = f.read()
                    if 'sentiment-api' in content and 'prometheus' in content:
                        print_success("docker-compose.yml configurato correttamente")
                    else:
                        print_warning("docker-compose.yml potrebbe essere incompleto")
            except Exception as e:
                print_error(f"Errore nella lettura docker-compose.yml: {e}")
        else:
            print_warning("File docker-compose.yml non presente")
        
        if os.path.exists('k8s/sentiment-stack.yaml'):
            print_success("Manifest Kubernetes presente")
            try:
                with open('k8s/sentiment-stack.yaml', 'r') as f:
                    content = f.read()
                    required_resources = [
                        'kind: Namespace',
                        'kind: Deployment',
                        'kind: Service',
                        'kind: ConfigMap'
                    ]
                    missing = [r for r in required_resources if r not in content]
                    if not missing:
                        print_success("Manifest Kubernetes completo")
                    else:
                        print_warning(f"Risorse mancanti nel manifest: {missing}")
            except Exception as e:
                print_error(f"Errore nella lettura manifest Kubernetes: {e}")
        else:
            print_warning("Manifest Kubernetes non presente")
        
        return all_ok
    
    def generate_report(self) -> Dict:
        print_header("REPORT FINALE")
        
        total_checks = 0
        passed_checks = 0
        
        checks = [
            ("Struttura File", self.verify_file_structure()),
            ("Test Unitari", self.verify_unit_tests()),
            ("Endpoint API", self.verify_api_endpoints()),
            ("Servizi Docker", self.verify_docker_services()),
            ("Deployment Kubernetes", self.verify_kubernetes_deployment()),
            ("Prometheus", self.verify_prometheus()),
            ("Grafana", self.verify_grafana()),
            ("Configurazioni", self.verify_configurations()),
        ]
        
        print("\n" + "="*60)
        print("RIEPILOGO VERIFICHE")
        print("="*60 + "\n")
        
        for name, result in checks:
            total_checks += 1
            if result:
                passed_checks += 1
                status = f"{Colors.GREEN}✓ PASS{Colors.RESET}"
            else:
                status = f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"{name:30} {status}")
        
        print("\n" + "="*60)
        percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        print(f"Risultato: {passed_checks}/{total_checks} verifiche passate ({percentage:.1f}%)")
        print("="*60 + "\n")
        
        if passed_checks == total_checks:
            print_success("TUTTE LE VERIFICHE SONO PASSATE!")
        elif passed_checks >= total_checks * 0.7:
            print_warning("Alcune verifiche sono fallite. Controlla i dettagli sopra.")
        else:
            print_error("Molte verifiche sono fallite. Rivedi la configurazione.")
        
        return {
            'total': total_checks,
            'passed': passed_checks,
            'percentage': percentage,
            'deployment_type': self.deployment_type
        }
    
    def run_all_checks(self):
        print_header("VERIFICA COMPLETA DEL SISTEMA SENTIMENT ANALYSIS")
        print_info(f"API URL: {self.api_url}")
        print_info(f"Prometheus URL: {self.prometheus_url}")
        print_info(f"Grafana URL: {self.grafana_url}")
        print_info(f"Tipo deployment: {self.detect_deployment_type()}")
        
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("PROSSIMI PASSI")
        print("="*60)
        print("1. Se alcune verifiche sono fallite, controlla i log:")
        if self.deployment_type == 'docker':
            print("   docker-compose logs")
        elif self.deployment_type == 'k8s':
            print("   kubectl logs -n sentiment -l app=sentiment-api")
        else:
            print("   Controlla i log dell'applicazione")
        
        print("\n2. Verifica manualmente:")
        print(f"   - API: {self.api_url}/health")
        print(f"   - Prometheus: {self.prometheus_url}")
        print(f"   - Grafana: {self.grafana_url}")
        
        print("\n3. Esegui test manuali:")
        print("   python test_client.py")
        
        return report

def main():
    verifier = DeploymentVerifier()
    report = verifier.run_all_checks()
    
    # Exit code basato sul risultato
    if report['percentage'] == 100:
        sys.exit(0)
    elif report['percentage'] >= 70:
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == '__main__':
    main()

