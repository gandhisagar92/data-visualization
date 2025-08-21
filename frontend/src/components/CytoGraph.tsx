import React, { useEffect, useMemo, useRef } from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import cytoscape from 'cytoscape'
import type { GraphResponse } from './types'

// Plugins registered lazily in effect to avoid SSR/require issues

type Props = {
  graph: GraphResponse | null
  isDark: boolean
  onNodeClick?: (id: string, type: string) => void
}

export default function CytoGraph({ graph, isDark, onNodeClick }: Props) {
  const cyRef = useRef<any>(null)

  const elements = useMemo(() => {
    if (!graph) return []
    const nodes = graph.nodes.map(n => ({
      data: { id: n.id, label: n.label || n.id, type: n.type, attributes: n.attributes || {} }
    }))
    const edges = graph.edges.map(e => ({ data: { id: e.id, source: e.source, target: e.target, label: e.label || e.type } }))
    return [...nodes, ...edges]
  }, [graph])

  const stylesheet = useMemo(() => [
    {
      selector: 'node',
      style: {
        'background-color': isDark ? '#0b1426' : '#ffffff',
        'border-color': isDark ? '#253453' : '#c9d2e3',
        'border-width': 1.5,
        'label': 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        'color': isDark ? '#0f172a' : '#0f172a',
        'text-background-color': isDark ? '#0b1426' : '#ffffff',
        'text-background-opacity': 1,
        'text-background-padding': 8,
        'font-size': 12,
        'width': 220,
        'height': 60,
        'shape': 'round-rectangle'
      }
    },
    {
      selector: 'edge',
      style: {
        'line-color': isDark ? '#4b5563' : '#94a3b8',
        'target-arrow-color': isDark ? '#4b5563' : '#94a3b8',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'width': 2,
        'label': 'data(label)',
        'font-size': 10,
        'color': isDark ? '#9FB3C8' : '#475569'
      }
    }
  ], [isDark])

  useEffect(() => {
    if (!cyRef.current) return
    const cy = cyRef.current
    ;(async () => {
      try {
        const mod: any = await import('cytoscape-dagre')
        const plugin = mod.default || mod
        // Register once
        // @ts-ignore
        if (!(cytoscape as any).__dagre_registered) {
          cytoscape.use(plugin)
          ;(cytoscape as any).__dagre_registered = true
        }
        cy.layout({ name: 'dagre', rankDir: 'LR', rankSep: 140, nodeSep: 80, edgeSep: 20 }).run()
      } catch (e) {
        cy.layout({ name: 'breadthfirst', directed: true, spacingFactor: 1.5 }).run()
      }
      cy.fit(undefined, 40)
      cy.off('tap')
      cy.on('tap', 'node', (evt: any) => {
        const n = evt.target
        const id = n.data('id')
        const type = n.data('type')
        onNodeClick && onNodeClick(id, type)
      })
    })()
  }, [elements, onNodeClick])

  useEffect(() => {
    if (!cyRef.current) return
    cyRef.current.style().fromJson(stylesheet).update()
  }, [stylesheet])

  return (
    <div style={{ width: '100%', height: '100%', background: isDark ? '#0b1220' : '#f8fafc', borderRadius: 12 }}>
      <CytoscapeComponent
        elements={elements as any}
        stylesheet={stylesheet as any}
        style={{ width: '100%', height: '100%' }}
        cy={(cy: any) => (cyRef.current = cy)}
      />
    </div>
  )
}

