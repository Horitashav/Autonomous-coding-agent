import React, { useState, useRef, useEffect } from 'react';
import type { Message, FlowGraphData } from '../types/api';
import {
  Send,
  Terminal,
  Cpu,
  Layers,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Loader2,
} from 'lucide-react';

interface ChatFeedProps {
  messages: Message[];
  onSendMessage: (content: string) => Promise<void>;
  onOpenFlowModal: (graph: FlowGraphData) => void;
  isSending: boolean;
}

export const ChatFeed: React.FC<ChatFeedProps> = ({
  messages,
  onSendMessage,
  onOpenFlowModal,
  isSending,
}) => {
  const [prompt, setPrompt] = useState('');
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isSending) return;
    const content = prompt;
    setPrompt('');
    await onSendMessage(content);
  };

  const handleCopyCode = (code: string, id: number) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col flex-1 h-screen bg-[#FAF6F0]">
      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#F3ECE2] border border-[#E8DCCF] text-[#871658] mb-4 shadow-sm">
              <Terminal className="h-7 w-7" />
            </div>
            <h2 className="text-lg font-bold text-[#24071B]">Autonomous Agent Workspace</h2>
            <p className="text-xs text-[#7A6960] mt-1.5 leading-relaxed">
              Describe your software task or algorithm requirement below. The LangGraph agent
              will generate code, execute it in a secure sandbox, and construct an AST flow graph.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${
                msg.role === 'user' ? 'items-end' : 'items-start'
              }`}
            >
              <div
                className={`max-w-3xl rounded-2xl p-5 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-[#871658] text-[#FAF6F0] rounded-br-none shadow-md'
                    : 'bg-white border border-[#E8DCCF] text-[#24071B] rounded-bl-none shadow-sm'
                }`}
              >
                {/* Content */}
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Assistant Code Block */}
                {msg.code && (
                  <div className="mt-4 rounded-xl border border-[#4D123B] bg-[#1A0413] text-[#FAF6F0] overflow-hidden text-xs shadow-inner">
                    <div className="flex items-center justify-between border-b border-[#4D123B] px-4 py-2.5 bg-[#24071B]">
                      <span className="font-mono text-[#FAF6F0]/70">Python Solution</span>
                      <button
                        onClick={() => handleCopyCode(msg.code!, msg.id)}
                        className="flex items-center gap-1.5 text-[#FAF6F0]/70 hover:text-[#FAF6F0] transition-colors"
                      >
                        {copiedId === msg.id ? (
                          <>
                            <Check className="h-3.5 w-3.5 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-3.5 w-3.5" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="p-4 font-mono text-[#FAF6F0] overflow-x-auto selection:bg-[#871658]">
                      <code>{msg.code}</code>
                    </pre>
                  </div>
                )}

                {/* Execution Telemetry Badges */}
                {msg.role === 'assistant' && (
                  <div className="mt-4 flex flex-wrap items-center gap-2 pt-3 border-t border-[#E8DCCF] text-xs">
                    {/* Status Badge */}
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold ${
                        msg.status === 'success'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}
                    >
                      {msg.status === 'success' ? (
                        <CheckCircle2 className="h-3.5 w-3.5" />
                      ) : (
                        <XCircle className="h-3.5 w-3.5" />
                      )}
                      {msg.status || 'Executed'}
                    </span>

                    {/* AST Visualizer Button */}
                    {msg.flow_graph && (
                      <button
                        onClick={() => onOpenFlowModal(msg.flow_graph!)}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#871658] text-[#FAF6F0] hover:bg-[#A01B69] transition-all font-medium shadow-sm cursor-pointer"
                      >
                        <Layers className="h-3.5 w-3.5" />
                        View Flow Graph
                      </button>
                    )}

                    {/* Telemetry info */}
                    {msg.tokens_used > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-[#7A6960] ml-auto">
                        <Cpu className="h-3 w-3" />
                        {msg.tokens_used.toLocaleString()} tokens ($
                        {msg.cost_usd.toFixed(4)})
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isSending && (
          <div className="flex items-center gap-2 text-xs font-medium text-[#871658]">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Agent orchestrator running pipeline...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-[#E8DCCF] bg-[#F3ECE2]/80 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="flex gap-2 max-w-4xl mx-auto">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isSending}
            placeholder="Instruct the agent (e.g. 'Write a Python function to balance a binary search tree')..."
            className="flex-1 rounded-xl border border-[#E8DCCF] bg-white px-4 py-3 text-sm text-[#24071B] placeholder-[#7A6960]/60 focus:border-[#871658] focus:outline-none focus:ring-2 focus:ring-[#871658]/20 shadow-sm disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!prompt.trim() || isSending}
            className="flex items-center justify-center rounded-xl bg-[#871658] px-5 text-[#FAF6F0] hover:bg-[#A01B69] disabled:opacity-40 transition-all shadow-md active:scale-95"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};