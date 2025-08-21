from typing import Any, Dict, List, Optional
import logging
from store import FileJsonStore
from nodes import BaseNode, NODE_REGISTRY


logger = logging.getLogger(__name__)


class GraphBuilder:
    def __init__(self, store: FileJsonStore):
        self.store = store
        self.root: Optional[BaseNode] = None
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def build(self, root_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if root_type not in NODE_REGISTRY:
            raise ValueError(f"Unknown node type: {root_type}")
        logger.info('Building graph for root_type=%s params=%s', root_type, params)
        root_cls = NODE_REGISTRY[root_type]
        self.root = root_cls(self.store, **params)
        self.root.fetch_data()
        if not self.root.node_id:
            logger.info('Root node not found')
            return {"metaVersion": 1, "nodes": [], "edges": [], "root": None}
        self._add_node(self.root)
        self._expand(self.root, params)
        return {
            "metaVersion": 1,
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "root": f"{self.root.ref_data_type}:{self.root.node_id}",
        }

    def _add_node(self, node: BaseNode):
        gid = f"{node.ref_data_type}:{node.node_id}"
        if gid not in self.nodes:
            self.nodes[gid] = node.to_graph_node()

    def _add_edge(self, source: BaseNode, target: BaseNode, rel: str):
        sid = f"{source.ref_data_type}:{source.node_id}"
        tid = f"{target.ref_data_type}:{target.node_id}"
        self.edges.append({
            'id': f"{sid}->{rel}->{tid}",
            'source': sid,
            'target': tid,
            'type': rel,
            'label': rel,
        })

    def _expand(self, node: BaseNode, params: Dict[str, Any]):
        if not node.linked_nodes:
            return
        for link in node.linked_nodes:
            ltype = link.get('type')
            lid = link.get('id')
            rel = link.get('rel', 'HAS')
            if ltype not in NODE_REGISTRY:
                logger.debug('Unknown linked node type %s; skipping', ltype)
                continue
            child_cls = NODE_REGISTRY[ltype]
            # Pass id under appropriate key based on target type
            child_params = {**params}
            if ltype in ('Stock', 'Option', 'Future', 'Index'):
                child_params['InstrumentId'] = lid
            elif ltype in ('StockTradingLine', 'OptionTradingLine', 'IndexTradingLine', 'FutureTradingLine'):
                child_params['TradingLineId'] = lid
            elif ltype == 'Exchange':
                child_params['mic'] = lid
            elif ltype == 'IndexComposition':
                child_params['basketId'] = lid
            child = child_cls(self.store, **child_params)
            child.fetch_data()
            if not child.node_id:
                continue
            self._add_node(child)
            self._add_edge(node, child, rel)
            self._expand(child, params)

