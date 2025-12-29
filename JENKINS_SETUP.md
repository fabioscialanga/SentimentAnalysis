# Configurazione Jenkins per CI/CD Automatico

Questa guida spiega come configurare Jenkins per rilevare automaticamente i push e avviare la pipeline.

## Metodo 1: Polling SCM (Consigliato - Più Semplice)

Jenkins controlla periodicamente il repository per nuovi commit.

### Passi:

1. **Crea una nuova Pipeline in Jenkins:**
   - Vai su Jenkins → New Item
   - Nome: `sentiment-analysis-pipeline`
   - Tipo: Pipeline
   - Clicca OK

2. **Configura il Repository:**
   - Scorri fino a "Pipeline"
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: URL del tuo repository (es: `https://github.com/tuo-username/SentimentAnalysis.git`)
   - Credentials: Aggiungi credenziali se il repo è privato
   - Branch: `*/main` (o `*/master`)
   - Script Path: `jenkins/Jenkinsfile`

3. **Configura il Polling Automatico:**
   - Scorri fino a "Build Triggers"
   - Spunta "Poll SCM"
   - Schedule: `H/5 * * * *` (controlla ogni 5 minuti)
     - Oppure `* * * * *` (ogni minuto, per test)
     - Oppure `H * * * *` (ogni ora)

4. **Salva e Testa:**
   - Clicca "Save"
   - Clicca "Build Now" per testare manualmente
   - Dopo il primo build, ogni push attiverà automaticamente la pipeline

## Metodo 2: Webhook (Più Veloce - Richiede Configurazione)

GitHub/GitLab notifica Jenkins immediatamente quando c'è un push.

### Passi:

1. **Installa Plugin GitHub/GitLab in Jenkins:**
   - Manage Jenkins → Manage Plugins
   - Cerca "GitHub Plugin" o "GitLab Plugin"
   - Installa e riavvia Jenkins

2. **Configura Jenkins per Webhook:**
   - Manage Jenkins → Configure System
   - Sezione "GitHub"
   - Aggiungi GitHub Server
   - API URL: `https://api.github.com` (se GitHub)
   - Credentials: Aggiungi token GitHub

3. **Configura la Pipeline:**
   - Nella configurazione della pipeline
   - Build Triggers → "GitHub hook trigger for GITScm polling"
   - Salva

4. **Configura Webhook su GitHub/GitLab:**
   - Vai su Settings del repository
   - Webhooks → Add webhook
   - Payload URL: `http://tuo-jenkins-server:8080/github-webhook/`
   - Content type: `application/json`
   - Eventi: "Just the push event"
   - Salva

## Verifica Funzionamento

1. **Fai un commit e push:**
   ```bash
   git add .
   git commit -m "Test pipeline automatica"
   git push origin main
   ```

2. **Controlla Jenkins:**
   - Dopo qualche minuto (polling) o immediatamente (webhook)
   - Dovresti vedere un nuovo build nella pipeline
   - Il build partirà automaticamente

## Troubleshooting

### La pipeline non si avvia automaticamente:

1. **Verifica il polling:**
   - Vai nella configurazione della pipeline
   - Controlla che "Poll SCM" sia spuntato
   - Verifica lo schedule

2. **Verifica le credenziali:**
   - Se il repo è privato, assicurati che le credenziali siano corrette
   - Testa la connessione al repository

3. **Controlla i log:**
   - Vai su "View Configuration"
   - Clicca "Polling Log" per vedere quando Jenkins controlla il repo

### La pipeline fallisce:

1. **Verifica che Docker sia accessibile:**
   - Jenkins deve poter eseguire comandi `docker`
   - Aggiungi l'utente Jenkins al gruppo docker (Linux) o configura Docker Desktop (Windows)

2. **Verifica i permessi:**
   - Jenkins deve poter eseguire `docker-compose` o `kubectl`
   - Verifica i path e le variabili d'ambiente

## Schedule Polling (Cron Syntax)

Esempi di schedule per il polling:

- `* * * * *` - Ogni minuto (solo per test)
- `H/5 * * * *` - Ogni 5 minuti
- `H * * * *` - Ogni ora
- `H H * * *` - Una volta al giorno
- `H H * * 1-5` - Solo giorni lavorativi

La `H` distribuisce i build nel tempo per evitare picchi di carico.

