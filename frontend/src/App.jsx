import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, guessTicker } from "./api/client";
import { useAuth } from "./context/AuthContext";

const SENTIMENT_COLOR = {
  Bullish: "text-emerald-400",
  Bearish: "text-rose-400",
  Neutral: "text-amber-400",
};

const VERDICT_COLOR = {
  BUY: "text-emerald-400",
  SELL: "text-rose-400",
  HOLD: "text-amber-400",
};

const DEFAULT_INSIGHT = {
  sentiment: "Neutral",
  confidence: "—",
  holding_period: "—",
};

const WELCOME_MESSAGE = {
  role: "assistant",
  kind: "text",
  content:
    'Hello! Ask me about any Nifty 50 stock for swing-trade analysis. Example: "Should I buy TCS for next 3 months?"',
};

function VerdictCard({ data }) {
  return (
    <div className="space-y-3 text-sm leading-6 text-slate-100">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Trade Verdict
          </p>
          <p
            className={`text-lg font-semibold ${
              VERDICT_COLOR[data.trade_verdict] ?? "text-white"
            }`}
          >
            {data.trade_verdict}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Market Sentiment
          </p>
          <p
            className={`text-lg font-semibold ${
              SENTIMENT_COLOR[data.market_sentiment] ?? "text-white"
            }`}
          >
            {data.market_sentiment}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Suggested Holding Period
          </p>
          <p className="font-medium">{data.suggested_holding_period}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Confidence Score
          </p>
          <p className="font-medium">{data.confidence_score}%</p>
        </div>
      </div>

      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">
          Technical Analysis
        </p>
        <p>{data.technical_analysis}</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">
          News Analysis
        </p>
        <p>{data.news_analysis}</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">
          Fundamental Analysis
        </p>
        <p>{data.fundamental_analysis}</p>
      </div>
      <div className="pt-2 border-t border-slate-800">
        <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">
          Final AI Thesis
        </p>
        <p className="text-slate-200">{data.final_thesis}</p>
      </div>
    </div>
  );
}

function sessionLabel(session) {
  const ticker = session.ticker?.replace(".NS", "") || "Analysis";
  const verdict = session.trade_verdict || "";
  return `${ticker}${verdict ? ` · ${verdict}` : ""}`;
}

