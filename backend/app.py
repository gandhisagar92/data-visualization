import json
import os
from typing import Any, Dict, List, Tuple

import tornado.ioloop
import tornado.web
import tornado.escape


WORKDIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORKDIR, "data")


def cors(fn):
    async def wrapper(self: "BaseHandler", *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        if self.request.method == "OPTIONS":
            self.set_status(204)
            self.finish()
            return
        return await fn(self, *args, **kwargs)

    return wrapper


class FileJsonStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.cache: Dict[str, List[Dict[str, Any]]] = {}

    def _load_file(self, name: str) -> List[Dict[str, Any]]:
        if name in self.cache:
            return self.cache[name]
        path = os.path.join(self.data_dir, f"{name}.json")
        if not os.path.exists(path):
            self.cache[name] = []
            return self.cache[name]
        with open(path, "r", encoding="utf-8") as f:
            self.cache[name] = json.load(f)
        return self.cache[name]

    def list_all(self, name: str) -> List[Dict[str, Any]]:
        return self._load_file(name)

    def find_by_attribute(self, name: str, attribute_type: str, attribute_id: Any) -> List[Dict[str, Any]]:
        items = self._load_file(name)
        matched: List[Dict[str, Any]] = []
        for item in items:
            if attribute_type in item and str(item.get(attribute_type)) == str(attribute_id):
                matched.append(item)
        return matched

    def get_by_id(self, name: str, primary_key: str, value: Any) -> Dict[str, Any] | None:
        items = self._load_file(name)
        for item in items:
            if str(item.get(primary_key)) == str(value):
                return item
        return None


class Meta:
    @staticmethod
    def mapping() -> Dict[str, Any]:
        # Dynamic input schema for the UI
        return {
            "referenceDataTypes": [
                {
                    "type": "StockInstrument",
                    "display": "Stock",
                    "queryBy": [
                        {"type": "InstrumentId", "inputs": [{"id": "InstrumentId", "label": "Instrument ID", "kind": "text"}]},
                        {"type": "ISIN", "inputs": [{"id": "ISIN", "label": "ISIN", "kind": "text"}]},
                        {"type": "TradingLineId", "inputs": [{"id": "TradingLineId", "label": "Trading Line ID", "kind": "text"}]},
                        {"type": "PostTradeId", "inputs": [{"id": "PostTradeId", "label": "Post Trade ID", "kind": "text"}]},
                        {"type": "RIC", "inputs": [{"id": "RIC", "label": "RIC", "kind": "text"}]},
                        {"type": "BloombergTicker", "inputs": [{"id": "BloombergTicker", "label": "Bloomberg Ticker", "kind": "text"}]},
                    ],
                },
                {
                    "type": "OptionInstrument",
                    "display": "Option",
                    "queryBy": [
                        {"type": "InstrumentId", "inputs": [{"id": "InstrumentId", "label": "Instrument ID", "kind": "text"}]},
                        {"type": "RIC", "inputs": [{"id": "RIC", "label": "RIC", "kind": "text"}]},
                        {"type": "TradingLineId", "inputs": [{"id": "TradingLineId", "label": "Trading Line ID", "kind": "text"}]},
                        {"type": "OCCSymbol", "inputs": [{"id": "OCCSymbol", "label": "OCC Symbol", "kind": "text"}]},
                        {"type": "PostTradeId", "inputs": [{"id": "PostTradeId", "label": "Post Trade ID", "kind": "text"}]},
                        {"type": "ISIN", "inputs": [{"id": "ISIN", "label": "ISIN", "kind": "text"}]},
                        {"type": "BloombergTicker", "inputs": [{"id": "BloombergTicker", "label": "Bloomberg Ticker", "kind": "text"}]},
                        {"type": "UnderlyingTradingLineId", "inputs": [{"id": "UnderlyingTradingLineId", "label": "Underlying Trading Line ID", "kind": "text"}]},
                        {"type": "UnderlyingInstrumentId", "inputs": [{"id": "UnderlyingInstrumentId", "label": "Underlying Instrument ID", "kind": "text"}]},
                        {
                            "type": "Economics",
                            "inputs": [
                                {"id": "UnderlyingId", "label": "Underlying (InstrumentId or TradingLineId)", "kind": "text"},
                                {"id": "Strike", "label": "Strike Price", "kind": "number"},
                                {"id": "ContractSize", "label": "Contract Size", "kind": "number"},
                                {"id": "ExpirationDate", "label": "Expiration Date", "kind": "date"},
                                {"id": "CallOrPut", "label": "Call or Put", "kind": "select", "options": ["Call", "Put"]},
                            ],
                        },
                    ],
                },
                {
                    "type": "FutureInstrument",
                    "display": "Future",
                    "queryBy": [
                        {"type": "InstrumentId", "inputs": [{"id": "InstrumentId", "label": "Instrument ID", "kind": "text"}]},
                        {"type": "RIC", "inputs": [{"id": "RIC", "label": "RIC", "kind": "text"}]},
                        {"type": "TradingLineId", "inputs": [{"id": "TradingLineId", "label": "Trading Line ID", "kind": "text"}]},
                        {"type": "OCCSymbol", "inputs": [{"id": "OCCSymbol", "label": "OCC Symbol", "kind": "text"}]},
                        {"type": "PostTradeId", "inputs": [{"id": "PostTradeId", "label": "Post Trade ID", "kind": "text"}]},
                        {"type": "ISIN", "inputs": [{"id": "ISIN", "label": "ISIN", "kind": "text"}]},
                        {"type": "BloombergTicker", "inputs": [{"id": "BloombergTicker", "label": "Bloomberg Ticker", "kind": "text"}]},
                        {"type": "UnderlyingTradingLineId", "inputs": [{"id": "UnderlyingTradingLineId", "label": "Underlying Trading Line ID", "kind": "text"}]},
                        {"type": "UnderlyingInstrumentId", "inputs": [{"id": "UnderlyingInstrumentId", "label": "Underlying Instrument ID", "kind": "text"}]},
                        {
                            "type": "Economics",
                            "inputs": [
                                {"id": "UnderlyingId", "label": "Underlying (InstrumentId or TradingLineId)", "kind": "text"},
                                {"id": "Strike", "label": "Strike Price", "kind": "number"},
                                {"id": "ContractSize", "label": "Contract Size", "kind": "number"},
                                {"id": "ExpirationDate", "label": "Expiration Date", "kind": "date"},
                                {"id": "CallOrPut", "label": "Call or Put", "kind": "select", "options": ["Call", "Put"]},
                            ],
                        },
                    ],
                },
                {
                    "type": "IndexInstrument",
                    "display": "Index",
                    "queryBy": [
                        {"type": "InstrumentId", "inputs": [{"id": "InstrumentId", "label": "Instrument ID", "kind": "text"}]},
                        {"type": "ISIN", "inputs": [{"id": "ISIN", "label": "ISIN", "kind": "text"}]},
                        {"type": "TradingLineId", "inputs": [{"id": "TradingLineId", "label": "Trading Line ID", "kind": "text"}]},
                        {"type": "PostTradeId", "inputs": [{"id": "PostTradeId", "label": "Post Trade ID", "kind": "text"}]},
                        {"type": "RIC", "inputs": [{"id": "RIC", "label": "RIC", "kind": "text"}]},
                        {"type": "BloombergTicker", "inputs": [{"id": "BloombergTicker", "label": "Bloomberg Ticker", "kind": "text"}]},
                    ],
                },
            ],
            "nodeAttributes": {
                "Stock": ["instrumentId", "isin"],
                "StockTradingLine": ["tradingLineId", "postTradeId", "ric", "bloombergTicker", "currency"],
                "Option": ["instrumentId", "isin", "postTradeId", "strike", "contractSize", "expirationDate", "CallOrPut"],
                "OptionTradingLine": ["tradingLineId", "ric", "bloombergTicker", "currency", "tradingSession"],
                "Index": ["instrumentId", "isin", "postTradeId"],
                "IndexTradingLine": ["tradingLineId", "ric", "bloombergTicker", "currency", "tradingSession"],
                "Future": ["instrumentId", "isin", "postTradeId", "contractSize", "lastTradeDate"],
                "FutureTradingLine": ["tradingLineId", "ric", "bloombergTicker", "currency", "pricingSession"],
                "IndexComposition": ["basketId", "totalConstituents"],
                "Exchange": ["mic"],
            },
        }


class GraphService:
    def __init__(self, store: FileJsonStore):
        self.store = store

    def _graph_node_id(self, node_type: str, business_id: str) -> str:
        return f"{node_type}:{business_id}"

    def _shape_node(self, node_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Choose best display label
        label = payload.get("name") or payload.get("ric") or payload.get("bloombergTicker") or payload.get("instrumentId") or payload.get("tradingLineId") or payload.get("mic") or payload.get("basketId")
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

        # Relationship rules per spec
        if node_type == "Stock":
            # HAS StockTradingLine
            for tl_id in payload.get("tradingLines", []):
                tl = self.store.get_by_id("StockTradingLine", "tradingLineId", tl_id)
                if not tl:
                    continue
                tl_node = self._shape_node("StockTradingLine", tl)
                nodes[tl_node["id"]] = tl_node
                self._add_edge(edges, node_id, tl_node["id"], "HAS")
                # LISTED_ON Exchange
                mic = tl.get("exchangeMic")
                if mic:
                    ex = self.store.get_by_id("Exchange", "mic", mic)
                    if ex:
                        ex_node = self._shape_node("Exchange", ex)
                        nodes[ex_node["id"]] = ex_node
                        self._add_edge(edges, tl_node["id"], ex_node["id"], "LISTED_ON")

        if node_type == "Option":
            # HAS OptionTradingLine
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
            # HAS_UNDERLYING Stock or Index
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
        # Determine entity and attribute mapping for lookup
        type_to_entity = {
            "StockInstrument": ("Stock", "instrumentId"),
            "OptionInstrument": ("Option", "instrumentId"),
            "FutureInstrument": ("Future", "instrumentId"),
            "IndexInstrument": ("Index", "instrumentId"),
        }
        if reference_data_type not in type_to_entity:
            return {"error": f"Unsupported referenceDataType {reference_data_type}"}

        entity_name, default_pk = type_to_entity[reference_data_type]
        attribute_type = query_by_type

        # Economics query can be simplified to match by attributes
        if attribute_type == "Economics":
            # Match options/futures by economics attributes
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
            value = None
            # All other queries assume a single text input matching the attribute name
            # Inputs may have either the same key as query_by_type or a common 'value'
            if attribute_type in inputs:
                value = inputs.get(attribute_type)
            else:
                # fallback to any first value
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
        # Load node
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


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, store: FileJsonStore, graph_service: GraphService):
        self.store = store
        self.graph_service = graph_service


class MetaHandler(BaseHandler):
    @cors
    async def get(self):
        self.write(Meta.mapping())


class SearchHandler(BaseHandler):
    @cors
    async def post(self):
        try:
            data = tornado.escape.json_decode(self.request.body or b"{}")
        except Exception:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
            return

        ref_type = data.get("referenceDataType")
        query_by = data.get("queryByType")
        inputs = data.get("inputs", {})

        result = self.graph_service.search(ref_type, query_by, inputs)
        self.write(result)


class NodeHandler(BaseHandler):
    @cors
    async def get(self, node_type: str, business_id: str):
        # Determine PK per node type
        if node_type in ("StockTradingLine", "OptionTradingLine", "IndexTradingLine", "FutureTradingLine"):
            payload = self.store.get_by_id(node_type, "tradingLineId", business_id)
        elif node_type == "Exchange":
            payload = self.store.get_by_id("Exchange", "mic", business_id)
        elif node_type == "IndexComposition":
            payload = self.store.get_by_id("IndexComposition", "basketId", business_id)
        else:
            payload = self.store.get_by_id(node_type, "instrumentId", business_id)

        if payload:
            self.write(payload)
        else:
            self.set_status(404)
            self.write({"error": "Not found"})


class ExpandHandler(BaseHandler):
    @cors
    async def get(self):
        node_type = self.get_query_argument("nodeType", None)
        business_id = self.get_query_argument("id", None)
        if not node_type or not business_id:
            self.set_status(400)
            self.write({"error": "nodeType and id are required"})
            return
        result = self.graph_service.expand(node_type, business_id)
        self.write(result)


def make_app() -> tornado.web.Application:
    store = FileJsonStore(DATA_DIR)
    graph_service = GraphService(store)
    return tornado.web.Application(
        [
            (r"/api/meta", MetaHandler, dict(store=store, graph_service=graph_service)),
            (r"/api/search", SearchHandler, dict(store=store, graph_service=graph_service)),
            (r"/api/node/(.+?)/(.+)", NodeHandler, dict(store=store, graph_service=graph_service)),
            (r"/api/expand", ExpandHandler, dict(store=store, graph_service=graph_service)),
        ],
        debug=True,
    )


def main():
    port = int(os.environ.get("PORT", "8000"))
    app = make_app()
    app.listen(port)
    print(f"Backend listening on http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

