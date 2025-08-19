from typing import Any, Dict, List
import logging
from store import FileJsonStore
from builder import GraphBuilder

logger = logging.getLogger(__name__)


class GraphService:
    def __init__(self, store: FileJsonStore):
        self.store = store
        self.builder = GraphBuilder(store)

    def _graph_node_id(self, node_type: str, business_id: str) -> str:
        return f"{node_type}:{business_id}"

    def _shape_node(self, node_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        label = (
            payload.get("name")
            or payload.get("ric")
            or payload.get("bloombergTicker")
            or payload.get("instrumentId")
            or payload.get("tradingLineId")
            or payload.get("mic")
            or payload.get("basketId")
        )
        business_id = (
            payload.get("instrumentId")
            or payload.get("tradingLineId")
            or payload.get("basketId")
            or payload.get("mic")
            or payload.get("id")
        )
        node_id = self._graph_node_id(node_type, str(business_id))
        attrs = payload.copy()
        return {
            "id": node_id,
            "type": node_type,
            "label": label,
            "attributes": attrs,
        }

    def _add_edge(self, edges: List[Dict[str, Any]], source: str, target: str, rel_type: str):
        edges.append({
            "id": f"{source}->{rel_type}->{target}",
            "source": source,
            "target": target,
            "type": rel_type,
            "label": rel_type,
        })

    def _expand_relationships(self, node_type: str, payload: Dict[str, Any], nodes: Dict[str, Dict[str, Any]], edges: List[Dict[str, Any]]):
        node_id = self._graph_node_id(node_type, str(payload.get("instrumentId") or payload.get("tradingLineId") or payload.get("basketId") or payload.get("mic") or payload.get("id")))

        if node_type == "Stock":
            for tl_id in payload.get("tradingLines", []):
                tl = self.store.get_by_id("StockTradingLine", "tradingLineId", tl_id)
                if not tl:
                    continue
                tl_node = self._shape_node("StockTradingLine", tl)
                nodes[tl_node["id"]] = tl_node
                self._add_edge(edges, node_id, tl_node["id"], "HAS")
                mic = tl.get("exchangeMic")
                if mic:
                    ex = self.store.get_by_id("Exchange", "mic", mic)
                    if ex:
                        ex_node = self._shape_node("Exchange", ex)
                        nodes[ex_node["id"]] = ex_node
                        self._add_edge(edges, tl_node["id"], ex_node["id"], "LISTED_ON")

        if node_type == "Option":
            for tl_id in payload.get("tradingLines", []):
                tl = self.store.get_by_id("OptionTradingLine", "tradingLineId", tl_id)
                if not tl:
                    continue
                tl_node = self._shape_node("OptionTradingLine", tl)
                nodes[tl_node["id"]] = tl_node
                self._add_edge(edges, node_id, tl_node["id"], "HAS")
                mic = tl.get("exchangeMic")
                if mic:
                    ex = self.store.get_by_id("Exchange", "mic", mic)
                    if ex:
                        ex_node = self._shape_node("Exchange", ex)
                        nodes[ex_node["id"]] = ex_node
                        self._add_edge(edges, tl_node["id"], ex_node["id"], "LISTED_ON")
            for und_id in payload.get("underlyingInstrumentIds", []):
                st = self.store.get_by_id("Stock", "instrumentId", und_id)
                if st:
                    st_node = self._shape_node("Stock", st)
                    nodes[st_node["id"]] = st_node
                    self._add_edge(edges, node_id, st_node["id"], "HAS_UNDERLYING")
                    self._expand_relationships("Stock", st, nodes, edges)
                idx = self.store.get_by_id("Index", "instrumentId", und_id)
                if idx:
                    idx_node = self._shape_node("Index", idx)
                    nodes[idx_node["id"]] = idx_node
                    self._add_edge(edges, node_id, idx_node["id"], "HAS_UNDERLYING")
                    self._expand_relationships("Index", idx, nodes, edges)

        if node_type == "Index":
            for tl_id in payload.get("tradingLines", []):
                tl = self.store.get_by_id("IndexTradingLine", "tradingLineId", tl_id)
                if not tl:
                    continue
                tl_node = self._shape_node("IndexTradingLine", tl)
                nodes[tl_node["id"]] = tl_node
                self._add_edge(edges, node_id, tl_node["id"], "HAS")
                mic = tl.get("exchangeMic")
                if mic:
                    ex = self.store.get_by_id("Exchange", "mic", mic)
                    if ex:
                        ex_node = self._shape_node("Exchange", ex)
                        nodes[ex_node["id"]] = ex_node
                        self._add_edge(edges, tl_node["id"], ex_node["id"], "LISTED_ON")
            comp_id = payload.get("compositionId")
            if comp_id:
                comp = self.store.get_by_id("IndexComposition", "basketId", comp_id)
                if comp:
                    comp_node = self._shape_node("IndexComposition", comp)
                    nodes[comp_node["id"]] = comp_node
                    self._add_edge(edges, node_id, comp_node["id"], "HAS")
                    for stk_id in comp.get("constituentStocks", []):
                        st = self.store.get_by_id("Stock", "instrumentId", stk_id)
                        if st:
                            st_node = self._shape_node("Stock", st)
                            nodes[st_node["id"]] = st_node
                            self._add_edge(edges, comp_node["id"], st_node["id"], "HAS")
                            self._expand_relationships("Stock", st, nodes, edges)

        if node_type == "Future":
            for tl_id in payload.get("tradingLines", []):
                tl = self.store.get_by_id("FutureTradingLine", "tradingLineId", tl_id)
                if not tl:
                    continue
                tl_node = self._shape_node("FutureTradingLine", tl)
                nodes[tl_node["id"]] = tl_node
                self._add_edge(edges, node_id, tl_node["id"], "HAS")
                mic = tl.get("exchangeMic")
                if mic:
                    ex = self.store.get_by_id("Exchange", "mic", mic)
                    if ex:
                        ex_node = self._shape_node("Exchange", ex)
                        nodes[ex_node["id"]] = ex_node
                        self._add_edge(edges, tl_node["id"], ex_node["id"], "LISTED_ON")
            for und_id in payload.get("underlyingInstrumentIds", []):
                st = self.store.get_by_id("Stock", "instrumentId", und_id)
                if st:
                    st_node = self._shape_node("Stock", st)
                    nodes[st_node["id"]] = st_node
                    self._add_edge(edges, node_id, st_node["id"], "HAS_UNDERLYING")
                    self._expand_relationships("Stock", st, nodes, edges)
                idx = self.store.get_by_id("Index", "instrumentId", und_id)
                if idx:
                    idx_node = self._shape_node("Index", idx)
                    nodes[idx_node["id"]] = idx_node
                    self._add_edge(edges, node_id, idx_node["id"], "HAS_UNDERLYING")
                    self._expand_relationships("Index", idx, nodes, edges)

    def search(self, reference_data_type: str, query_by_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("search called: refType=%s queryBy=%s inputs=%s", reference_data_type, query_by_type, inputs)
        # Build graph generically using GraphBuilder
        try:
            graph = self.builder.build(reference_data_type, inputs)
            logger.info("graph built: nodes=%d edges=%d", len(graph.get('nodes', [])), len(graph.get('edges', [])))
            return graph
        except Exception as e:
            logger.exception("Error building graph: %s", e)
            return {"metaVersion": 1, "nodes": [], "edges": [], "root": None}

    def expand(self, node_type: str, business_id: str) -> Dict[str, Any]:
        logger.debug("expand called: nodeType=%s id=%s", node_type, business_id)
        if node_type in ("StockTradingLine", "OptionTradingLine", "IndexTradingLine", "FutureTradingLine"):
            payload = self.store.get_by_id(node_type, "tradingLineId", business_id)
        elif node_type == "Exchange":
            payload = self.store.get_by_id("Exchange", "mic", business_id)
        elif node_type == "IndexComposition":
            payload = self.store.get_by_id("IndexComposition", "basketId", business_id)
        else:
            payload = self.store.get_by_id(node_type, "instrumentId", business_id)

        if not payload:
            logger.warning("expand not found: %s %s", node_type, business_id)
            return {"metaVersion": 1, "nodes": [], "edges": [], "root": None}

        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []
        node = self._shape_node(node_type, payload)
        nodes[node["id"]] = node
        self._expand_relationships(node_type, payload, nodes, edges)
        logger.debug("expand built: nodes=%d edges=%d", len(nodes), len(edges))
        return {"metaVersion": 1, "nodes": list(nodes.values()), "edges": edges, "root": node["id"]}

