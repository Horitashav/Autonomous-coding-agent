import React from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { X, Network } from 'lucide-react';
import type { FlowGraphData } from '../types/api';

interface FlowVisualizerModalProps {
  isOpen: boolean;
  onClose: () => void;
  graphData: FlowGraphData | null;
}

export const FlowVisualizerModal: React.FC<FlowVisualizerModalProps> = ({
  isOpen,
  onClose,
  graphData,
}) => {
  if (!isOpen || !graphData) return null;

  const [nodes, , onNodesChange] = useNodesState(graphData.nodes || []);
  const [edges, , onEdgesChange] = useEdgesState(graphData.edges || []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#24071B]/60 backdrop-blur-sm p-6">
      <div className="flex flex-col h-[85vh] w-[90vw] rounded-2xl border border-[#4D123B] bg-[#24071B] shadow-2xl overflow-hidden">
        {/* Deep Berry Header */}
        <div className="flex items-center justify-between border-b border-[#4D123B] px-6 py-4 bg-[#24071B]">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-lg bg-[#871658] text-[#FAF6F0]">
              <Network className="h-5 w-5" />
            </div>
            <h3 className="text-base font-bold text-[#FAF6F0]">AST Code Flow Visualizer</h3>
            <span className="rounded-full bg-[#360B29] px-2.5 py-0.5 text-xs text-[#FAF6F0]/80 border border-[#4D123B]">
              {nodes.length} Nodes • {edges.length} Edges
            </span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-[#FAF6F0]/60 hover:bg-[#360B29] hover:text-[#FAF6F0] transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Vanilla Cloud Canvas */}
        <div className="flex-1 w-full bg-[#FAF6F0]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background color="#D9CDC1" gap={20} />
            <Controls className="bg-white border border-[#E8DCCF] text-[#24071B] rounded-lg shadow-sm" />
            <MiniMap
              nodeColor={(node) => (node.data?.color as string) || '#871658'}
              className="bg-white border border-[#E8DCCF] rounded-lg shadow-sm"
            />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
};