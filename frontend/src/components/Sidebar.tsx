import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import type { ChatSummary } from '../types/api';
import {
  Plus,
  MessageSquare,
  Trash2,
  Edit2,
  Check,
  X,
  LogOut,
  Terminal,
} from 'lucide-react';

interface SidebarProps {
  chats: ChatSummary[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onCreateChat: () => void;
  onDeleteChat: (chatId: string) => void;
  onRenameChat: (chatId: string, newName: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  chats,
  activeChatId,
  onSelectChat,
  onCreateChat,
  onDeleteChat,
  onRenameChat,
}) => {
  const { user, logout } = useAuth();
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');

  const handleStartRename = (chat: ChatSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingChatId(chat.chat_id);
    setEditName(chat.name);
  };

  const handleSaveRename = (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (editName.trim()) {
      onRenameChat(chatId, editName.trim());
    }
    setEditingChatId(null);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingChatId(null);
  };

  return (
    <aside className="flex flex-col w-72 h-screen border-r border-[#4D123B] bg-[#24071B] text-[#FAF6F0] shrink-0 select-none shadow-xl">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-[#4D123B]">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#871658] border border-[#FAF6F0]/20 text-[#FAF6F0] shadow-md">
          <Terminal className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-[#FAF6F0]">Agent Studio</h1>
          <p className="text-[11px] text-[#FAF6F0]/60">Deep Berry & Vanilla</p>
        </div>
      </div>

      {/* New Workspace Button */}
      <div className="p-3">
        <button
          onClick={onCreateChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#FAF6F0] hover:bg-[#F3ECE2] py-2.5 px-4 text-xs font-bold text-[#24071B] shadow-md transition-all active:scale-[0.98]"
        >
          <Plus className="h-4 w-4 stroke-[2.5]" />
          New Workspace
        </button>
      </div>

      {/* Workspaces List */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="px-2 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#FAF6F0]/40">
          Workspaces
        </div>
        {chats.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-[#FAF6F0]/40">
            No workspaces yet. Click "New Workspace" to start.
          </div>
        ) : (
          chats.map((chat) => {
            const isActive = chat.chat_id === activeChatId;
            const isEditing = chat.chat_id === editingChatId;

            return (
              <div
                key={chat.chat_id}
                onClick={() => onSelectChat(chat.chat_id)}
                className={`group flex items-center justify-between gap-2 rounded-xl px-3 py-2 text-xs font-medium cursor-pointer transition-all ${
                  isActive
                    ? 'bg-[#360B29] text-[#FAF6F0] shadow-sm border border-[#871658]'
                    : 'text-[#FAF6F0]/70 hover:bg-[#360B29]/50 hover:text-[#FAF6F0]'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <MessageSquare
                    className={`h-4 w-4 shrink-0 ${
                      isActive ? 'text-[#FAF6F0]' : 'text-[#FAF6F0]/40 group-hover:text-[#FAF6F0]'
                    }`}
                  />
                  {isEditing ? (
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="w-full bg-[#1A0413] border border-[#871658] rounded px-1.5 py-0.5 text-xs text-[#FAF6F0] focus:outline-none"
                      autoFocus
                    />
                  ) : (
                    <span className="truncate">{chat.name}</span>
                  )}
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {isEditing ? (
                    <>
                      <button
                        onClick={(e) => handleSaveRename(chat.chat_id, e)}
                        className="rounded p-1 hover:bg-[#4D123B] text-[#FAF6F0]"
                      >
                        <Check className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={handleCancelRename}
                        className="rounded p-1 hover:bg-[#4D123B] text-[#FAF6F0]/60"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={(e) => handleStartRename(chat, e)}
                        className="rounded p-1 hover:bg-[#4D123B] text-[#FAF6F0]/60 hover:text-[#FAF6F0]"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteChat(chat.chat_id);
                        }}
                        className="rounded p-1 hover:bg-[#4D123B] text-[#FAF6F0]/60 hover:text-rose-300"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* User Footer */}
      <div className="border-t border-[#4D123B] p-3">
        <div className="flex items-center justify-between rounded-xl bg-[#360B29] p-2.5 border border-[#4D123B]/60">
          <div className="min-w-0 pr-2">
            <p className="truncate text-xs font-semibold text-[#FAF6F0]">{user?.username}</p>
            <p className="truncate text-[10px] text-[#FAF6F0]/60">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="rounded-lg p-1.5 text-[#FAF6F0]/60 hover:bg-[#4D123B] hover:text-[#FAF6F0] transition-colors"
            title="Sign Out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};