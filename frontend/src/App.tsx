import React, { useEffect, useMemo, useRef, useState } from 'react'
import CytoGraph from './components/CytoGraph'
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
  gridTemplateColumns: '1fr 420px',
  gridTemplateRows: 'auto 1fr',
  height: '100vh',
  gap: '12px',
  padding: '12px',
  boxSizing: 'border-box',
  background: '#0b1220',
  color: '#E2E8F0',
  fontFamily: 'Inter, system-ui, Segoe UI, Roboto, Arial, sans-serif'
}

const cardStyleBase: React.CSSProperties = {
  border: '1px solid',
  borderRadius: 16,
  padding: 16,
  overflow: 'auto',
  boxShadow: '0 10px 25px rgba(0,0,0,0.12)'
}

const labelStyle: React.CSSProperties = { display: 'block', fontSize: 12, marginBottom: 6 }
const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: 10,
  border: '1px solid',
  marginBottom: 10
}
const selectStyle = inputStyle

const buttonStyle: React.CSSProperties = {
  padding: '10px 14px',
  borderRadius: 10,
  border: '1px solid',
  cursor: 'pointer',
  fontWeight: 600,
  boxShadow: '0 6px 16px rgba(0,0,0,0.08)'
}

function App() {
  const [isDark, setIsDark] = useState(true)
  const [meta, setMeta] = useState<Meta | null>(null)
  const [refType, setRefType] = useState<string>('Stock')
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
    logger.info('Search', { referenceDataType: refType, queryByType: queryBy, inputs })
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
    <div style={{ ...panelStyles, background: isDark ? '#0b1220' : '#f8fafc', color: isDark ? '#E2E8F0' : '#0f172a' }}>
      <div style={{
        ...cardStyleBase,
        background: isDark ? 'linear-gradient(180deg, #0f172a 0%, #0b1220 100%)' : '#ffffff',
        borderColor: isDark ? '#1f2a44' : '#e2e8f0',
        gridColumn: '1 / 3', gridRow: '1 / 2', display: 'flex', alignItems: 'end', gap: 12, flexWrap: 'wrap'
      }}>
        <div style={{ marginLeft: 'auto' }}>
          <label style={{ ...labelStyle, color: isDark ? '#94A3B8' : '#64748b' }}>Theme</label>
          <button
            style={{
              ...buttonStyle,
              background: isDark ? '#111827' : '#e2e8f0',
              color: isDark ? '#E2E8F0' : '#0f172a',
              borderColor: isDark ? '#374151' : '#cbd5e1'
            }}
            onClick={() => setIsDark(v => !v)}
          >{isDark ? 'Dark' : 'Light'}</button>
        </div>
        <div style={{ minWidth: 240, flex: '1 1 240px' }}>
          <label style={{ ...labelStyle, color: isDark ? '#94A3B8' : '#64748b' }}>Reference Data Type</label>
          <select
            style={{ ...selectStyle, background: isDark ? '#0b1426' : '#ffffff', color: isDark ? '#E2E8F0' : '#0f172a', borderColor: isDark ? '#243253' : '#cbd5e1' }}
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
        <div style={{ minWidth: 240, flex: '1 1 240px' }}>
          <label style={{ ...labelStyle, color: isDark ? '#94A3B8' : '#64748b' }}>Query By</label>
          <select
            style={{ ...selectStyle, background: isDark ? '#0b1426' : '#ffffff', color: isDark ? '#E2E8F0' : '#0f172a', borderColor: isDark ? '#243253' : '#cbd5e1' }}
            value={queryBy}
            onChange={e => setQueryBy(e.target.value)}
          >
            {currentMetaType?.queryBy.map(q => (
              <option key={q.type} value={q.type}>{q.type}</option>
            ))}
          </select>
        </div>
        {currentQuery?.inputs.map(inp => (
          <div key={inp.id} style={{ minWidth: 240, flex: '1 1 240px' }}>
            <label style={{ ...labelStyle, color: isDark ? '#94A3B8' : '#64748b' }}>{inp.label}</label>
            {inp.kind === 'select' ? (
              <select
                style={{ ...selectStyle, background: isDark ? '#0b1426' : '#ffffff', color: isDark ? '#E2E8F0' : '#0f172a', borderColor: isDark ? '#243253' : '#cbd5e1' }}
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
                style={{ ...inputStyle, background: isDark ? '#0b1426' : '#ffffff', color: isDark ? '#0f172a' : '#0f172a', borderColor: isDark ? '#243253' : '#cbd5e1' }}
                type={inp.kind}
                value={inputs[inp.id] ?? ''}
                onChange={e => setInputs({ ...inputs, [inp.id]: e.target.value })}
              />
            )}
          </div>
        ))}
        <div style={{ minWidth: 220, flex: '1 1 220px', alignSelf: 'end' }}>
          <label style={{ ...labelStyle, color: isDark ? '#94A3B8' : '#64748b' }}>Filter</label>
          <input
            placeholder="Filter nodes by attribute..."
            style={{ ...inputStyle, marginBottom: 0, background: isDark ? '#0b1426' : '#ffffff', color: isDark ? '#0f172a' : '#0f172a', borderColor: isDark ? '#243253' : '#cbd5e1' }}
            value={filterText}
            onChange={e => setFilterText(e.target.value)}
          />
        </div>
        <div style={{ alignSelf: 'end' }}>
          <button style={{ ...buttonStyle, background: isDark ? '#2563eb' : '#1d4ed8', color: '#ffffff', borderColor: isDark ? '#1f2a44' : '#cbd5e1' }} onClick={onSearch}>Search</button>
        </div>
      </div>

      <div style={{
        ...cardStyleBase,
        background: isDark ? 'linear-gradient(180deg, #0f172a 0%, #0b1220 100%)' : '#ffffff',
        borderColor: isDark ? '#1f2a44' : '#e2e8f0',
        gridColumn: '2 / 3', gridRow: '2 / 3'
      }}>
        <h4 style={{ marginTop: 0, color: isDark ? '#E2E8F0' : '#0f172a' }}>Payload</h4>
        {selectedNode ? (
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(selectedNode.attributes ?? {}, null, 2)}</pre>
        ) : (
          <div style={{ color: '#94A3B8' }}>Click a node to view payload</div>
        )}
      </div>

      <div style={{
        ...cardStyleBase,
        background: isDark ? 'linear-gradient(180deg, #0f172a 0%, #0b1220 100%)' : '#ffffff',
        borderColor: isDark ? '#1f2a44' : '#e2e8f0',
        gridColumn: '1 / 2', gridRow: '2 / 3', position: 'relative', overflow: 'hidden'
      }}>
        <CytoGraph graph={filteredGraph || null} isDark={isDark} onNodeClick={(id, type) => handleNodeClick({ id, type, attributes: {} })} />
      </div>
    </div>
  )
}

export default App