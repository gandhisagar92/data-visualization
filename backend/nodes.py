from typing import Any, Dict, List, Optional, Tuple
import logging
from store import FileJsonStore


logger = logging.getLogger(__name__)


class BaseNode:
    def __init__(self, store: FileJsonStore, ref_data_type: str, **kwargs):
        self.store = store
        self.ref_data_type = ref_data_type
        self.node_id: str = ''
        self.label: str = ''
        self.source: Optional[str] = None
        self.attributes: Optional[Dict[str, Any]] = None
        self.payload: Optional[Dict[str, Any]] = None
        self.linked_nodes: Optional[List[Dict[str, str]]] = None
        self.params = kwargs

    def fetch_data(self, **kwargs) -> None:
        raise NotImplementedError

    def to_graph_node(self) -> Dict[str, Any]:
        return {
            'id': f"{self.ref_data_type}:{self.node_id}",
            'type': self.ref_data_type,
            'label': self.label,
            'attributes': self.attributes or {},
        }


class Stock(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'Stock', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        instrument_id = self.params.get('InstrumentId') or self.params.get('instrumentId')
        isin = self.params.get('ISIN')
        # simple attribute-based lookup
        payload = None
        if instrument_id:
            payload = self.store.get_by_id('Stock', 'instrumentId', instrument_id)
        if not payload and isin:
            matches = self.store.find_by_attribute('Stock', 'isin', isin)
            payload = matches[0] if matches else None
        if not payload:
            logger.info('Stock not found for %s', self.params)
            return
        self.payload = payload
        self.node_id = payload.get('instrumentId')
        self.label = payload.get('name') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('tradingLines')}
        # linked trading lines
        self.linked_nodes = []
        for tl in payload.get('tradingLines', []):
            self.linked_nodes.append({'type': 'StockTradingLine', 'id': tl, 'rel': 'HAS'})


