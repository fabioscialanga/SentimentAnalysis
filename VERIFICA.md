# 🔍 Guida alla Verifica del Deployment

Questa guida ti aiuta a verificare che tutti i componenti del sistema di Sentiment Analysis siano configurati e funzionanti correttamente.

## 📋 Metodi di Verifica

### 1. Script Automatico di Verifica (Consigliato)

Lo script `verify_deployment.py` esegue automaticamente tutte le verifiche necessarie.

#### Prerequisiti
```bash
pip install requests
```

#### Esecuzione
```bash
# Verifica completa
python verify_deployment.py

# Con variabili ambiente personalizzate
set API_URL=http://localhost:5000
set PROMETHEUS_URL=http://localhost:9090
set GRAFANA_URL=http://localhost:3000
python verify_deployment.py
```

Lo script verifica:
- ✅ Struttura dei file del progetto
- ✅ Test unitari
- ✅ Endpoint API (health, predict, metrics)
- ✅ Servizi Docker (se in uso)
- ✅ Deployment Kubernetes (se in uso)
- ✅ Prometheus (raccolta metriche)
- ✅ Grafana (accessibilità)
- ✅ Configurazioni

### 2. Verifica Manuale Passo-Passo

#### 2.1 Verifica Struttura File

Controlla che tutti i file necessari siano presenti:

```bash
# Windows PowerShell
Test-Path api/app.py
Test-Path docker-compose.yml
Test-Path k8s/sentiment-stack.yaml
Test-Path monitoring/prometheus.yml

# Linux/Mac
ls -la api/app.py docker-compose.yml k8s/sentiment-stack.yaml
```

#### 2.2 Esegui Test Unitari

```bash
cd api
python -m pytest tests/test_app.py -v
cd ..
```

**Risultato atteso**: Tutti i test devono passare.

#### 2.3 Verifica API

##### Health Check
```bash
curl http://localhost:5000/health
```

**Risultato atteso**:
```json
{"status": "ok"}
```

##### Test Predizione
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"review\": \"This product is amazing!\"}"
```

**Risultato atteso**:
```json
{
  "sentiment": "positive",
  "confidence": 0.95
}
```

##### Metriche Prometheus
```bash
curl http://localhost:5000/metrics
```

**Risultato atteso**: Dovresti vedere metriche come:
- `request_count`
- `request_latency_seconds`
- `prediction_errors_total`
- `auth_failures_total`

#### 2.4 Verifica Docker Compose

```bash
# Controlla servizi in esecuzione
docker-compose ps

# Verifica log
docker-compose logs sentiment-api
docker-compose logs prometheus
docker-compose logs grafana
```

**Risultato atteso**: Tutti e tre i servizi devono essere in stato "Up".

#### 2.5 Verifica Kubernetes

```bash
# Verifica namespace
kubectl get namespace sentiment

# Verifica pod
kubectl get pods -n sentiment

# Verifica servizi
kubectl get svc -n sentiment

# Verifica log
kubectl logs -n sentiment -l app=sentiment-api
```

**Risultato atteso**:
- Namespace `sentiment` presente
- Pod in stato "Running"
- Servizi esposti correttamente

#### 2.6 Verifica Prometheus

1. **Accesso Web**: Apri `http://localhost:9090`

2. **Verifica Target**:
   - Vai su "Status" → "Targets"
   - Il target `sentiment-api:5000` deve essere "UP"

3. **Verifica Metriche**:
   - Vai su "Graph"
   - Esegui query: `request_count`
   - Dovresti vedere metriche raccolte

4. **API Check**:
```bash
curl http://localhost:9090/api/v1/targets
```

#### 2.7 Verifica Grafana

1. **Accesso Web**: Apri `http://localhost:3000`
   - Username: `admin`
   - Password: (dal file `.env` o Secret Kubernetes)

2. **Verifica Datasource**:
   - Vai su "Configuration" → "Data Sources"
   - Dovresti vedere "Prometheus" configurato

3. **Verifica Dashboard**:
   - Vai su "Dashboards"
   - Dovresti vedere "Sentiment API - Overview"

