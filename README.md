# AI Swing Trade Assistant

## Prerequisites

- Python 3.11+
- Node.js 18+
- AWS CLI
- Docker Desktop

Configure AWS credentials:

```bash
aws configure
```

---

## Frontend Setup (UI)

Navigate to UI directory:

```bash
cd ui
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Backend Setup (FastAPI)

Navigate to backend directory:

```bash
cd server
```

Create virtual environment (first time only):

```bash
python -m venv venv
```

Activate virtual environment:

### Windows CMD

```cmd
venv\Scripts\activate
```

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Serverless Deployment

Navigate to backend directory:

```bash
cd server
```

Install Node dependencies (first time only):

```bash
npm install
```

Ensure Docker Desktop is running:

```bash
docker ps
```

Deploy:

```bash
npx serverless deploy
```

Force redeploy:

```bash
npx serverless deploy --force
```

View logs:

```bash
npx serverless logs -f api --tail
```

Remove deployed resources:

```bash
npx serverless remove
```
