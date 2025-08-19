import tornado.web
import tornado.escape
from typing import Any
from .meta import Meta


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


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, store, graph_service):
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

