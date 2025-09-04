HealthBot — Rasa-based preventive health chatbot

Quick start (local, development)

1) Create a Python venv and install dependencies:

	powershell:
	```powershell
	python -m venv .venv; .\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	```

2) Set required environment variables (example):

	```powershell
	$env:TWILIO_ACCOUNT_SID="<your-sid>"; $env:TWILIO_AUTH_TOKEN="<your-token>"; $env:TWILIO_NUMBER="whatsapp:+1415..."; $env:GOV_API_BASE="https://api.yourgov.example"
	```

3) Run action server and rasa server (in separate terminals):

	```powershell
	# run actions
	rasa run actions

	# in another terminal, run rasa
	rasa shell
	```

Notes
- Credentials are loaded from `backend/credentials.yml` which references environment variables; do not commit real secrets to the repo.
- Replace the in-memory subscriber store in `backend/actions/actions.py` with a persistent DB for production.
