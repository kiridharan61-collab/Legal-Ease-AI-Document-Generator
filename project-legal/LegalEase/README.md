# LegalEase — AI-Powered Legal Document Generator

LegalEase is a Streamlit + FastAPI application for generating editable legal-document templates with Google's Gemini API and exporting them as TXT, DOCX, or PDF.

## What is included

- Streamlit frontend
- FastAPI backend
- Gemini AI integration
- Editable document preview
- TXT export
- DOCX export with optional logo and key-terms table
- PDF export with header/footer and optional logo
- Input validation with Pydantic
- Environment-variable configuration
- Automated tests
- Dockerfile and Procfile

## Important model note

The original project document selects `gemini-1.5-pro`. That model was shut down by Google on September 29, 2025, so this implementation uses the current Google GenAI SDK and a configurable current model. The default is `gemini-3.8-flash`; you can change `GEMINI_MODEL` in `.env`.

## Project structure

```text
LegalEase/
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── routes.py
├── utils/
│   ├── __init__.py
│   ├── exporters.py
│   └── sanitize.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_sanitize.py
├── app.py
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── requirements.txt
├── run_backend.bat
└── run_frontend.bat
```

## Windows + VS Code setup

### 1. Install Python

Use Python 3.10 or newer. Python 3.12 is recommended for this project.

Verify:

```powershell
python --version
pip --version
```

### 2. Open the project in VS Code

Open the `LegalEase` folder, not an individual file.

### 3. Create a virtual environment

In the VS Code terminal:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt in VS Code:

```cmd
.venv\Scripts\activate.bat
```

### 4. Select the Python interpreter

In VS Code:

1. Press `Ctrl+Shift+P`
2. Select `Python: Select Interpreter`
3. Choose the interpreter inside `.venv`

### 5. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Gemini

Copy:

```text
.env.example
```

to:

```text
.env
```

Then edit `.env`:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
GEMINI_MODEL=gemini-3.8-flash
BACKEND_URL=http://127.0.0.1:8000
```

Never commit `.env` to Git.

## Run the application

You need two VS Code terminals.

### Terminal 1 — FastAPI

```powershell
.venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2 — Streamlit

```powershell
.venv\Scripts\activate
streamlit run app.py
```

Streamlit normally opens:

```text
http://localhost:8501
```

## Test the project

Run:

```powershell
pytest -q
```

The API test mocks Gemini, so the automated tests do not consume your API quota.

## Manual end-to-end test

1. Start FastAPI.
2. Start Streamlit.
3. Choose `Employment Contract`.
4. Enter parties, for example:
   `Jane Doe (Employee), ABC Corp (Employer)`
5. Enter terms separated with semicolons:
   `Monthly payment; Confidentiality applies; Either party may terminate with 15 days notice`
6. Select an effective date.
7. Click `Generate Document`.
8. Edit the generated text.
9. Download TXT, DOCX, and PDF.
10. Open each file and verify the formatting.

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure the file is named exactly `.env` and is located in the project root beside `app.py`.

### `Could not reach the backend`

Make sure this command is running:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Also check the Streamlit sidebar `Backend URL`.

### `ModuleNotFoundError`

Make sure the virtual environment is active and run:

```powershell
pip install -r requirements.txt
```

### PowerShell says scripts are disabled

Use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

or change the PowerShell execution policy only if you are allowed to do so on your computer.

## API example

POST `/generate`

```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Jane Doe (Disclosing Party), ABC Corp (Receiving Party)",
  "terms": "Confidential information must be protected; Agreement lasts two years",
  "effective_date": "2026-09-23"
}
```

The response is:

```json
{
  "document_type": "Non-Disclosure Agreement",
  "content": "..."
}
```

## Legal and security note

LegalEase generates templates and should not be presented as a replacement for qualified legal advice. For production deployment, restrict CORS to your real frontend domain, add authentication/rate limiting, avoid logging sensitive document contents, and use HTTPS.

## Architecture

```text
Streamlit
   |
   | POST /generate
   v
FastAPI
   |
   v
GeminiDocumentGenerator
   |
   v
Google Gemini API
   |
   v
Generated editable legal text
   |
   +--> TXT
   +--> DOCX
   +--> PDF
```
