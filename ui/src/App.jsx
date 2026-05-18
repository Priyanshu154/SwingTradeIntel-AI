export default function AISwingTradeChatbot() {
  const messages = [
    {
      role: "assistant",
      content:
        "Hello! Ask me about any stock for swing-trade analysis. Example: “Should I buy TCS for next 3 months?”",
    },
    {
      role: "user",
      content: "Analyze Infosys for swing trade.",
    },
    {
      role: "assistant",
      content:
        "Infosys currently shows moderately bullish momentum with improving sentiment in the IT sector. Suggested holding period: 1–3 months. Risk Level: Medium.",
    },
  ];

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
          <div className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm border border-emerald-500/20">
            Bedrock Connected
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-80 border-r border-slate-800 bg-slate-900/40 hidden lg:flex flex-col">
          <div className="p-4 border-b border-slate-800">
            <button className="w-full bg-indigo-600 hover:bg-indigo-500 transition rounded-xl py-3 font-medium">
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
                className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/70 transition cursor-pointer border border-slate-700"
              >
                <p className="text-sm text-slate-200">{item}</p>
              </div>
            ))}
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Top Insight Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6 border-b border-slate-800 bg-slate-900/30">
            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">Market Sentiment</p>
              <h3 className="text-xl font-semibold mt-2 text-emerald-400">
                Bullish
              </h3>
              <p className="text-sm text-slate-500 mt-2">
                Positive IT sector momentum detected.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">AI Confidence</p>
              <h3 className="text-xl font-semibold mt-2">78%</h3>
              <p className="text-sm text-slate-500 mt-2">
                Based on technical + news signals.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 shadow-lg">
              <p className="text-slate-400 text-sm">Suggested Holding</p>
              <h3 className="text-xl font-semibold mt-2">2–4 Months</h3>
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

                  <p className="text-sm leading-7 text-slate-100">
                    {message.content}
                  </p>
                </div>
              </div>
            ))}
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
                placeholder="Ask about a stock, sector, or swing-trade setup..."
                className="flex-1 bg-transparent outline-none resize-none text-sm text-white placeholder:text-slate-500 min-h-[40px]"
              />

              <button className="bg-indigo-600 hover:bg-indigo-500 transition px-5 py-3 rounded-xl font-medium">
                Analyze
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
