export type GraphNode = { id: string; type: string; label?: string; attributes?: Record<string, any> }
export type GraphEdge = { id: string; source: string; target: string; type: string; label?: string }
export type GraphResponse = { metaVersion: number; nodes: GraphNode[]; edges: GraphEdge[]; root: string | null }

