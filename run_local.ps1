# Avvio ambiente locale flask
Write-Host "Aggiornamento dipendenze..."
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\activate
pip install -r api/requirements.txt
python -m textblob.download_corpora

Write-Host "Avvio dell'API Flask..."
Write-Host "L'API sarà disponibile su http://localhost:5000"
python api/app.py
