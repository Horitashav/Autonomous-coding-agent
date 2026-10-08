import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AuthModal } from './components/AuthModal';
import { Sidebar } from './components/Sidebar';
import { ChatFeed } from './components/ChatFeed';
import { FlowVisualizerModal } from './components/FlowVisualizerModal';
import api from './lib/api';
import type { ChatSummary, ChatDetail, FlowGraphData } from './types/api';

const DashboardContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [activeChatDetail, setActiveChatDetail] = useState<ChatDetail | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [selectedGraph, setSelectedGraph] = useState<FlowGraphData | null>(null);

  // Fetch workspaces when authenticated
  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchChats = async () => {
      try {
        const res = await api.get<ChatSummary[]>('/chats/');
        setChats(res.data);
        if (res.data.length > 0 && !activeChatId) {
          setActiveChatId(res.data[0].chat_id);
        }
      } catch (err) {
        console.error('Failed to fetch workspaces:', err);
      }
    };
    fetchChats();
  }, [isAuthenticated]);

  // Load chat messages when activeChatId changes
  useEffect(() => {
    if (!activeChatId) {
      setActiveChatDetail(null);
      return;
    }
    const loadChat = async () => {
      try {
        const res = await api.get<ChatDetail>(`/chats/${activeChatId}`);
        setActiveChatDetail(res.data);
      } catch (err) {
        console.error('Failed to load chat details:', err);
      }
    };
    loadChat();
  }, [activeChatId]);

  const handleCreateChat = async () => {
    try {
      const res = await api.post<ChatSummary>('/chats/', {
        name: `Workspace ${chats.length + 1}`,
      });
      setChats([res.data, ...chats]);
      setActiveChatId(res.data.chat_id);
    } catch (err) {
      console.error('Failed to create workspace:', err);
    }
  };

  const handleDeleteChat = async (chatId: string) => {
    try {
      await api.delete(`/chats/${chatId}`);
      const updated = chats.filter((c) => c.chat_id !== chatId);
      setChats(updated);
      if (activeChatId === chatId) {
        setActiveChatId(updated[0]?.chat_id || null);
      }
    } catch (err) {
      console.error('Failed to delete workspace:', err);
    }
  };

  const handleRenameChat = async (chatId: string, newName: string) => {
    try {
      const res = await api.put<ChatSummary>(`/chats/${chatId}/rename`, { name: newName });
      setChats(chats.map((c) => (c.chat_id === chatId ? res.data : c)));
    } catch (err) {
      console.error('Failed to rename workspace:', err);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeChatId) return;
    setIsSending(true);
    try {
      const res = await api.post(`/chats/${activeChatId}/messages`, { content });
      if (activeChatDetail) {
        setActiveChatDetail({
          ...activeChatDetail,
          messages: [...activeChatDetail.messages, res.data],
        });
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setIsSending(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-400">
        Loading Agent Studio...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthModal />;
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onCreateChat={handleCreateChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
      />
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <ChatFeed
          messages={activeChatDetail?.messages || []}
          onSendMessage={handleSendMessage}
          onOpenFlowModal={setSelectedGraph}
          isSending={isSending}
        />
      </main>
      <FlowVisualizerModal
        isOpen={!!selectedGraph}
        onClose={() => setSelectedGraph(null)}
        graphData={selectedGraph}
      />
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <DashboardContent />
    </AuthProvider>
  );
}