export default function AISwingTradeChatbot() {
  const navigate = useNavigate();
  const { email, logout } = useAuth();
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [sessions, setSessions] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [insight, setInsight] = useState(DEFAULT_INSIGHT);

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      try {
        const response = await apiFetch("/history");
        if (!response.ok) return;
        const data = await response.json();
        if (!cancelled) {
          setSessions(data.sessions ?? []);
        }
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) setHistoryLoading(false);
      }
    }

    loadHistory();
    return () => {
      cancelled = true;
    };
  }, []);

  const applyInsight = (data) => {
    setInsight({
      sentiment: data.market_sentiment ?? "Neutral",
      confidence: data.confidence_score ?? "—",
      holding_period: data.suggested_holding_period ?? "N/A",
    });
  };

  const handleAnalyze = async (query = input) => {
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", kind: "text", content: query }]);
    setLoading(true);
    setInput("");

    try {
      const ticker = guessTicker(query);
      const response = await apiFetch("/analyze", {
        method: "POST",
        body: JSON.stringify({ query, ...(ticker ? { ticker } : {}) }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      applyInsight(data);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", kind: "verdict", content: data },
      ]);
      setSessions((prev) => [
        {
          sessionId: crypto.randomUUID(),
          timestamp: Date.now(),
          query,
          ticker: data.ticker,
          trade_verdict: data.trade_verdict,
          market_sentiment: data.market_sentiment,
          confidence_score: data.confidence_score,
          suggested_holding_period: data.suggested_holding_period,
          result: data,
        },
        ...prev,
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          kind: "text",
          content:
            error.message ||
            "Something went wrong while analyzing the stock. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const openSession = (session) => {
    if (session.result) {
      applyInsight(session.result);
      setMessages([
        WELCOME_MESSAGE,
        { role: "user", kind: "text", content: session.query },
        { role: "assistant", kind: "verdict", content: session.result },
      ]);
      return;
    }
    handleAnalyze(session.query);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            AI Swing Trade Research Assistant
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Multi-Agent GenAI powered market analysis · Nifty 50
          </p>
        </div>

        <div className="flex items-center gap-3">
          {email && (
            <span className="text-sm text-slate-400 hidden sm:inline">{email}</span>
          )}
          <div className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm border border-emerald-500/20">
            Bedrock Connected
          </div>
          <button
            type="button"
            onClick={async () => {
              await logout();
              navigate("/login", { replace: true });
            }}
            className="px-4 py-2 rounded-xl border border-slate-700 hover:border-slate-500 hover:bg-slate-800 transition text-sm"
          >
            Log out
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-80 border-r border-slate-800 bg-slate-900/40 hidden lg:flex flex-col">
          <div className="p-4 border-b border-slate-800">
            <button
              type="button"
              onClick={() => {
                setMessages([WELCOME_MESSAGE]);
                setInsight(DEFAULT_INSIGHT);
              }}
              className="w-full bg-indigo-600 hover:bg-indigo-500 transition rounded-xl py-3 font-medium"
            >
              + New Analysis
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {historyLoading && (
              <p className="text-xs text-slate-500">Loading sessions…</p>
            )}
            {!historyLoading && sessions.length === 0 && (
              <p className="text-xs text-slate-500">
                Past analyses will appear here.
              </p>
            )}
            {sessions.map((session) => (
              <button
                type="button"
                key={`${session.sessionId}-${session.timestamp}`}
                onClick={() => openSession(session)}
                className="w-full text-left p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/70 transition border border-slate-700"
              >
                <p className="text-sm text-slate-200">{sessionLabel(session)}</p>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                  {session.query}
                </p>
              </button>
            ))}
          </div>
        </aside>

        <main className="flex-1 flex flex-col">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6 border-b border-slate-800 bg-slate-900/30">
            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">Market Sentiment</p>
              <h3
                className={`text-xl font-semibold mt-2 ${
                  SENTIMENT_COLOR[insight.sentiment] ?? "text-white"
                }`}
              >
                {insight.sentiment}
              </h3>
              <p className="text-sm text-slate-500 mt-2">
                From the latest multi-agent verdict.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">AI Confidence</p>
              <h3 className="text-xl font-semibold mt-2">
                {typeof insight.confidence === "number"
                  ? `${insight.confidence}%`
                  : insight.confidence}
              </h3>
              <p className="text-sm text-slate-500 mt-2">
                Judge agent reconciliation score.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">Suggested Holding</p>
              <h3 className="text-xl font-semibold mt-2">
                {insight.holding_period}
              </h3>
              <p className="text-sm text-slate-500 mt-2">
                Swing horizon from the thesis.
              </p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-5 py-4 shadow-md border ${
                    message.role === "user"
                      ? "bg-indigo-600 border-indigo-500"
                      : "bg-slate-900 border-slate-800"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        message.role === "user"
                          ? "bg-indigo-200"
                          : "bg-emerald-400"
                      }`}
                    />
                    <span className="text-xs uppercase tracking-wide text-slate-300">
                      {message.role === "user" ? "You" : "AI Analyst"}
                    </span>
                  </div>

                  {message.kind === "verdict" ? (
                    <VerdictCard data={message.content} />
                  ) : (
                    <p className="text-sm leading-7 text-slate-100 whitespace-pre-wrap">
                      {message.content}
                    </p>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl px-5 py-4 bg-slate-900 border border-slate-800 shadow-md">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="text-xs uppercase tracking-wide text-slate-300">
                      Running agents…
                    </span>
                  </div>
                  <div className="flex gap-1 items-center h-5">
                    <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce [animation-delay:0ms]" />
                    <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce [animation-delay:150ms]" />
                    <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="px-6 pb-4 flex flex-wrap gap-3">
            {[
              "Should I buy TCS for next 3 months?",
              "Analyze RELIANCE swing setup",
              "Is INFY a HOLD right now?",
              "HDFCBANK technical outlook",
            ].map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => handleAnalyze(prompt)}
                className="px-4 py-2 rounded-full bg-slate-900 border border-slate-700 hover:border-indigo-500 hover:bg-slate-800 transition text-sm"
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="border-t border-slate-800 p-4 bg-slate-950">
            <div className="max-w-5xl mx-auto flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-2xl p-3 shadow-lg">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about a Nifty 50 swing-trade setup..."
                className="flex-1 bg-transparent outline-none resize-none text-sm text-white placeholder:text-slate-500 min-h-[40px]"
              />
              <button
                type="button"
                onClick={() => handleAnalyze()}
                disabled={loading || !input.trim()}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition px-5 py-3 rounded-xl font-medium"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </div>
            <p className="text-center text-xs text-slate-600 mt-2">
              Press Enter to send · Shift+Enter for new line · Demo gate only
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
