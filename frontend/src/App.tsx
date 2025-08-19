import React, { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D, { NodeObject, LinkObject } from 'react-force-graph-2d'
import MindMapTree from './components/MindMapTree'
import axios from 'axios'

type MetaInput = { id: string; label: string; kind: 'text' | 'number' | 'date' | 'select'; options?: string[] }
type MetaQuery = { type: string; inputs: MetaInput[] }
type MetaType = { type: string; display: string; queryBy: MetaQuery[] }
type Meta = { referenceDataTypes: MetaType[]; nodeAttributes: Record<string, string[]> }

type GraphNode = { id: string; type: string; label?: string; attributes?: Record<string, any> }
type GraphEdge = { id: string; source: string; target: string; type: string; label?: string }
type GraphResponse = { metaVersion: number; nodes: GraphNode[]; edges: GraphEdge[]; root: string | null }

const panelStyles: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '420px 1fr',
  gridTemplateRows: '330px 1fr',
  height: '100vh',
  gap: '8px',
  padding: '8px',
  boxSizing: 'border-box',
  background: '#0c1116',
  color: '#e6edf3',
  fontFamily: 'Inter, system-ui, Segoe UI, Roboto, Arial, sans-serif'
}

const cardStyle: React.CSSProperties = {
  background: '#151b23',
  border: '1px solid #2d3846',
  borderRadius: 10,
  padding: 12,
  overflow: 'auto'
}

const labelStyle: React.CSSProperties = { display: 'block', fontSize: 12, color: '#9FB3C8', marginBottom: 4 }
const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  borderRadius: 8,
  border: '1px solid #2d3846',
  background: '#0f141a',
  color: '#e6edf3',
  marginBottom: 8
}
const selectStyle = inputStyle

const buttonStyle: React.CSSProperties = {
  padding: '10px 14px',
  borderRadius: 8,
  border: '1px solid #2d3846',
  background: '#238636',
  color: 'white',
  cursor: 'pointer',
  fontWeight: 600
}

const chipStyle = (active: boolean): React.CSSProperties => ({
  padding: '2px 8px',
  borderRadius: 999,
  border: '1px solid #2d3846',
  background: active ? '#1f6feb' : '#0f141a',
  color: active ? 'white' : '#9FB3C8',
  fontSize: 12,
  marginRight: 6
})