4. **API Check**:
```bash
curl http://localhost:3000/api/health
```

**Risultato atteso**:
```json
{"database":"ok","version":"..."}
```

### 3. Checklist Rapida

Usa questa checklist per una verifica veloce:

- [ ] File `.env` configurato (o Secret Kubernetes)
- [ ] Test unitari passano (`pytest api/tests/test_app.py`)
- [ ] API risponde a `/health`
- [ ] API risponde a `/predict` con recensioni di test
- [ ] API espone metriche su `/metrics`
- [ ] Docker Compose: tutti i servizi "Up" (se in uso)
- [ ] Kubernetes: pod in "Running" (se in uso)
- [ ] Prometheus: target "UP" e metriche raccolte
- [ ] Grafana: accessibile e datasource configurato
- [ ] Dashboard Grafana mostra dati

## 🐛 Troubleshooting

### API non raggiungibile

**Problema**: `curl http://localhost:5000/health` fallisce

**Soluzioni**:
1. Verifica che il servizio sia in esecuzione:
   ```bash
   docker-compose ps
   # o
   kubectl get pods -n sentiment
   ```

2. Controlla i log:
   ```bash
   docker-compose logs sentiment-api
   # o
   kubectl logs -n sentiment -l app=sentiment-api
   ```

3. Verifica che la porta 5000 non sia già in uso:
   ```bash
   # Windows
   netstat -an | findstr 5000
   
   # Linux/Mac
   lsof -i :5000
   ```

### Prometheus non raccoglie metriche

**Problema**: Nessuna metrica in Prometheus

**Soluzioni**:
1. Verifica che l'API esponga metriche:
   ```bash
   curl http://localhost:5000/metrics
   ```

2. Verifica la configurazione Prometheus:
   ```bash
   docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
   ```

3. Controlla i target in Prometheus UI: `http://localhost:9090/targets`

### Grafana non mostra dati

**Problema**: Dashboard vuota

**Soluzioni**:
1. Verifica che Prometheus sia configurato come datasource
2. Controlla che Prometheus stia raccogliendo metriche
3. Verifica le query nella dashboard (potrebbero essere errate)

### Test falliscono

**Problema**: `pytest` fallisce

**Soluzioni**:
1. Installa le dipendenze:
   ```bash
   pip install -r api/requirements.txt
   pip install pytest
   ```

2. Verifica che l'API sia in esecuzione (per alcuni test)

3. Controlla i log di pytest per dettagli

## 📊 Interpretazione dei Risultati

### Script di Verifica

Lo script `verify_deployment.py` restituisce:

- **Exit code 0**: Tutte le verifiche passate (100%)
- **Exit code 1**: La maggior parte delle verifiche passate (≥70%)
- **Exit code 2**: Molte verifiche fallite (<70%)

### Cosa Significa Ogni Verifica

| Verifica | Cosa Controlla | Criticità |
|----------|---------------|-----------|
| Struttura File | File necessari presenti | Media |
| Test Unitari | Funzionalità base API | **Alta** |
| Endpoint API | API funzionante | **Alta** |
| Servizi Docker | Container in esecuzione | Media |
| Kubernetes | Pod e servizi OK | Media |
| Prometheus | Raccolta metriche | Media |
| Grafana | Dashboard accessibile | Bassa |
| Configurazioni | File config validi | Media |

## 🎯 Verifica Rapida (1 minuto)

Per una verifica veloce, esegui solo questi comandi:

```bash
# 1. Health check API
curl http://localhost:5000/health

# 2. Test predizione
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"review\": \"Great product!\"}"

# 3. Verifica servizi (Docker)
docker-compose ps

# 4. Verifica pod (Kubernetes)
kubectl get pods -n sentiment
```

Se tutti questi comandi funzionano, il sistema è operativo! 🎉

## 📝 Note

- Lo script di verifica può richiedere alcuni minuti per completarsi
- Alcune verifiche richiedono che i servizi siano già in esecuzione
- Le verifiche di Prometheus e Grafana richiedono che i servizi siano accessibili
- In produzione, considera di aggiungere verifiche di sicurezza e performance

