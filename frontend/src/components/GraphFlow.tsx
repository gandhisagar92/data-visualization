import React, { useCallback, useEffect } from 'react'
import ReactFlow, { Background, Controls, useEdgesState, useNodesState, Node, Edge, Position, MarkerType } from 'reactflow'
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
  const [nodes, setNodes, onNodesChange] = useNodesState<Node[]>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge[]>([])

  useEffect(() => {
    if (!graph) {
      setNodes([])
      setEdges([])
      return
    }
    const nmap: Record<string, Node> = {}
    const nlist: Node[] = graph.nodes.map(n => {
      const node: Node = { id: n.id, type: 'card', data: { meta: n }, position: { x: 0, y: 0 } }
      nmap[n.id] = node
      return node
    })
    const elist: Edge[] = graph.edges
      .filter(e => nmap[e.source] && nmap[e.target])
      .map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        type: 'smoothstep',
        animated: false,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#4b5563' },
        style: { stroke: '#4b5563' },
        label: e.label || e.type,
        labelStyle: { fill: '#9FB3C8', fontSize: 11 },
      }))
    const laid = layoutElements(nlist, elist, 'LR')
    setNodes([...laid.nodes])
    setEdges([...laid.edges])
  }, [graph, setNodes, setEdges])

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
        <Controls position="bottom-left" />
      </ReactFlow>
    </div>
  )
}

