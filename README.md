# Deploy e Monitoraggio di un Modello di Sentiment Analysis per Recensioni

## 📋 Indice

- [Contesto Aziendale](#contesto-aziendale)
- [Obiettivi del Progetto](#obiettivi-del-progetto)
- [Panoramica del Sistema](#panoramica-del-sistema)
- [Architettura](#architettura)
- [Struttura del Progetto](#struttura-del-progetto)
- [Prerequisiti](#prerequisiti)
- [Installazione e Configurazione](#installazione-e-configurazione)
- [Utilizzo](#utilizzo)
- [Monitoraggio](#monitoraggio)
- [CI/CD con Jenkins](#cicd-con-jenkins)
- [Deploy su Kubernetes](#deploy-su-kubernetes)
- [Sicurezza](#sicurezza)
- [Troubleshooting](#troubleshooting)
- [Repository GitHub](#repository-github)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

---

## 🏢 Contesto Aziendale

Una piattaforma di e-commerce riceve migliaia di recensioni sui prodotti ogni giorno. Analizzare il sentimento di queste recensioni (positivo, negativo, neutro) è cruciale per:

- **Migliorare i prodotti**: Identificare rapidamente problemi segnalati dai clienti
- **Ottimizzare il servizio clienti**: Prioritarizzare le recensioni negative per risposte immediate
- **Decisioni basate sui dati**: Utilizzare insight quantitativi per guidare strategie di prodotto
- **Scalabilità**: Gestire volumi crescenti di recensioni senza intervento manuale

Questo progetto implementa un sistema automatizzato per il deploy e il monitoraggio di un modello di Sentiment Analysis, garantendo **scalabilità**, **affidabilità** e **monitoraggio proattivo**.

---

## 🎯 Obiettivi del Progetto

1. **Implementare un modello di Sentiment Analysis** utilizzando un framework di Machine Learning (scikit-learn)
2. **Creare un pipeline CI/CD** con Jenkins per automatizzare il deploy del modello
3. **Configurare un'infrastruttura di monitoraggio** con Prometheus e Grafana per metriche in tempo reale
4. **Documentare e gestire il progetto** su repository GitHub

---

## 🏗️ Panoramica del Sistema

Il sistema è composto da API REST Flask, Prometheus per il monitoraggio, Grafana per le dashboard, Jenkins per CI/CD e Docker/Kubernetes per il deploy.

---

## 🏛️ Architettura

### Architettura con Docker Compose

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │  Flask API   │───▶│  Prometheus  │                  │
│  │  :5000       │    │  :9090       │                  │
│  └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                           │
│         │                   ▼                           │
│         │            ┌──────────────┐                   │
│         └───────────▶│   Grafana    │                   │
│                      │   :3000      │                   │
│                      └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

### Architettura Kubernetes

Il sistema può essere deployato su Kubernetes utilizzando i manifest nella directory `k8s/`, che includono namespace, deployment, service, ConfigMap e Secret.

---

## 📁 Struttura del Progetto

```
SentimentAnalysis/
│
├── api/                          # API Flask
│   ├── app.py                    # Applicazione principale Flask
│   ├── Dockerfile                # Immagine Docker per l'API
│   ├── requirements.txt         # Dipendenze Python
│   ├── templates/
│   │   └── index.html           # Pagina web di test
│   └── tests/
│       └── test_app.py           # Test unitari
│
├── monitoring/                   # Configurazioni monitoraggio
│   ├── prometheus.yml           # Configurazione Prometheus
│   ├── alerts.yml               # Regole di alerting
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   │   └── datasource.yml    # Datasource Prometheus
│       │   └── dashboards/
│       │       └── dashboard.yml     # Configurazione dashboard
│       └── dashboards/
│           └── sentiment-overview.json  # Dashboard principale
│
├── jenkins/                      # Pipeline CI/CD
│   └── Jenkinsfile              # Definizione pipeline Jenkins
│
├── k8s/                         # Manifest Kubernetes
│   └── sentiment-stack.yaml     # Stack completo Kubernetes
│
├── docker-compose.yml           # Orchestrazione servizi locali
├── env.example                  # Template variabili ambiente
├── .gitignore                   # File esclusi da Git
└── README.md                    # Questa documentazione
```

---

## 🔧 Prerequisiti

### Software Richiesto

- **Docker** (versione 20.10+)
- **Docker Compose** (versione 2.0+)
- **Python 3.9+** (opzionale, solo per test locali)
- **Git** (per clonare il repository)

### Per Deploy Kubernetes

- **kubectl** configurato e connesso a un cluster Kubernetes
- Cluster Kubernetes funzionante (minikube, kind, o cloud provider)

### Per CI/CD Jenkins

- **Jenkins** installato e configurato
- Plugin Docker installato su Jenkins
- Accesso a Docker da Jenkins

---

## 🚀 Installazione e Configurazione

### 1. Clonare il Repository

```bash
git clone https://github.com/TUO-USERNAME/SentimentAnalysis.git
cd SentimentAnalysis
```

### 2. Configurare le Variabili Ambiente

Crea un file `.env` basato su `env.example`:

```bash
cp env.example .env
```

Modifica `.env` con i tuoi valori:

```env
# Password amministratore Grafana
GF_SECURITY_ADMIN_PASSWORD=tua_password_sicura

# Token Bearer per autenticazione API (opzionale)
API_TOKEN=il_tuo_token_segreto

# URL del modello (default: repository pubblico)
MODEL_URL=https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl
```

**⚠️ Importante**: Il file `.env` è escluso da Git per sicurezza. Non committarlo mai!

### 3. Avviare i Servizi con Docker Compose

    ```bash
    docker-compose up -d --build
    ```

Questo comando:
- Costruisce l'immagine Docker dell'API
- Scarica le immagini di Prometheus e Grafana
- Avvia tutti i servizi in background

### 4. Verificare lo Stato dei Servizi

```bash
docker-compose ps
```

Dovresti vedere tre servizi in esecuzione:
- `sentiment-api`
- `prometheus`
- `grafana`

### 5. Verificare i Log

```bash
# Log di tutti i servizi
docker-compose logs -f

# Log solo dell'API
docker-compose logs -f sentiment-api
```

---

## 💻 Utilizzo

### Endpoint API Disponibili

#### 1. **GET /** - Pagina Web di Test

Accesso: `http://localhost:5000`

Interfaccia web semplice per testare l'API.

#### 2. **POST /predict** - Analisi Sentiment

Endpoint principale per analizzare il sentiment di una recensione.

**Richiesta**:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"review": "This product is amazing! I love it."}'
```

**Con Autenticazione** (se `API_TOKEN` è configurato):
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer il_tuo_token_segreto" \
  -d '{"review": "This product is amazing! I love it."}'
```

**Risposta**:
```json
{
  "sentiment": "positive",
  "confidence": 0.95
}
```

**Possibili valori di `sentiment`**:
- `"positive"`: Sentimento positivo
- `"negative"`: Sentimento negativo
- `"neutral"`: Sentimento neutro (se supportato dal modello)

**Codici di Risposta**:
- `200 OK`: Predizione riuscita
- `400 Bad Request`: Richiesta malformata (manca campo `review`)
- `401 Unauthorized`: Token mancante o non valido (se autenticazione attiva)
- `500 Internal Server Error`: Errore durante la predizione

#### 3. **GET /health** - Health Check

Verifica lo stato dell'API.

```bash
curl http://localhost:5000/health
```

**Risposta**:
```json
{
  "status": "ok"
}
```

#### 4. **GET /metrics** - Metriche Prometheus

Espone le metriche in formato Prometheus.

```bash
curl http://localhost:5000/metrics
```

**Metriche Esposte**:
- `request_count`: Contatore delle richieste per metodo, endpoint e status HTTP
- `request_latency_seconds`: Istogramma della latenza delle richieste
- `prediction_errors_total`: Contatore degli errori di predizione
- `auth_failures_total`: Contatore dei fallimenti di autenticazione

### Esempi di Utilizzo

#### Python

```python
import requests

# Configurazione
API_URL = "http://localhost:5000"
API_TOKEN = "il_tuo_token_segreto"  # Opzionale

# Headers
headers = {
    "Content-Type": "application/json"
}
if API_TOKEN:
    headers["Authorization"] = f"Bearer {API_TOKEN}"

# Analisi sentiment
response = requests.post(
    f"{API_URL}/predict",
    json={"review": "This product exceeded my expectations!"},
    headers=headers
)

result = response.json()
print(f"Sentiment: {result['sentiment']}")
print(f"Confidence: {result['confidence']:.2%}")
```


---

## 📊 Monitoraggio

### Prometheus

**Accesso**: `http://localhost:9090`

Prometheus raccoglie automaticamente le metriche dall'API ogni 15 secondi.

#### Query Utili

**Numero totale di richieste**:
```promql
sum(rate(request_count[5m]))
```

**Latenza p95**:
```promql
histogram_quantile(0.95, sum(rate(request_latency_seconds_bucket[5m])) by (le))
```

**Tasso di errori**:
```promql
rate(prediction_errors_total[5m])
```

**Throughput per endpoint**:
```promql
sum(rate(request_count[5m])) by (endpoint)
```

### Grafana

**Accesso**: `http://localhost:3000`

**Credenziali**:
- Username: `admin`
- Password: Valore di `GF_SECURITY_ADMIN_PASSWORD` nel file `.env`

#### Dashboard Preconfigurata

Il sistema include una dashboard preconfigurata **"Sentiment API - Overview"** che mostra:

1. **Richieste Totali**: Grafico a linea del numero di richieste nel tempo
2. **Errori di Predizione**: Contatore degli errori
3. **Fallimenti Autenticazione**: Contatore dei fallimenti auth
4. **Latenza p95**: Istogramma della latenza percentile 95
5. **Throughput**: Richieste al secondo per endpoint

La dashboard viene caricata automaticamente al primo avvio di Grafana grazie al provisioning.

#### Alerting

Prometheus include regole di alerting configurate in `monitoring/alerts.yml`:

1. **HighErrorRate**: Si attiva quando ci sono più di 5 errori di predizione in 5 minuti
2. **HighLatencyP95**: Si attiva quando la latenza p95 supera 1 secondo per più di 5 minuti

Gli alert possono essere visualizzati in Prometheus (`http://localhost:9090/alerts`) e configurati per inviare notifiche via email, Slack, ecc.

---

## 🔄 CI/CD con Jenkins

### Configurazione Jenkins

1. **Crea una nuova Pipeline**:
   - Vai su Jenkins → New Item
   - Seleziona "Pipeline"
   - Nome: `sentiment-analysis-pipeline`

2. **Configura il Repository**:
   - Pipeline definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: URL del tuo repository GitHub/GitLab
   - Script Path: `jenkins/Jenkinsfile`

3. **Configura Credenziali** (se necessario):
   - Se il repository è privato, aggiungi credenziali Git
   - Se usi Kubernetes, configura credenziali `kubectl`

### Pipeline Stages

Il `Jenkinsfile` definisce una pipeline con i seguenti stage:

1. **Checkout**: Scarica il codice dal repository
2. **Build**: Costruisce l'immagine Docker dell'API
3. **Test**: Esegue i test unitari con `pytest`
4. **Deploy**: 
   - Deploy con Docker Compose (default)
   - Deploy su Kubernetes (se `APPLY_K8S=true`)

### Parametri Pipeline

- `APPLY_K8S`: Se `true`, applica i manifest Kubernetes invece di Docker Compose

---

## ☸️ Deploy su Kubernetes

### Prerequisiti

- Cluster Kubernetes funzionante
- `kubectl` configurato e connesso al cluster
- Accesso per creare namespace, deployment, service, configmap e secret

### Deploy Completo

```bash
kubectl apply -f k8s/sentiment-stack.yaml
```

Questo comando crea:
- Namespace `sentiment-analysis`
- Secret con password Grafana e token API
- ConfigMap per Prometheus (configurazione + alerting)
- ConfigMap per provisioning Grafana
- Deployment e Service per API, Prometheus e Grafana

### Verificare il Deploy

```bash
# Verifica namespace
kubectl get namespace sentiment-analysis

# Verifica pod
kubectl get pods -n sentiment-analysis

# Verifica servizi
kubectl get svc -n sentiment-analysis

# Log dell'API
kubectl logs -n sentiment-analysis -l app=sentiment-api -f
```

### Accesso ai Servizi

#### Port Forwarding

```bash
# API
kubectl port-forward -n sentiment-analysis svc/sentiment-api 5000:5000

# Prometheus
kubectl port-forward -n sentiment-analysis svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n sentiment-analysis svc/grafana 3000:3000
```

### Aggiornare il Deploy

Dopo modifiche al codice:

```bash
# Ricostruisci l'immagine Docker
docker build -t sentiment-analysis-api:latest ./api

# Carica nel cluster (per minikube)
minikube image load sentiment-analysis-api:latest

# Riavvia i pod
kubectl rollout restart deployment/sentiment-api -n sentiment-analysis
```

---

## 🔒 Sicurezza

### Autenticazione API

L'API supporta autenticazione opzionale tramite token Bearer:

1. Imposta `API_TOKEN` nel file `.env`
2. Tutte le richieste (tranne `/`, `/health`, `/metrics`) richiedono l'header:
   ```
   Authorization: Bearer <token>
   ```

### Password Grafana

- **Non hardcodare** la password nel `docker-compose.yml`
- Utilizza sempre variabili ambiente tramite `.env`
- Cambia la password di default dopo il primo accesso

### Best Practices

- Mai committare file `.env` nel repository
- Utilizza Secret invece di ConfigMap per dati sensibili in Kubernetes
- Configura HTTPS/TLS in produzione

---

## 🐛 Troubleshooting

### Problema: API non risponde

**Sintomi**: `curl http://localhost:5000/health` restituisce errore di connessione

**Soluzioni**:
1. Verifica che il container sia in esecuzione: `docker-compose ps`
2. Controlla i log: `docker-compose logs sentiment-api`
3. Verifica che la porta 5000 non sia già in uso: `netstat -an | findstr 5000`

### Problema: Modello non caricato

**Sintomi**: L'API funziona ma usa il fallback TextBlob

**Soluzioni**:
1. Verifica che `MODEL_URL` sia corretto nel `.env`
2. Controlla i log per errori di download: `docker-compose logs sentiment-api`
3. Verifica la connettività di rete dal container: `docker-compose exec sentiment-api ping github.com`

### Problema: Grafana non mostra dati

**Sintomi**: Dashboard vuota o "No data"

**Soluzioni**:
1. Verifica che Prometheus stia raccogliendo metriche: `http://localhost:9090/targets`
2. Controlla che il datasource Prometheus sia configurato: Grafana → Configuration → Data Sources
3. Verifica che l'API esponga metriche: `curl http://localhost:5000/metrics`

### Problema: Prometheus non raccoglie metriche

**Sintomi**: Nessuna metrica in Prometheus

**Soluzioni**:
1. Verifica la configurazione: `docker-compose exec prometheus cat /etc/prometheus/prometheus.yml`
2. Controlla i target: `http://localhost:9090/targets` (dovrebbe mostrare `sentiment-api:5000` come UP)
3. Verifica la connettività di rete: `docker-compose exec prometheus ping sentiment-api`

### Problema: Jenkins pipeline fallisce

**Sintomi**: Build o test falliscono

**Soluzioni**:
1. Verifica che Docker sia accessibile da Jenkins
2. Controlla i log della pipeline in Jenkins
3. Verifica che le dipendenze Python siano installate per i test
4. Assicurati che il repository sia accessibile da Jenkins

---

## 📦 Repository GitHub

### Pubblicazione su GitHub

1. **Crea un nuovo repository** su GitHub:
   - Vai su https://github.com/new
   - Nome: `SentimentAnalysis` (o altro)
   - **Non** inizializzare con README, .gitignore o licenza (già presenti)

2. **Aggiungi il remote e pubblica**:
   ```bash
   git remote add origin https://github.com/TUO-USERNAME/SentimentAnalysis.git
   git branch -M main
   git push -u origin main
   ```

### Struttura del Repository

Il repository include:

- ✅ Codice sorgente completo dell'API Flask
- ✅ Configurazioni Docker e Docker Compose
- ✅ Manifest Kubernetes completi
- ✅ Pipeline CI/CD Jenkins
- ✅ Configurazioni Prometheus e Grafana
- ✅ Dashboard e alerting preconfigurati
- ✅ Test automatizzati
- ✅ Documentazione completa

---

## 🤝 Contribuire

1. Fork il repository
2. Crea un branch per la tua feature
3. Commit le modifiche
4. Push al branch
5. Apri una Pull Request

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT.

