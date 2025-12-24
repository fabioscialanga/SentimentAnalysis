# Script per pubblicare il progetto su GitHub
# Prima di eseguire questo script:
# 1. Crea un nuovo repository su GitHub (https://github.com/new)
#    - NON inizializzarlo con README, .gitignore o licenza
# 2. Sostituisci GITHUB_USERNAME e REPO_NAME nelle variabili qui sotto

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "SentimentAnalysis"
)

$RepoUrl = "https://github.com/$GitHubUsername/$RepoName.git"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Pubblicazione progetto su GitHub" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository URL: $RepoUrl" -ForegroundColor Yellow
Write-Host ""

# Verifica che Git sia installato
try {
    $gitVersion = git --version
    Write-Host "✓ Git trovato: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git non trovato. Installa Git prima di continuare." -ForegroundColor Red
    exit 1
}

# Verifica se esiste già un remote
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "⚠ Remote 'origin' già configurato: $existingRemote" -ForegroundColor Yellow
    $overwrite = Read-Host "Vuoi sovrascriverlo? (s/n)"
    if ($overwrite -ne "s" -and $overwrite -ne "S") {
        Write-Host "Operazione annullata." -ForegroundColor Yellow
        exit 0
    }
    git remote remove origin
    Write-Host "✓ Remote rimosso" -ForegroundColor Green
}

# Aggiungi il remote
Write-Host ""
Write-Host "Aggiungo remote GitHub..." -ForegroundColor Cyan
git remote add origin $RepoUrl
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Remote aggiunto con successo" -ForegroundColor Green
} else {
    Write-Host "✗ Errore nell'aggiungere il remote" -ForegroundColor Red
    exit 1
}

# Verifica che siamo sul branch main
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host ""
    Write-Host "Rinomino branch corrente in 'main'..." -ForegroundColor Cyan
    git branch -M main
    Write-Host "✓ Branch rinominato in 'main'" -ForegroundColor Green
}

# Push del codice
Write-Host ""
Write-Host "Pubblico il codice su GitHub..." -ForegroundColor Cyan
Write-Host "Questo potrebbe richiedere l'autenticazione GitHub." -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✓ Progetto pubblicato con successo!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository disponibile su:" -ForegroundColor Cyan
    Write-Host "  $RepoUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Prossimi passi:" -ForegroundColor Cyan
    Write-Host "  1. Visita il repository su GitHub" -ForegroundColor White
    Write-Host "  2. Configura GitHub Actions (opzionale)" -ForegroundColor White
    Write-Host "  3. Configura Jenkins per usare questo repository" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Errore durante il push. Verifica:" -ForegroundColor Red
    Write-Host "  - Il repository esiste su GitHub" -ForegroundColor Yellow
    Write-Host "  - Hai le credenziali corrette" -ForegroundColor Yellow
    Write-Host "  - Hai i permessi per scrivere sul repository" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Per autenticazione, puoi usare:" -ForegroundColor Cyan
    Write-Host "  - Personal Access Token (consigliato)" -ForegroundColor White
    Write-Host "  - GitHub CLI (gh auth login)" -ForegroundColor White
    Write-Host ""
}

