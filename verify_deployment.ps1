# Script PowerShell per verifica rapida su Windows
# Esegue controlli base del sistema Sentiment Analysis

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICA RAPIDA DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Funzione helper
function Test-Command {
    param($Command, $Description)
    try {
        $result = Get-Command $Command -ErrorAction Stop
        Write-Host "✓ $Description" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ $Description (comando non trovato)" -ForegroundColor Red
        return $false
    }
}

function Test-URL {
    param($URL, $Description)
    try {
        $response = Invoke-WebRequest -Uri $URL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $Description" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ $Description (status: $($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "⚠ $Description (non raggiungibile: $($_.Exception.Message))" -ForegroundColor Yellow
        $script:warnings++
        return $false
    }
}

# 1. Verifica comandi disponibili
Write-Host "`n[1] Verifica Prerequisiti" -ForegroundColor Yellow
$hasDocker = Test-Command "docker" "Docker installato"
$hasDockerCompose = Test-Command "docker-compose" "Docker Compose installato"
$hasKubectl = Test-Command "kubectl" "kubectl installato"
$hasPython = Test-Command "python" "Python installato"

# 2. Verifica file
Write-Host "`n[2] Verifica File Progetto" -ForegroundColor Yellow
$requiredFiles = @(
    "api\app.py",
    "docker-compose.yml",
    "k8s\sentiment-stack.yaml",
    "monitoring\prometheus.yml"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ File presente: $file" -ForegroundColor Green
    } else {
        Write-Host "✗ File mancante: $file" -ForegroundColor Red
        $errors++
    }
}

# 3. Verifica servizi Docker
Write-Host "`n[3] Verifica Servizi Docker" -ForegroundColor Yellow
if ($hasDockerCompose) {
    try {
        $services = docker-compose ps --format json 2>$null | ConvertFrom-Json
        if ($services) {
            $running = ($services | Where-Object { $_.State -eq "running" }).Count
            Write-Host "✓ Servizi Docker: $running in esecuzione" -ForegroundColor Green
        } else {
            Write-Host "⚠ Nessun servizio Docker in esecuzione" -ForegroundColor Yellow
            $warnings++
        }
    } catch {
        Write-Host "⚠ Impossibile verificare servizi Docker" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "⚠ Docker Compose non disponibile" -ForegroundColor Yellow
    $warnings++
}

# 4. Verifica Kubernetes
Write-Host "`n[4] Verifica Kubernetes" -ForegroundColor Yellow
if ($hasKubectl) {
    try {
        $namespace = kubectl get namespace sentiment 2>$null
        if ($namespace) {
            Write-Host "✓ Namespace 'sentiment' presente" -ForegroundColor Green
            
            $pods = kubectl get pods -n sentiment --no-headers 2>$null
            if ($pods) {
                $runningPods = ($pods | Where-Object { $_ -match "Running" }).Count
                Write-Host "✓ Pod in esecuzione: $runningPods" -ForegroundColor Green
            } else {
                Write-Host "⚠ Nessun pod trovato" -ForegroundColor Yellow
                $warnings++
            }
        } else {
            Write-Host "⚠ Namespace 'sentiment' non trovato" -ForegroundColor Yellow
            $warnings++
        }
    } catch {
        Write-Host "⚠ Impossibile verificare Kubernetes" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "⚠ kubectl non disponibile" -ForegroundColor Yellow
    $warnings++
}

# 5. Verifica API
Write-Host "`n[5] Verifica API" -ForegroundColor Yellow
$apiHealth = Test-URL "http://localhost:5000/health" "Health check API"
if (-not $apiHealth) { $errors++ }

# Test predizione
try {
    $body = @{ review = "This is a great product!" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:5000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 10 `
        -ErrorAction Stop
    
    if ($response.sentiment -and $response.confidence) {
        Write-Host "✓ Endpoint /predict funzionante (sentiment: $($response.sentiment))" -ForegroundColor Green
    } else {
        Write-Host "✗ Risposta /predict incompleta" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host "⚠ Endpoint /predict non raggiungibile: $($_.Exception.Message)" -ForegroundColor Yellow
    $warnings++
}

# 6. Verifica Prometheus
Write-Host "`n[6] Verifica Prometheus" -ForegroundColor Yellow
$prometheusHealth = Test-URL "http://localhost:9090/-/healthy" "Health check Prometheus"
if (-not $prometheusHealth) { $warnings++ }

# 7. Verifica Grafana
Write-Host "`n[7] Verifica Grafana" -ForegroundColor Yellow
$grafanaHealth = Test-URL "http://localhost:3000/api/health" "Health check Grafana"
if (-not $grafanaHealth) { $warnings++ }

# Riepilogo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RIEPILOGO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✓ TUTTE LE VERIFICHE SONO PASSATE!" -ForegroundColor Green
    exit 0
} elseif ($errors -eq 0) {
    Write-Host "✓ Verifiche critiche passate" -ForegroundColor Green
    Write-Host "⚠ $warnings avvisi (non critici)" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✗ $errors errori trovati" -ForegroundColor Red
    if ($warnings -gt 0) {
        Write-Host "⚠ $warnings avvisi" -ForegroundColor Yellow
    }
    Write-Host "`nControlla i dettagli sopra per risolvere i problemi." -ForegroundColor Yellow
    exit 1
}

