from typing import Any, Dict


class Meta:
    @staticmethod
    def mapping() -> Dict[str, Any]:
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

