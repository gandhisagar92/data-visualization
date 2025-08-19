import React, { useMemo } from 'react'
import { motion } from 'framer-motion'

export type GraphNode = { id: string; type: string; label?: string; attributes?: Record<string, any> }
export type GraphEdge = { id: string; source: string; target: string; type: string; label?: string }
export type GraphResponse = { metaVersion: number; nodes: GraphNode[]; edges: GraphEdge[]; root: string | null }

export type MindMapTreeProps = {
  graph: GraphResponse | null
  filterText?: string
  onNodeClick?: (node: GraphNode) => void
}

type TreeNode = GraphNode & { children?: TreeNode[]; depth?: number; x?: number; y?: number }

export default function MindMapTree({ graph, filterText = '', onNodeClick }: MindMapTreeProps) {
  const NODE_W = 220
  const ROW_H = 18
  const H_GAP = 260
  const V_GAP = 90

  const { nodes, edges, viewBox } = useMemo(() => {
    if (!graph || !graph.root) {
      return { nodes: [] as TreeNode[], edges: [] as any[], viewBox: '0 0 1200 800' }
    }

    const idToNode = new Map<string, TreeNode>()
    graph.nodes.forEach(n => idToNode.set(n.id, { ...n }))

    // Filter by text if present
    const term = (filterText || '').toLowerCase()
    const matches = (n: GraphNode) =>
      (n.label || '').toLowerCase().includes(term) ||
      Object.values(n.attributes || {}).some(v => String(v).toLowerCase().includes(term))

    // Build directed adjacency (source -> targets)
    const outgoing = new Map<string, string[]>()
    graph.edges.forEach(e => {
      if (!outgoing.has(e.source)) outgoing.set(e.source, [])
      outgoing.get(e.source)!.push(e.target)
    })

    // Choose a tree spanning from root; avoid cycles by visited set
    const visited = new Set<string>()
    function build(nodeId: string): TreeNode | null {
      const gn = idToNode.get(nodeId)
      if (!gn) return null
      if (visited.has(nodeId)) return { ...gn, children: [] }
      visited.add(nodeId)
      const childrenIds = outgoing.get(nodeId) || []
      const childNodes: TreeNode[] = []
      for (const cid of childrenIds) {
        const cn = build(cid)
        if (cn) childNodes.push(cn)
      }
      const tn: TreeNode = { ...gn, children: childNodes }
      return tn
    }

    let rootTree = build(graph.root)

    // Apply filter: if filter is set, keep only nodes that match or lead to matches
    if (term && rootTree) {
      function filterTree(n: TreeNode): TreeNode | null {
        const keptChildren = (n.children || []).map(filterTree).filter(Boolean) as TreeNode[]
        const keepSelf = matches(n)
        if (keepSelf || keptChildren.length > 0) {
          return { ...n, children: keptChildren }
        }
        return null
      }
      rootTree = filterTree(rootTree)
    }

    if (!rootTree) {
      return { nodes: [] as TreeNode[], edges: [] as any[], viewBox: '0 0 1200 800' }
    }

    // Tidy layout: set depth
    function setDepth(n: TreeNode, d = 0) {
      n.depth = d
      ;(n.children || []).forEach(c => setDepth(c, d + 1))
    }
    setDepth(rootTree, 0)

    // assign y positions: leaves take next slot; internal = average(child y)
    let nextLeafY = 0
    function assignY(n: TreeNode) {
      if (!n.children || n.children.length === 0) {
        n.y = nextLeafY * V_GAP
        nextLeafY += 1
      } else {
        n.children.forEach(assignY)
        const ys = n.children.map(c => c.y || 0)
        n.y = (Math.min(...ys) + Math.max(...ys)) / 2
      }
    }
    assignY(rootTree)

    // assign x from depth
    function assignX(n: TreeNode) {
      n.x = (n.depth || 0) * H_GAP
      ;(n.children || []).forEach(assignX)
    }
    assignX(rootTree)

    // Collect nodes/edges with references for edge label lookup
    const treeNodes: TreeNode[] = []
    const treeEdges: { id: string; from: TreeNode; to: TreeNode; label?: string }[] = []
    const edgeLabelLookup = new Map<string, string>()
    graph.edges.forEach(e => edgeLabelLookup.set(`${e.source}->${e.target}`, e.label || e.type))

    function walk(n: TreeNode) {
      treeNodes.push(n)
      ;(n.children || []).forEach(c => {
        treeEdges.push({ id: `${n.id}->${c.id}`, from: n, to: c, label: edgeLabelLookup.get(`${n.id}->${c.id}`) })
        walk(c)
      })
    }
    walk(rootTree)

    // Compute viewbox
    const pad = 80
    const NODE_H_BASE = 48
    function nodeHeight(n: TreeNode) {
      const attrs = Object.entries(n.attributes || {})
      const lines = 1 + attrs.length
      return NODE_H_BASE + Math.max(0, lines - 1) * ROW_H
    }
    const minX = Math.min(...treeNodes.map(n => (n.x || 0) - NODE_W / 2)) - pad
    const maxX = Math.max(...treeNodes.map(n => (n.x || 0) + NODE_W / 2)) + pad
    const minY = Math.min(...treeNodes.map(n => (n.y || 0) - nodeHeight(n) / 2)) - pad
    const maxY = Math.max(...treeNodes.map(n => (n.y || 0) + nodeHeight(n) / 2)) + pad

    return { nodes: treeNodes, edges: treeEdges, viewBox: `${minX} ${minY} ${maxX - minX} ${maxY - minY}` }
  }, [graph, filterText])

  function linkPath(from: TreeNode, to: TreeNode) {
    const NODE_H = 48 + Math.max(0, Object.keys(from.attributes || {}).length) * ROW_H
    const x1 = (from.x || 0) + NODE_W / 2
    const y1 = from.y || 0
    const x2 = (to.x || 0) - NODE_W / 2
    const y2 = to.y || 0
    const dx = Math.max(40, (x2 - x1) * 0.5)
    return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`
  }

  const renderNode = (n: TreeNode) => {
    const attrs = Object.entries(n.attributes || {})
    const lines = [n.label || n.id, ...attrs.map(([k, v]) => `${k}: ${String(v)}`)]
    const NODE_H = 48 + Math.max(0, lines.length - 1) * ROW_H
    return (
      <motion.g
        key={n.id}
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 22 }}
        onClick={() => onNodeClick && onNodeClick(n)}
        style={{ cursor: onNodeClick ? 'pointer' : 'default' }}
      >
        <rect
          x={(n.x || 0) - NODE_W / 2}
          y={(n.y || 0) - NODE_H / 2}
          rx={10}
          ry={10}
          width={NODE_W}
          height={NODE_H}
          filter="url(#shadow)"
          fill={(n.depth || 0) === 0 ? '#1f6feb' : '#0f141a'}
          stroke={(n.depth || 0) === 0 ? '#1b4fb1' : '#2d3846'}
          strokeWidth={1.5}
        />
        {lines.map((t, i) => (
          <text
            key={`${n.id}-line-${i}`}
            x={n.x}
            y={(n.y || 0) - NODE_H / 2 + 20 + i * ROW_H}
            textAnchor="middle"
            fontSize={12}
            fontWeight={i === 0 ? 600 : 400}
            fill={(n.depth || 0) === 0 ? '#ffffff' : '#e6edf3'}
          >
            {t}
          </text>
        ))}
      </motion.g>
    )
  }

  return (
    <div style={{ width: '100%', height: '100%', background: '#0c1116', borderRadius: 10 }}>
      <svg width="100%" height="100%" viewBox={viewBox}>
        <defs>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.25" />
          </filter>
        </defs>

        {edges.map(e => (
          <g key={e.id}>
            <path d={linkPath(e.from, e.to)} stroke="#4b5563" strokeWidth={2} fill="none" />
            <text
              x={(((e.from.x || 0) + (e.to.x || 0)) / 2)}
              y={(((e.from.y || 0) + (e.to.y || 0)) / 2) - 8}
              textAnchor="middle"
              fontSize={11}
              fill="#9FB3C8"
              stroke="#0c1116"
              strokeWidth={3}
              paintOrder="stroke"
            >
              {e.label}
            </text>
          </g>
        ))}

        {nodes.map(renderNode)}
      </svg>
    </div>
  )
}

