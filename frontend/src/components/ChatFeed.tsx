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
  Zap,
  Code2,
  Columns,
} from 'lucide-react';

interface ChatFeedProps {
  messages: Message[];
  onSendMessage: (content: string) => Promise<void>;
  onOpenFlowModal: (graph: FlowGraphData) => void;
  isSending: boolean;
}

type ViewMode = 'optimized' | 'baseline' | 'both';

export const ChatFeed: React.FC<ChatFeedProps> = ({
  messages,
  onSendMessage,
  onOpenFlowModal,
  isSending,
}) => {
  const [prompt, setPrompt] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [viewModes, setViewModes] = useState<Record<number, ViewMode>>({});
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

  const handleCopyCode = (code: string, key: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(key);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const cycleViewMode = (msgId: number) => {
    setViewModes((prev) => {
      const current = prev[msgId] || 'optimized';
      const next: ViewMode = current === 'optimized' ? 'baseline' : current === 'baseline' ? 'both' : 'optimized';
      return { ...prev, [msgId]: next };
    });
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
              Submit a task. The agent generates, tests in a Docker sandbox, and creates idiomatic refactors.
            </p>
          </div>
        ) : (
          messages.map((msg) => {
            const hasOptimization = !!msg.optimized_code && msg.optimized_code !== msg.code;
            const currentMode: ViewMode = viewModes[msg.id] || (hasOptimization ? 'optimized' : 'baseline');

            return (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`max-w-4xl w-full rounded-2xl p-5 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-[#871658] text-[#FAF6F0] rounded-br-none shadow-md max-w-2xl'
                      : 'bg-white border border-[#E8DCCF] text-[#24071B] rounded-bl-none shadow-sm'
                  }`}
                >
                  {/* Content Text */}
                  <div className="whitespace-pre-wrap">{msg.content}</div>

                  {/* Code Container */}
                  {(msg.code || msg.optimized_code) && (
                    <div className="mt-4 rounded-xl border border-[#4D123B] bg-[#1A0413] text-[#FAF6F0] overflow-hidden text-xs shadow-inner">
                      {/* Top Bar with Mode Switcher */}
                      <div className="flex items-center justify-between border-b border-[#4D123B] px-4 py-2.5 bg-[#24071B]">
                        <div className="flex items-center gap-2">
                          <Code2 className="h-4 w-4 text-[#871658]" />
                          <span className="font-mono text-xs text-[#FAF6F0]/80">
                            {currentMode === 'both'
                              ? 'Side-by-Side Comparison'
                              : currentMode === 'optimized'
                              ? '⚡ Idiomatic Standard Library Solution'
                              : '📄 Baseline Implementation'}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          {hasOptimization && (
                            <button
                              type="button"
                              onClick={() => cycleViewMode(msg.id)}
                              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-[#871658] text-[#FAF6F0] hover:bg-[#A01B69] transition cursor-pointer"
                            >
                              {currentMode === 'optimized' && <><Zap className="h-3 w-3" /> Show Baseline</>}
                              {currentMode === 'baseline' && <><Columns className="h-3 w-3" /> Compare Both</>}
                              {currentMode === 'both' && <><Zap className="h-3 w-3" /> Show Optimized</>}
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Code Display Area */}
                      {currentMode === 'both' && hasOptimization ? (
                        /* Side-by-Side View */
                        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-[#4D123B]">
                          {/* Baseline Column */}
                          <div className="flex flex-col">
                            <div className="flex items-center justify-between px-3 py-1.5 bg-[#2A0520] border-b border-[#4D123B] text-[11px] text-[#FAF6F0]/70">
                              <span className="font-mono">Baseline</span>
                              <button
                                type="button"
                                onClick={() => handleCopyCode(msg.code || '', `base-${msg.id}`)}
                                className="flex items-center gap-1 hover:text-[#FAF6F0]"
                              >
                                {copiedId === `base-${msg.id}` ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                                Copy
                              </button>
                            </div>
                            <pre className="p-3 font-mono text-[#FAF6F0] overflow-x-auto text-[11px]">
                              <code>{msg.code}</code>
                            </pre>
                          </div>

                          {/* Optimized Column */}
                          <div className="flex flex-col bg-[#160210]">
                            <div className="flex items-center justify-between px-3 py-1.5 bg-[#340727] border-b border-[#4D123B] text-[11px] text-amber-300 font-medium">
                              <span className="flex items-center gap-1"><Zap className="h-3 w-3" /> Optimized</span>
                              <button
                                type="button"
                                onClick={() => handleCopyCode(msg.optimized_code || '', `opt-${msg.id}`)}
                                className="flex items-center gap-1 text-[#FAF6F0]/70 hover:text-[#FAF6F0]"
                              >
                                {copiedId === `opt-${msg.id}` ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                                Copy
                              </button>
                            </div>
                            <pre className="p-3 font-mono text-[#FAF6F0] overflow-x-auto text-[11px]">
                              <code>{msg.optimized_code}</code>
                            </pre>
                          </div>
                        </div>
                      ) : (
                        /* Single Code View (Optimized or Baseline) */
                        <div>
                          <pre className="p-4 font-mono text-[#FAF6F0] overflow-x-auto text-xs">
                            <code>{currentMode === 'optimized' && msg.optimized_code ? msg.optimized_code : msg.code}</code>
                          </pre>
                        </div>
                      )}

                      {/* Compression Telemetry Banner */}
                      {msg.optimization_metrics && (
                        <div className="flex items-center justify-between border-t border-[#4D123B] px-4 py-2 bg-[#2E0B22] text-[11px] text-[#FAF6F0]/80">
                          <span className="flex items-center gap-1.5 font-medium text-amber-300">
                            <Zap className="h-3.5 w-3.5" />
                            Refactored via Standard Library
                          </span>
                          <div className="flex gap-3">
                            <span>
                              Lines: <strong>{msg.optimization_metrics.original_loc}</strong> → <strong>{msg.optimization_metrics.optimized_loc}</strong> (-{msg.optimization_metrics.loc_reduction_pct}%)
                            </span>
                            <span>
                              AST Nodes: <strong>{msg.optimization_metrics.original_ast_nodes}</strong> → <strong>{msg.optimization_metrics.optimized_ast_nodes}</strong> (-{msg.optimization_metrics.ast_reduction_pct}%)
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Telemetry Bar */}
                  {msg.role === 'assistant' && (
                    <div className="mt-4 flex flex-wrap items-center gap-2 pt-3 border-t border-[#E8DCCF] text-xs">
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

                      {msg.flow_graph && (
                        <button
                          type="button"
                          onClick={() => onOpenFlowModal(msg.flow_graph!)}
                          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#871658] text-[#FAF6F0] hover:bg-[#A01B69] transition font-medium shadow-sm cursor-pointer"
                        >
                          <Layers className="h-3.5 w-3.5" />
                          View Flow Graph
                        </button>
                      )}

                      {msg.tokens_used > 0 && (
                        <span className="inline-flex items-center gap-1 text-[11px] text-[#7A6960] ml-auto">
                          <Cpu className="h-3 w-3" />
                          {msg.tokens_used.toLocaleString()} tokens (${msg.cost_usd.toFixed(4)})
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        {isSending && (
          <div className="flex items-center gap-2 text-xs font-medium text-[#871658]">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Agent orchestrating generation, sandbox test & idiomatic refactoring...</span>
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
            className="flex items-center justify-center rounded-xl bg-[#871658] px-5 text-[#FAF6F0] hover:bg-[#A01B69] disabled:opacity-40 transition shadow-md active:scale-95 cursor-pointer"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};