import React, { useEffect, useMemo, useRef, useState } from 'react'
import MindMapTree from './components/MindMapTree'
import axios from 'axios'
import { logger } from './lib/logger'

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
  gap: '12px',
  padding: '12px',
  boxSizing: 'border-box',
  background: '#0b1220',
  color: '#E2E8F0',
  fontFamily: 'Inter, system-ui, Segoe UI, Roboto, Arial, sans-serif'
}

const cardStyle: React.CSSProperties = {
  background: 'linear-gradient(180deg, #0f172a 0%, #0b1220 100%)',
  border: '1px solid #1f2a44',
  borderRadius: 16,
  padding: 16,
  overflow: 'auto',
  boxShadow: '0 10px 25px rgba(0,0,0,0.3)'
}

const labelStyle: React.CSSProperties = { display: 'block', fontSize: 12, color: '#94A3B8', marginBottom: 6 }
const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: 10,
  border: '1px solid #243253',
  background: '#0b1426',
  color: '#E2E8F0',
  marginBottom: 10
}
const selectStyle = inputStyle

const buttonStyle: React.CSSProperties = {
  padding: '10px 14px',
  borderRadius: 10,
  border: '1px solid #1f2a44',
  background: 'linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%)',
  color: 'white',
  cursor: 'pointer',
  fontWeight: 600,
  boxShadow: '0 6px 16px rgba(29,78,216,0.35)'
}

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
      logger.info('Loaded meta')
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
    logger.info('Search', { refType, queryBy, inputs })
    const res = await axios.post('/api/search', {
      referenceDataType: refType,
      queryByType: queryBy,
      inputs
    })
    setGraph(res.data)
    logger.debug('Graph received', res.data)
    ;(res.data.nodes as GraphNode[]).forEach(n => {
      payloadCache.current.set(n.id, n)
    })
  }

  const [filterText, setFilterText] = useState('')
  const filteredGraph = useMemo<GraphResponse | null>(() => {
    if (!graph || !filterText.trim()) return graph
    // Let MindMapTree perform whole-subtree filtering; pass through graph here
    return { ...graph }
  }, [graph, filterText])

  const handleNodeClick = async (node: GraphNode) => {
    setSelectedNode(node)
    if (payloadCache.current.has(node.id)) return
    const [type, businessId] = node.id.split(':')
    const res = await axios.get(`/api/node/${encodeURIComponent(type)}/${encodeURIComponent(businessId)}`)
    const fullNode: GraphNode = { ...node, attributes: res.data }
    payloadCache.current.set(node.id, fullNode)
    setSelectedNode(fullNode)
  }

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
      </div>

      <div style={{ ...cardStyle, gridColumn: '1 / 2', gridRow: '2 / 3' }}>
        <h4 style={{ marginTop: 0 }}>Payload</h4>
        {selectedNode ? (
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(selectedNode.attributes ?? {}, null, 2)}</pre>
        ) : (
          <div style={{ color: '#94A3B8' }}>Hover a node to view payload in tooltip; click to pin here</div>
        )}
      </div>

      <div style={{ ...cardStyle, gridColumn: '2 / 3', gridRow: '1 / 3', position: 'relative' }}>
        <MindMapTree
          graph={filteredGraph || null}
          filterText={filterText}
          onNodeClick={handleNodeClick}
        />
      </div>
    </div>
  )
}

export default App