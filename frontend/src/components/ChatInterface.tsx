import { useEffect, useRef } from "react";
import { useChat } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";

export function ChatInterface() {
  const { messages, isLoading, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-slate-950">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-slate-800 px-6 py-4 bg-slate-950/95 backdrop-blur sticky top-0 z-10">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center text-lg shadow-lg">
            ⛅
          </div>
          <div>
            <h1 className="font-semibold text-slate-100 tracking-tight">Weather Forecast AI</h1>
            <p className="text-xs text-slate-500">Powered by Amazon Nova · OpenWeatherMap</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-slate-500">Live</span>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-3xl mx-auto">
          {messages.length === 0 && (
            <div className="text-center mt-24">
              <div className="text-6xl mb-5 drop-shadow-lg">🌤️</div>
              <p className="text-xl font-semibold text-slate-300 mb-2">
                Ask me anything about the weather
              </p>
              <p className="text-sm text-slate-500 mb-8">
                Real-time conditions · Multi-day forecasts · Severe alerts
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto text-left">
                {[
                  { icon: "🌡️", text: "What's the weather in Tokyo right now?" },
                  { icon: "🌧️", text: "Will it rain in London this week?" },
                  { icon: "⚠️", text: "Any severe alerts for Miami?" },
                  { icon: "🌍", text: "Compare Paris vs Berlin weather" },
                ].map(({ icon, text }) => (
                  <button
                    key={text}
                    onClick={() => sendMessage(text)}
                    className="flex items-start gap-3 p-3 rounded-xl bg-slate-800/60 border border-slate-700 hover:border-sky-500/50 hover:bg-slate-800 text-left transition-all group"
                  >
                    <span className="text-lg mt-0.5">{icon}</span>
                    <span className="text-sm text-slate-400 group-hover:text-slate-200 transition-colors leading-snug">
                      {text}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input */}
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