function App() {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [refType, setRefType] = useState<string>('StockInstrument')
  const [queryBy, setQueryBy] = useState<string>('InstrumentId')
  const [inputs, setInputs] = useState<Record<string, any>>({})
  const [graph, setGraph] = useState<GraphResponse | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)

  // Client-side payload cache by node id
  const payloadCache = useRef<Map<string, GraphNode>>(new Map())

  useEffect(() => {
    axios.get('/api/meta').then(r => {
      setMeta(r.data as Meta)
    })
  }, [])

  const currentMetaType = useMemo(() => meta?.referenceDataTypes.find(t => t.type === refType), [meta, refType])
  const currentQuery = useMemo(() => currentMetaType?.queryBy.find(q => q.type === queryBy), [currentMetaType, queryBy])

  useEffect(() => {
    if (currentQuery) {
      const initial: Record<string, any> = {}
      currentQuery.inputs.forEach(i => {
        initial[i.id] = ''
      })
      setInputs(initial)
    }
  }, [currentQuery?.type])

  const onSearch = async () => {
    const res = await axios.post('/api/search', {
      referenceDataType: refType,
      queryByType: queryBy,
      inputs
    })
    setGraph(res.data)
    // seed cache with returned nodes
    ;(res.data.nodes as GraphNode[]).forEach(n => {
      payloadCache.current.set(n.id, n)
    })
  }

  const nodes = useMemo(() => graph?.nodes ?? [], [graph])
  const links = useMemo(() => (graph?.edges ?? []).map(e => ({ ...e })), [graph])

  const handleNodeClick = async (nodeObj: NodeObject) => {
    const node = nodeObj as GraphNode
    setSelectedNode(node)
    if (payloadCache.current.has(node.id)) return
    const [type, businessId] = node.id.split(':')
    const res = await axios.get(`/api/node/${encodeURIComponent(type)}/${encodeURIComponent(businessId)}`)
    const fullNode: GraphNode = { ...node, attributes: res.data }
    payloadCache.current.set(node.id, fullNode)
    setSelectedNode(fullNode)
  }

  const drawNode = (node: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const n = node as GraphNode
    const attrs = n.attributes || {}
    const label = n.label || n.id
    const lines: string[] = [label]
    Object.keys(attrs).forEach(k => {
      const v = attrs[k]
      if (v === undefined || v === null || v === '') return
      lines.push(`${k}: ${v}`)
    })
    const fontSize = 12 / Math.sqrt(globalScale)
    ctx.font = `${fontSize}px Inter, system-ui`
    const paddingX = 8
    const paddingY = 6
    const width = Math.max(...lines.map(l => ctx.measureText(l).width)) + paddingX * 2
    const height = (fontSize + 4) * lines.length + paddingY * 2
    ctx.fillStyle = '#0f141a'
    ctx.strokeStyle = '#2d3846'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.roundRect((n as any).x - width / 2, (n as any).y - height / 2, width, height, 8)
    ctx.fill()
    ctx.stroke()
    ctx.textAlign = 'left'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = '#e6edf3'
    lines.forEach((l, i) => {
      ctx.fillText(l, (n as any).x - width / 2 + paddingX, (n as any).y - height / 2 + paddingY + i * (fontSize + 4) + fontSize / 2)
    })
  }

  const graphRef = useRef<any>(null)

  // Filtering UI for large child sets (client-side immediate filter by attribute match)
  const [filterText, setFilterText] = useState('')
  const filteredGraph = useMemo<GraphResponse | null>(() => {
    if (!graph || !filterText.trim()) return graph
    const term = filterText.toLowerCase()
    const keepNode = (n: GraphNode) =>
      (n.label || '').toLowerCase().includes(term) ||
      Object.values(n.attributes || {}).some(v => String(v).toLowerCase().includes(term))

    const keptNodes = graph.nodes.filter(keepNode)
    const keptIds = new Set(keptNodes.map(n => n.id))
    const keptEdges = graph.edges.filter(e => keptIds.has(e.source) && keptIds.has(e.target))
    return { ...graph, nodes: keptNodes, edges: keptEdges }
  }, [graph, filterText])

  return (
    <div style={panelStyles}>
      <div style={{ ...cardStyle, gridColumn: '1 / 2', gridRow: '1 / 2' }}>
        <h3 style={{ marginTop: 0 }}>Reference Data Relationship Explorer</h3>
        <div>
          <label style={labelStyle}>Reference Data Type</label>
          <select
            style={selectStyle}
            value={refType}
            onChange={e => {
              setRefType(e.target.value)
              const next = meta?.referenceDataTypes.find(t => t.type === e.target.value)?.queryBy[0]?.type
              if (next) setQueryBy(next)
            }}
          >
            {meta?.referenceDataTypes.map(t => (
              <option key={t.type} value={t.type}>{t.display}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={labelStyle}>Query By</label>
          <select
            style={selectStyle}
            value={queryBy}
            onChange={e => setQueryBy(e.target.value)}
          >
            {currentMetaType?.queryBy.map(q => (
              <option key={q.type} value={q.type}>{q.type}</option>
            ))}
          </select>
        </div>

        {currentQuery?.inputs.map(inp => (
          <div key={inp.id}>
            <label style={labelStyle}>{inp.label}</label>
            {inp.kind === 'select' ? (
              <select
                style={selectStyle}
                value={inputs[inp.id] ?? ''}
                onChange={e => setInputs({ ...inputs, [inp.id]: e.target.value })}
              >
                <option value="">Select...</option>
                {inp.options?.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : (
              <input
                style={inputStyle}
                type={inp.kind}
                value={inputs[inp.id] ?? ''}
                onChange={e => setInputs({ ...inputs, [inp.id]: e.target.value })}
              />
            )}
          </div>
        ))}

        <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <button style={buttonStyle} onClick={onSearch}>Search</button>
          <input
            placeholder="Filter nodes by attribute..."
            style={{ ...inputStyle, marginBottom: 0 }}
            value={filterText}
            onChange={e => setFilterText(e.target.value)}
          />
        </div>

        <div style={{ marginTop: 10 }}>
          <span style={chipStyle(true)}>Pan: drag background</span>
          <span style={chipStyle(true)}>Zoom: mouse wheel</span>
          <span style={chipStyle(true)}>Drag node to reposition</span>
        </div>
      </div>

      <div style={{ ...cardStyle, gridColumn: '1 / 2', gridRow: '2 / 3' }}>
        <h4 style={{ marginTop: 0 }}>Payload</h4>
        {selectedNode ? (
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(selectedNode.attributes ?? {}, null, 2)}</pre>
        ) : (
          <div style={{ color: '#9FB3C8' }}>Click a node to view payload</div>
        )}
      </div>

      <div style={{ ...cardStyle, gridColumn: '2 / 3', gridRow: '1 / 3', position: 'relative' }}>
        <MindMapTree
          graph={filteredGraph || null}
          filterText={filterText}
          onNodeClick={(n) => setSelectedNode(n)}
        />
      </div>
    </div>
  )
}

export default App

