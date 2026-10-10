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
  data: { label: string; details?: string };
  position: { x: number; y: number };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
}

export interface FlowGraphData {
  nodes: FlowNode[];
  edges: FlowEdge[];
}

export interface OptimizationMetrics {
  original_loc: number;
  optimized_loc: number;
  loc_reduction_pct: number;
  original_ast_nodes: number;
  optimized_ast_nodes: number;
  ast_reduction_pct: number;
}

export interface Message {
  id: number;
  chat_id: number;
  role: 'user' | 'assistant';
  content: string;
  code?: string | null;
  optimized_code?: string | null;
  optimization_metrics?: OptimizationMetrics | null;
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