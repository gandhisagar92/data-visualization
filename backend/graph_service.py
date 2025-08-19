from typing import Any, Dict, List
from .store import FileJsonStore


class GraphService:
    def __init__(self, store: FileJsonStore):
        self.store = store

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
        type_to_entity = {
            "StockInstrument": ("Stock", "instrumentId"),
            "OptionInstrument": ("Option", "instrumentId"),
            "FutureInstrument": ("Future", "instrumentId"),
            "IndexInstrument": ("Index", "instrumentId"),
        }
        if reference_data_type not in type_to_entity:
            return {"error": f"Unsupported referenceDataType {reference_data_type}"}

        entity_name, _ = type_to_entity[reference_data_type]
        attribute_type = query_by_type

        if attribute_type == "Economics":
            items = self.store.list_all(entity_name)

            def matches(item: Dict[str, Any]) -> bool:
                strike_ok = (str(item.get("strike")) == str(inputs.get("Strike"))) if inputs.get("Strike") is not None else True
                csize_ok = (str(item.get("contractSize")) == str(inputs.get("ContractSize"))) if inputs.get("ContractSize") is not None else True
                exp_ok = (str(item.get("expirationDate")) == str(inputs.get("ExpirationDate"))) if inputs.get("ExpirationDate") is not None else True
                cp_ok = (str(item.get("CallOrPut")).lower() == str(inputs.get("CallOrPut")).lower()) if inputs.get("CallOrPut") else True
                underlying_ok = True
                if inputs.get("UnderlyingId"):
                    underlying_ok = str(inputs.get("UnderlyingId")) in [str(u) for u in item.get("underlyingInstrumentIds", [])]
                return strike_ok and csize_ok and exp_ok and cp_ok and underlying_ok

            candidates = [i for i in items if matches(i)]
        else:
            value = inputs.get(attribute_type)
            if value is None:
                for v in inputs.values():
                    value = v
                    break
            candidates = self.store.find_by_attribute(entity_name, attribute_type, value)

        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []

        if not candidates:
            return {"metaVersion": 1, "nodes": [], "edges": [], "root": None}

        root_payload = candidates[0]
        root_node = self._shape_node(entity_name, root_payload)
        nodes[root_node["id"]] = root_node
        self._expand_relationships(entity_name, root_payload, nodes, edges)

        return {
            "metaVersion": 1,
            "nodes": list(nodes.values()),
            "edges": edges,
            "root": root_node["id"],
        }

    def expand(self, node_type: str, business_id: str) -> Dict[str, Any]:
        if node_type in ("StockTradingLine", "OptionTradingLine", "IndexTradingLine", "FutureTradingLine"):
            payload = self.store.get_by_id(node_type, "tradingLineId", business_id)
        elif node_type == "Exchange":
            payload = self.store.get_by_id("Exchange", "mic", business_id)
        elif node_type == "IndexComposition":
            payload = self.store.get_by_id("IndexComposition", "basketId", business_id)
        else:
            payload = self.store.get_by_id(node_type, "instrumentId", business_id)

        if not payload:
            return {"metaVersion": 1, "nodes": [], "edges": [], "root": None}

        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []
        node = self._shape_node(node_type, payload)
        nodes[node["id"]] = node
        self._expand_relationships(node_type, payload, nodes, edges)
        return {"metaVersion": 1, "nodes": list(nodes.values()), "edges": edges, "root": node["id"]}

