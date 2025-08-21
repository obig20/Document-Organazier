cd "C:\Users\USER\Downloads\mmmmmm-main (1)\backend"
winget install -e --id UB-Mannheim.TesseractOCR
if (Test-Path .\venv\Scripts\Activate.ps1) { . .\venv\Scripts\Activate.ps1 } else { py -3 -m venv venv; . .\venv\Scripts\Activate.ps1 }
pip install -r .\requirements.txt
$env:PYTHONPATH = "$PWD"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload