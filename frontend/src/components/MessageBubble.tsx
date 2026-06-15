import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "../types/chat";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-5`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-sky-600 flex items-center justify-center text-base mr-3 flex-shrink-0 mt-1 shadow-md">
          ⛅
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-sky-600 text-white rounded-br-sm shadow-md"
            : "bg-slate-800 text-slate-100 rounded-bl-sm shadow-md border border-slate-700"
        }`}
      >
        {isUser ? (
          <span>{message.content}</span>
        ) : (
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
            {message.isStreaming && (
              <span className="inline-block w-1.5 h-4 bg-slate-400 ml-1 animate-pulse align-middle" />
            )}
          </div>
        )}
        {isUser && message.isStreaming && (
          <span className="inline-block w-1.5 h-4 bg-white/60 ml-1 animate-pulse align-middle" />
        )}
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center text-xs font-bold ml-3 flex-shrink-0 mt-1 shadow-md">
          U
        </div>
      )}
    </div>
  );
}
