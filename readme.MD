# AI-Edu-Assist-Chatbot

Django app with OpenAI integration.

## Requirements
- Python 3.11+ (or your version)
- pip
- (optional) virtualenv

## Setup
```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Create local env
copy .env.example .env   # Windows
# or:
cp .env.example .env     # macOS/Linux

# Run DB & server
python manage.py migrate
python manage.py runserver
