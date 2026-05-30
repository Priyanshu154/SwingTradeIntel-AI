import { useState } from "react";
import { useNavigate } from "react-router-dom";
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
  sentiment: "Bullish",
  confidence: 78,
  holding_period: "2–4 Months",
};

export default function AISwingTradeChatbot() {
  const navigate = useNavigate();
  const { email, logout, authFetch } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: `Hello! Ask me about any stock for swing-trade analysis. Example: "Should I buy TCS for next 3 months?"`,
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [insight, setInsight] = useState(DEFAULT_INSIGHT);

  const handleAnalyze = async (query = input) => {
    if (!query.trim()) return;

    const userMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setInput("");

    try {
      const response = await authFetch("/analyze", {
        method: "POST",
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // Update top insight cards from response
      const sentimentMap = {
        BUY: "Bullish",
        SELL: "Bearish",
        HOLD: "Neutral",
      };

      setInsight({
        sentiment: sentimentMap[data.verdict] ?? "Neutral",
        confidence: data.confidence,
        holding_period: data.holding_period ?? "N/A",
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Something went wrong while analyzing the stock. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            AI Swing Trade Research Assistant
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Multi-Agent GenAI powered market analysis
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
        {/* Sidebar */}
        <aside className="w-80 border-r border-slate-800 bg-slate-900/40 hidden lg:flex flex-col">
          <div className="p-4 border-b border-slate-800">
            <button
              onClick={() => {
                setMessages([
                  {
                    role: "assistant",
                    content: `Hello! Ask me about any stock for swing-trade analysis. Example: "Should I buy TCS for next 3 months?"`,
                  },
                ]);
                setInsight(DEFAULT_INSIGHT);
              }}
              className="w-full bg-indigo-600 hover:bg-indigo-500 transition rounded-xl py-3 font-medium"
            >
              + New Analysis
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {[
              "TCS swing analysis",
              "BankNifty weekly outlook",
              "Reliance breakout analysis",
              "Infosys holding strategy",
            ].map((item) => (
              <div
                key={item}
                onClick={() => handleAnalyze(item)}
                className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/70 transition cursor-pointer border border-slate-700"
              >
                <p className="text-sm text-slate-200">{item}</p>
              </div>
            ))}
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Top Insight Cards — now dynamic */}
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
                Based on latest query analysis.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">AI Confidence</p>
              <h3 className="text-xl font-semibold mt-2">
                {insight.confidence}%
              </h3>
              <p className="text-sm text-slate-500 mt-2">
                Based on technical + news signals.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">Suggested Holding</p>
              <h3 className="text-xl font-semibold mt-2">
                {insight.holding_period}
              </h3>
              <p className="text-sm text-slate-500 mt-2">
                Medium-risk swing setup.
              </p>
            </div>
          </div>

          {/* Chat Messages */}
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

                  {/* Preserve newlines in AI response */}
                  <p className="text-sm leading-7 text-slate-100 whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl px-5 py-4 bg-slate-900 border border-slate-800 shadow-md">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="text-xs uppercase tracking-wide text-slate-300">
                      AI Analyst
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

          {/* Suggested Prompts */}
          <div className="px-6 pb-4 flex flex-wrap gap-3">
            {[
              "Should I buy TCS?",
              "Analyze Reliance",
              "BankNifty weekly outlook",
              "Best swing trade today",
            ].map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleAnalyze(prompt)}
                className="px-4 py-2 rounded-full bg-slate-900 border border-slate-700 hover:border-indigo-500 hover:bg-slate-800 transition text-sm"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <div className="border-t border-slate-800 p-4 bg-slate-950">
            <div className="max-w-5xl mx-auto flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-2xl p-3 shadow-lg">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about a stock, sector, or swing-trade setup..."
                className="flex-1 bg-transparent outline-none resize-none text-sm text-white placeholder:text-slate-500 min-h-[40px]"
              />

              <button
                onClick={() => handleAnalyze()}
                disabled={loading || !input.trim()}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition px-5 py-3 rounded-xl font-medium"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </div>
            <p className="text-center text-xs text-slate-600 mt-2">
              Press Enter to send · Shift+Enter for new line
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
