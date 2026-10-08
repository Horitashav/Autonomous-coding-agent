export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface FlowNode {
  id: string;
  type: string;
  data: {
    label: string;
    nodeType: string;
    line: number;
    details?: string;
    color?: string;
  };
  position: { x: number; y: number };
  style?: Record<string, any>;
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  style?: Record<string, any>;
}

export interface FlowGraphData {
  nodes: FlowNode[];
  edges: FlowEdge[];
  summary?: Array<{
    id: string;
    type: string;
    label: string;
    line: number;
    depth: number;
    display: string;
  }>;
}

export interface Message {
  id: number;
  chat_id: number;
  role: 'user' | 'assistant';
  content: string;
  code?: string | null;
  stdout?: string | null;
  stderr?: string | null;
  status: string;
  tokens_used: number;
  cost_usd: number;
  flow_graph?: FlowGraphData | null;
  created_at: string;
}

export interface ChatSummary {
  id: number;
  chat_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatDetail {
  id: number;
  chat_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}