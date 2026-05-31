from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum
import random

from auth import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    get_current_user,
    login_user,
    signup_user,
)
from chat_history import list_conversations, save_conversation

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    query: str


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "ai-swing-trade-assistant"
    }


@app.post("/auth/signup", response_model=AuthResponse)
def auth_signup(request: SignupRequest):
    return signup_user(request)


@app.post("/auth/login", response_model=AuthResponse)
def auth_login(request: LoginRequest):
    return login_user(request)


@app.post("/auth/logout")
def auth_logout(_user: str = Depends(get_current_user)):
    return {"message": "Logged out successfully"}


@app.get("/auth/me")
def auth_me(user: str = Depends(get_current_user)):
    return {"email": user}


@app.get("/chat/history")
def chat_history(user: str = Depends(get_current_user)):
    items = list_conversations(user)
    return {"conversations": items}


@app.post("/analyze")
def analyze_stock(
    request: AnalyzeRequest,
    user: str = Depends(get_current_user),
):
    ## Currently mocking response
    query = request.query.lower()

    bullish_keywords = [
        "buy",
        "bullish",
        "uptrend",
        "breakout",
        "momentum",
    ]

    bearish_keywords = [
        "sell",
        "bearish",
        "downtrend",
        "weak",
    ]

    sentiment_score = 0

    for keyword in bullish_keywords:
        if keyword in query:
            sentiment_score += 1

    for keyword in bearish_keywords:
        if keyword in query:
            sentiment_score -= 1

    if sentiment_score > 0:
        verdict = "BUY"
        sentiment = "Bullish"
        holding_period = "1-3 months"
    elif sentiment_score < 0:
        verdict = "SELL"
        sentiment = "Bearish"
        holding_period = "1-2 weeks"
    else:
        verdict = "HOLD"
        sentiment = "Neutral"
        holding_period = "Wait for confirmation"

    confidence = random.randint(65, 85)

    technical_summary = (
        "RSI indicates improving momentum while moving averages suggest moderate trend strength."
    )

    news_summary = (
        "Recent market sentiment appears stable with moderate sector participation."
    )

    response_text = f'''
Trade Verdict: {verdict}

Market Sentiment: {sentiment}

Suggested Holding Period: {holding_period}

Confidence Score: {confidence}%

Technical Analysis:
{technical_summary}

News Analysis:
{news_summary}

Final AI Thesis:
Based on current technical momentum and recent sentiment signals, the stock shows a {sentiment.lower()} outlook for swing trading.
'''

    response_body = response_text.strip()

    save_conversation(
        user,
        request.query,
        response_body,
        verdict=verdict,
        confidence=confidence,
        holding_period=holding_period,
    )

    return {
        "query": request.query,
        "verdict": verdict,
        "confidence": confidence,
        "holding_period": holding_period,
        "response": response_body,
    }


handler = Mangum(app)