class StockTradingLine(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'StockTradingLine', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        tl_id = self.params.get('TradingLineId') or self.params.get('tradingLineId')
        if not tl_id:
            return
        payload = self.store.get_by_id('StockTradingLine', 'tradingLineId', tl_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('tradingLineId')
        self.label = payload.get('ric') or payload.get('bloombergTicker') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('exchangeMic')}
        mic = payload.get('exchangeMic')
        self.linked_nodes = []
        if mic:
            self.linked_nodes.append({'type': 'Exchange', 'id': mic, 'rel': 'LISTED_ON'})


class Exchange(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'Exchange', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        mic = self.params.get('mic') or self.params.get('MIC') or self.params.get('id')
        if not mic:
            return
        payload = self.store.get_by_id('Exchange', 'mic', mic)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('mic')
        self.label = payload.get('name') or self.node_id
        self.attributes = payload
        self.linked_nodes = []


class Option(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'Option', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        instrument_id = self.params.get('InstrumentId') or self.params.get('instrumentId')
        payload = None
        if instrument_id:
            payload = self.store.get_by_id('Option', 'instrumentId', instrument_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('instrumentId')
        self.label = payload.get('bloombergTicker') or payload.get('ric') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('tradingLines', 'underlyingInstrumentIds')}
        self.linked_nodes = []
        for tl in payload.get('tradingLines', []):
            self.linked_nodes.append({'type': 'OptionTradingLine', 'id': tl, 'rel': 'HAS'})
        for und in payload.get('underlyingInstrumentIds', []):
            # Could be Stock or Index; try Stock first then Index
            self.linked_nodes.append({'type': 'Stock', 'id': und, 'rel': 'HAS_UNDERLYING'})
            self.linked_nodes.append({'type': 'Index', 'id': und, 'rel': 'HAS_UNDERLYING'})


class OptionTradingLine(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'OptionTradingLine', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        tl_id = self.params.get('TradingLineId') or self.params.get('tradingLineId')
        if not tl_id:
            return
        payload = self.store.get_by_id('OptionTradingLine', 'tradingLineId', tl_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('tradingLineId')
        self.label = payload.get('ric') or payload.get('bloombergTicker') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('exchangeMic')}
        mic = payload.get('exchangeMic')
        self.linked_nodes = []
        if mic:
            self.linked_nodes.append({'type': 'Exchange', 'id': mic, 'rel': 'LISTED_ON'})


class Future(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'Future', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        instrument_id = self.params.get('InstrumentId') or self.params.get('instrumentId')
        payload = None
        if instrument_id:
            payload = self.store.get_by_id('Future', 'instrumentId', instrument_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('instrumentId')
        self.label = payload.get('bloombergTicker') or payload.get('ric') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('tradingLines', 'underlyingInstrumentIds')}
        self.linked_nodes = []
        for tl in payload.get('tradingLines', []):
            self.linked_nodes.append({'type': 'FutureTradingLine', 'id': tl, 'rel': 'HAS'})
        for und in payload.get('underlyingInstrumentIds', []):
            self.linked_nodes.append({'type': 'Stock', 'id': und, 'rel': 'HAS_UNDERLYING'})
            self.linked_nodes.append({'type': 'Index', 'id': und, 'rel': 'HAS_UNDERLYING'})


class FutureTradingLine(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'FutureTradingLine', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        tl_id = self.params.get('TradingLineId') or self.params.get('tradingLineId')
        if not tl_id:
            return
        payload = self.store.get_by_id('FutureTradingLine', 'tradingLineId', tl_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('tradingLineId')
        self.label = payload.get('ric') or payload.get('bloombergTicker') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('exchangeMic')}
        mic = payload.get('exchangeMic')
        self.linked_nodes = []
        if mic:
            self.linked_nodes.append({'type': 'Exchange', 'id': mic, 'rel': 'LISTED_ON'})


class Index(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'Index', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        instrument_id = self.params.get('InstrumentId') or self.params.get('instrumentId')
        isin = self.params.get('ISIN')
        payload = None
        if instrument_id:
            payload = self.store.get_by_id('Index', 'instrumentId', instrument_id)
        if not payload and isin:
            matches = self.store.find_by_attribute('Index', 'isin', isin)
            payload = matches[0] if matches else None
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('instrumentId')
        self.label = payload.get('name') or payload.get('ric') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('tradingLines', 'compositionId')}
        self.linked_nodes = []
        for tl in payload.get('tradingLines', []):
            self.linked_nodes.append({'type': 'IndexTradingLine', 'id': tl, 'rel': 'HAS'})
        comp = payload.get('compositionId')
        if comp:
            self.linked_nodes.append({'type': 'IndexComposition', 'id': comp, 'rel': 'HAS'})


class IndexTradingLine(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'IndexTradingLine', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        tl_id = self.params.get('TradingLineId') or self.params.get('tradingLineId')
        if not tl_id:
            return
        payload = self.store.get_by_id('IndexTradingLine', 'tradingLineId', tl_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('tradingLineId')
        self.label = payload.get('ric') or payload.get('bloombergTicker') or self.node_id
        self.attributes = {k: v for k, v in payload.items() if k not in ('exchangeMic')}
        mic = payload.get('exchangeMic')
        self.linked_nodes = []
        if mic:
            self.linked_nodes.append({'type': 'Exchange', 'id': mic, 'rel': 'LISTED_ON'})


class IndexComposition(BaseNode):
    def __init__(self, store: FileJsonStore, **kwargs):
        super().__init__(store, 'IndexComposition', **kwargs)

    def fetch_data(self, **kwargs) -> None:
        basket_id = self.params.get('basketId') or self.params.get('id')
        if not basket_id:
            return
        payload = self.store.get_by_id('IndexComposition', 'basketId', basket_id)
        if not payload:
            return
        self.payload = payload
        self.node_id = payload.get('basketId')
        self.label = f"Basket {self.node_id}"
        self.attributes = {k: v for k, v in payload.items() if k != 'constituentStocks'}
        self.linked_nodes = []
        for stk in payload.get('constituentStocks', []):
            self.linked_nodes.append({'type': 'Stock', 'id': stk, 'rel': 'HAS'})


NODE_REGISTRY: Dict[str, Any] = {
    'Stock': Stock,
    'StockTradingLine': StockTradingLine,
    'Exchange': Exchange,
    'Option': Option,
    'OptionTradingLine': OptionTradingLine,
    'Future': Future,
    'FutureTradingLine': FutureTradingLine,
    'Index': Index,
    'IndexTradingLine': IndexTradingLine,
    'IndexComposition': IndexComposition,
}

