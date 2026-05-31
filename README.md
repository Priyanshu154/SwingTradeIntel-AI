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

Deploy (by default creates both `users` and `conversations` DynamoDB tables):

```bash
npx serverless deploy
```

Create tables one at a time when one already exists outside the stack:

```bash
# Only users table already exists — create conversations table
CREATE_USERS_TABLE=false CREATE_CONVERSATIONS_TABLE=true npx serverless deploy

# Only conversations table already exists — create users table
CREATE_USERS_TABLE=true CREATE_CONVERSATIONS_TABLE=false npx serverless deploy

# Both tables already exist — skip table resources
CREATE_USERS_TABLE=false CREATE_CONVERSATIONS_TABLE=false npx serverless deploy
```

PowerShell:

```powershell
$env:CREATE_USERS_TABLE="false"; $env:CREATE_CONVERSATIONS_TABLE="true"; npx serverless deploy
```

Tables use `DeletionPolicy: Retain` so data is kept if you remove the stack. If a table exists outside CloudFormation, set its flag to `false` or [import it into the stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import.html).

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
