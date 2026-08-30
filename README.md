# AI Swing Trade Assistant

## Prerequisites

- Python 3.11+
- Node.js 18+ (frontend only)
- AWS CLI

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

Optional local config (non-secrets only; do not commit `.env`):

```bash
copy .env.example .env
```

Secrets (`JWT_SECRET`, DynamoDB access keys) are loaded from **AWS SSM Parameter Store** at startup. Ensure your AWS CLI profile (`aws configure`) can call `ssm:GetParameters` on:

- `DB_ACCESS_KEY_ID`
- `DB_SECRET_ACCESS_KEY`
- `JWT_SECRET`

Optional `.env` keys: `AWS_REGION`, `DYNAMODB_TABLE` (default `users`), `CHAT_DYNAMODB_TABLE` (default `conversations`).

Create the `conversations` DynamoDB table (partition key `user_email`, sort key `conversation_id`, both strings).

Auth API (DynamoDB table `users`, partition key `email`):

- `POST /auth/signup` — create account (bcrypt-hashed password)
- `POST /auth/login` — returns JWT
- `POST /auth/logout` — requires `Authorization: Bearer <token>`
- `GET /auth/me` — validate session

Chat API (DynamoDB table `conversations`; requires JWT):

- `POST /analyze` — analyze a stock query; saves user query and AI response for the logged-in user
- `GET /chat/history` — list saved conversations for the logged-in user

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
