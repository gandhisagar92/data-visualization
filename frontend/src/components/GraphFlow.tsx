import React, { useCallback, useMemo } from 'react'
import ReactFlow, { Background, Controls, MiniMap, useEdgesState, useNodesState, Node, Edge, Position } from 'reactflow'
import 'reactflow/dist/style.css'
import dagre from 'dagre'
import type { GraphResponse, GraphNode, GraphEdge } from './types'

const nodeWidth = 260
const nodeHeight = 80

const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

function layoutElements(nodes: Node[], edges: Edge[], direction: 'LR' | 'TB' = 'LR') {
  const isHorizontal = direction === 'LR'
  dagreGraph.setGraph({ rankdir: direction, ranksep: 100, nodesep: 60, edgesep: 20 })
  nodes.forEach((n) => dagreGraph.setNode(n.id, { width: nodeWidth, height: nodeHeight }))
  edges.forEach((e) => dagreGraph.setEdge(e.source, e.target))
  dagre.layout(dagreGraph)
  nodes.forEach((n) => {
    const pos = dagreGraph.node(n.id)
    n.targetPosition = isHorizontal ? Position.Left : Position.Top
    n.sourcePosition = isHorizontal ? Position.Right : Position.Bottom
    n.position = { x: pos.x - nodeWidth / 2, y: pos.y - nodeHeight / 2 }
  })
  return { nodes, edges }
}

function NodeCard({ data }: any) {
  const meta = data.meta as GraphNode
  const attrs = meta.attributes || {}
  const tooltip = [meta.label || meta.id, ...Object.entries(attrs).map(([k, v]) => `${k}: ${String(v)}`)].join('\n')
  return (
    <div title={tooltip} style={{
      border: '1px solid #253453',
      background: '#0b1426',
      color: '#E2E8F0',
      borderRadius: 10,
      padding: '8px 10px',
      width: nodeWidth - 2,
      height: nodeHeight - 2,
      boxShadow: '0 8px 22px rgba(0,0,0,0.35)'
    }}>
      <div style={{ fontSize: 10, color: '#93A3B8', marginBottom: 2 }}>{meta.type}</div>
      <div style={{ fontSize: 13, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{meta.label || meta.id}</div>
    </div>
  )
}

const nodeTypes = { card: NodeCard }

type Props = { graph: GraphResponse | null; onNodeClick?: (n: GraphNode) => void }

export default function GraphFlow({ graph, onNodeClick }: Props) {
  const { rfNodes, rfEdges } = useMemo(() => {
    const nodes: Node[] = []
    const edges: Edge[] = []
    if (!graph) return { rfNodes: nodes, rfEdges: edges }
    graph.nodes.forEach(n => {
      nodes.push({ id: n.id, type: 'card', data: { meta: n }, position: { x: 0, y: 0 } })
    })
    graph.edges.forEach(e => {
      edges.push({ id: e.id, source: e.source, target: e.target, animated: false, label: e.label || e.type, style: { stroke: '#4b5563' }, labelStyle: { fill: '#9FB3C8', fontSize: 11 } })
    })
    const laid = layoutElements(nodes, edges, 'LR')
    return { rfNodes: laid.nodes, rfEdges: laid.edges }
  }, [graph])

  const [nodes, setNodes, onNodesChange] = useNodesState(rfNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(rfEdges)

  const handleNodeClick = useCallback((_: any, node: Node) => {
    const meta = node.data?.meta as GraphNode
    if (meta && onNodeClick) onNodeClick(meta)
  }, [onNodeClick])

  return (
    <div style={{ width: '100%', height: '100%', background: '#0b1220' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        defaultEdgeOptions={{ type: 'smoothstep', style: { stroke: '#4b5563' } }}
      >
        <Background gap={20} color="#0f1a2b" />
        <MiniMap nodeStrokeColor={'#253453'} nodeColor={'#0b1426'} maskColor={'rgba(15,26,43,0.5)'} />
        <Controls position="bottom-left" />
      </ReactFlow>
    </div>
  )
}

