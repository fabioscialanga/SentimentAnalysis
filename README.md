# Sentiment Analysis Deployment & Monitoring Project

Questo progetto implementa un sistema completo per il deploy e il monitoraggio di un modello di Sentiment Analysis.

## Struttura del Progetto
- **api/**: Contiene il codice sorgente dell'API Flask, il Dockerfile e il modello.
- **jenkins/**: Contiene il `Jenkinsfile` per la pipeline CI/CD.
- **monitoring/**: Contiene la configurazione di Prometheus e Grafana.
- **k8s/**: Manifests Kubernetes per deploy e monitoraggio.
- **docker-compose.yml**: Orchestration per avviare tutti i servizi localmente.
- **env.example**: Valori di esempio per le variabili ambiente.

## Prerequisiti
- Docker e Docker Compose installati.
- Python 3.9+ (opzionale per test locali).

## Istruzioni per l'Avvio Rapido
1.  **Avvia i servizi**:
    ```bash
    cp env.example .env   # imposta le tue password/token
    docker-compose up -d --build
    ```
    Questo comando costruirà l'immagine dell'API e avvierà API, Prometheus e Grafana.

2.  **Accedi ai Servizi**:
    - **API**: `http://localhost:5000`
        - Test predizione: `POST /predict` con JSON `{"review": "I love this product"}`
    - **Prometheus**: `http://localhost:9090`
    - **Grafana**: `http://localhost:3000` (Login: admin/<password in .env>)

## Dettagli Tecnici

### 1. Sentiment Analysis Model API
L'API è costruita con **Flask**.
- Carica automaticamente il modello `sentimentanalysismodel.pkl` scaricandolo dal repository pubblico (configurabile via `MODEL_URL`). Se il download fallisce, utilizza una logica di fallback con TextBlob per garantire la disponibilità del servizio.
- Supporta autenticazione opzionale con token Bearer (`API_TOKEN`): quando impostato, le chiamate (tranne `/`, `/health`, `/metrics`) richiedono l'header `Authorization: Bearer <token>`.
- Espone `/predict` per le previsioni.
- Espone `/metrics` per Prometheus.

### 2. CI/CD con Jenkins
Il file `jenkins/Jenkinsfile` definisce una pipeline che:
- **Build**: Costruisce l'immagine Docker.
- **Test**: Esegue i test unitari con `pytest`.
- **Deploy**: Aggiorna il container in esecuzione tramite Docker Compose (flag opzionale `APPLY_K8S` per applicare `k8s/sentiment-stack.yaml` con `kubectl`).

### 3. Monitoraggio
- **Prometheus**: Raccoglie metriche ogni 15 secondi dall'endpoint `/metrics` dell'API. Include regole di alerting (errori frequenti, latenza p95 > 1s).
- **Grafana**: Provisioning automatico di datasource Prometheus e dashboard `Sentiment API - Overview` (richieste, errori, auth fail, p95 latenza, throughput). Password admin configurabile via `GF_SECURITY_ADMIN_PASSWORD`.

## Deploy su Kubernetes (manifests pronti)
```bash
kubectl apply -f k8s/sentiment-stack.yaml
```
I manifest includono namespace dedicato, secret per la password Grafana (riutilizzata anche come token API), ConfigMap Prometheus e provisioning Grafana.

## Repository Git

Questo progetto è gestito tramite Git e può essere pubblicato su GitHub o GitLab.

### Pubblicazione su GitHub/GitLab

1. **Crea un nuovo repository** su GitHub o GitLab (non inizializzarlo con README, .gitignore o licenza).

2. **Aggiungi il remote e pubblica**:
   ```bash
   git remote add origin <URL-del-tuo-repository>
   git branch -M main
   git push -u origin main
   ```

3. **Configura Jenkins** (se necessario):
   - Aggiungi il repository come sorgente nella pipeline Jenkins
   - Il Jenkinsfile è già configurato per trigger automatici su commit

### Struttura del Repository

Il repository include:
- Codice sorgente dell'API Flask
- Configurazioni Docker e Kubernetes
- Pipeline CI/CD Jenkins
- Configurazioni Prometheus e Grafana
- Dashboard e alerting preconfigurati
- Test automatizzati

## Esempio di utilizzo API (Python)
```python
import requests

response = requests.post("http://localhost:5000/predict", json={"review": "Pessimo prodotto, non lo consiglio."})
print(response.json())
```
