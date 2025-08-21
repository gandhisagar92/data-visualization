import React, { useMemo, useRef, useState } from 'react'
import Tree from 'react-d3-tree'
import type { GraphResponse, GraphNode, GraphEdge } from './types'

type Props = {
  graph: GraphResponse | null
  onNodeClick?: (node: GraphNode) => void
}

type D3Node = {
  name: string
  attributes?: Record<string, string>
  nodeSvgShape?: any
  children?: D3Node[]
  __meta?: { id: string; type: string; attributes: Record<string, any> }
}

export default function TreeView({ graph, onNodeClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [translate, setTranslate] = useState<{ x: number; y: number }>({ x: 60, y: 60 })

  const d3Data = useMemo<D3Node | null>(() => {
    if (!graph || !graph.root) return null
    const idToNode: Record<string, GraphNode> = {}
    graph.nodes.forEach(n => { idToNode[n.id] = n })

    const childrenMap: Record<string, string[]> = {}
    graph.edges.forEach(e => {
      if (!childrenMap[e.source]) childrenMap[e.source] = []
      childrenMap[e.source].push(e.target)
    })

    function build(id: string): D3Node {
      const n = idToNode[id]
      const attrs = n?.attributes || {}
      const d3node: D3Node = {
        name: `${n?.label || id}`,
        attributes: Object.keys(attrs).reduce((acc, k) => {
          const v = attrs[k]
          if (v !== undefined && v !== null && v !== '') acc[k] = String(v)
          return acc
        }, {} as Record<string, string>),
        __meta: { id: n.id, type: n.type, attributes: attrs },
      }
      const kids = childrenMap[id] || []
      if (kids.length) d3node.children = kids.map(build)
      return d3node
    }

    return build(graph.root)
  }, [graph])

  const renderCustomNode = ({ nodeDatum }: { nodeDatum: any }) => {
    const meta = nodeDatum.__meta
    const title = nodeDatum.name
    const attributeEntries = Object.entries(nodeDatum.attributes || {})
    return (
      <g>
        <foreignObject x={-140} y={-30} width={280} height={attributeEntries.length ? 80 + attributeEntries.length * 16 : 64}>
          <div style={{
            border: '1px solid #253453',
            background: '#0b1426',
            borderRadius: 10,
            padding: '8px 10px',
            color: '#E2E8F0',
            minWidth: 240,
            maxWidth: 280,
            boxShadow: '0 8px 22px rgba(0,0,0,0.35)'
          }}>
            <div style={{ fontSize: 10, color: '#93A3B8', marginBottom: 2 }}>{meta?.type}</div>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>{title}</div>
            {attributeEntries.length > 0 && (
              <div style={{ display: 'grid', gap: 3 }}>
                {attributeEntries.slice(0, 8).map(([k, v]) => (
                  <div key={k} style={{ fontSize: 11, color: '#B8C5D9', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    <span style={{ color: '#8FA4BD' }}>{k}:</span> {String(v)}
                  </div>
                ))}
              </div>
            )}
          </div>
        </foreignObject>
      </g>
    )
  }

  if (!d3Data) return <div style={{ height: '100%', width: '100%' }} />

  return (
    <div ref={containerRef} style={{ height: '100%', width: '100%', overflow: 'auto', background: '#0b1220', borderRadius: 12 }}>
      <Tree
        data={d3Data}
        orientation="horizontal" // left -> right
        translate={translate}
        separation={{ siblings: 1, nonSiblings: 1.2 }}
        zoomable
        collapsible={false}
        enableLegacyTransitions={true}
        pathFunc="elbow"
        nodeSize={{ x: 260, y: 120 }}
        renderCustomNodeElement={renderCustomNode as any}
        onNodeClick={(nodeData: any) => {
          const meta = nodeData.__meta
          if (meta && onNodeClick) onNodeClick({ id: meta.id, type: meta.type, label: nodeData.name, attributes: meta.attributes })
        }}
        // Custom link labels: react-d3-tree expects render props; emulate via svg overlay by enabling pathFunc and CSS spacing
      />
    </div>
  )
}

