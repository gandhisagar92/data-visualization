Reference Data Relationship Explorer

Tech Stack
- Frontend: React + TypeScript + Vite, react-force-graph-2d, Axios
- Backend: Python (Tornado), file-backed JSON store (mock DB)
- Node 20+, npm 10+, Python 3.10+

Run locally
1. Backend
   - Install deps:
     ```bash
     python3 -m pip install --break-system-packages -r /workspace/backend/requirements.txt
     ```
   - Run:
     ```bash
     python3 /workspace/backend/app.py
     ```
   - Server runs on http://localhost:8000
2. Frontend
   - Install deps and run dev server:
     ```bash
     cd /workspace/frontend
     npm install
     npm run dev
     ```
   - App runs on http://localhost:5173 and proxies /api to backend

API Contract
- GET /api/meta → Meta for dynamic UI
  Example response keys: referenceDataTypes (with queryBy + inputs), nodeAttributes
- POST /api/search
  Request example:
  ```json
  {
    "referenceDataType": "StockInstrument",
    "queryByType": "InstrumentId",
    "inputs": { "InstrumentId": "AAPL" }
  }
  ```
  Response shape:
  ```json
  {
    "metaVersion": 1,
    "nodes": [{"id": "Stock:AAPL", "type": "Stock", "label": "Apple Inc.", "attributes": {"instrumentId": "AAPL"}}],
    "edges": [{"id": "Stock:AAPL->HAS->StockTradingLine:AAPL.N", "source": "Stock:AAPL", "target": "StockTradingLine:AAPL.N", "type": "HAS"}],
    "root": "Stock:AAPL"
  }
  ```
- GET /api/node/:nodeType/:id → Full payload for a node
- GET /api/expand?nodeType=...&id=... → Expand relationships for a node

Graph Model
- Node types: Stock, StockTradingLine, Option, OptionTradingLine, Index, IndexTradingLine, Future, FutureTradingLine, Exchange, IndexComposition
- Edge types: HAS, LISTED_ON, HAS_UNDERLYING

Large Graph Strategy
- Client-side filter box narrows nodes/edges by label or attribute substring.
- Backend can add limit/cursor later to paginate large fan-outs.

ERD (conceptual)
- Stock (instrumentId, isin, name, tradingLines[])
- StockTradingLine (tradingLineId, postTradeId, ric, bloombergTicker, currency, exchangeMic)
- Option (instrumentId, isin, postTradeId, strike, contractSize, expirationDate, CallOrPut, tradingLines[], underlyingInstrumentIds[])
- OptionTradingLine (tradingLineId, ric, bloombergTicker, currency, exchangeMic)
- Index (instrumentId, isin, postTradeId, tradingLines[], compositionId)
- IndexComposition (basketId, totalConstituents, constituentStocks[])
- IndexTradingLine (tradingLineId, ric, bloombergTicker, currency, exchangeMic)
- Future (instrumentId, isin, postTradeId, contractSize, lastTradeDate, tradingLines[], underlyingInstrumentIds[])
- FutureTradingLine (tradingLineId, ric, bloombergTicker, currency, exchangeMic)
- Exchange (mic, name)

Caching
- Frontend caches node payloads by node id in-memory.
- Backend file store caches loaded JSON per file in-process.

Mock Data
- See backend/data/*.json for mock records.

Reference Data Relationship Explorer

Tech Stack
- Frontend: React + TypeScript + Vite, react-force-graph-2d, Axios
- Backend: Python (Tornado), file-backed JSON store (mock DB)
- Node 20+, npm 10+, Python 3.10+

Run locally
1. Backend
   - Install deps:
     ```bash
     python3 -m pip install --break-system-packages -r /workspace/backend/requirements.txt
     ```
   - Run:
     ```bash
     python3 /workspace/backend/app.py
     ```
   - Server runs on http://localhost:8000
2. Frontend
   - Install deps and run dev server:
     ```bash
     cd /workspace/frontend
     npm install
     npm run dev
     ```
   - App runs on http://localhost:5173 and proxies /api to backend

API Contract
- GET /api/meta → Meta for dynamic UI
  Example response keys: referenceDataTypes (with queryBy + inputs), nodeAttributes
- POST /api/search
  Request example:
  ```json
  {
    "referenceDataType": "StockInstrument",
    "queryByType": "InstrumentId",
    "inputs": { "InstrumentId": "AAPL" }
  }
  ```
  Response shape:
  ```json
  {
    "metaVersion": 1,
    "nodes": [{"id": "Stock:AAPL", "type": "Stock", "label": "Apple Inc.", "attributes": {"instrumentId": "AAPL"}}],
    "edges": [{"id": "Stock:AAPL->HAS->StockTradingLine:AAPL.N", "source": "Stock:AAPL", "target": "StockTradingLine:AAPL.N", "type": "HAS"}],
    "root": "Stock:AAPL"
  }
  ```
- GET /api/node/:nodeType/:id → Full payload for a node
- GET /api/expand?nodeType=...&id=... → Expand relationships for a node

Graph Model
- Node types: Stock, StockTradingLine, Option, OptionTradingLine, Index, IndexTradingLine, Future, FutureTradingLine, Exchange, IndexComposition
- Edge types: HAS, LISTED_ON, HAS_UNDERLYING

Large Graph Strategy
- Client-side filter box narrows nodes/edges by label or attribute substring.
- Backend can add limit/cursor later to paginate large fan-outs.

ERD (conceptual)
- Stock (instrumentId, isin, name, tradingLines[])
- StockTradingLine (tradingLineId, postTradeId, ric, bloombergTicker, currency, exchangeMic)
- Option (instrumentId, isin, postTradeId, strike, contractSize, expirationDate, CallOrPut, tradingLines[], underlyingInstrumentIds[])
- OptionTradingLine (tradingLineId, ric, bloombergTicker, currency, exchangeMic)
- Index (instrumentId, isin, postTradeId, tradingLines[], compositionId)
- IndexComposition (basketId, totalConstituents, constituentStocks[])
- IndexTradingLine (tradingLineId, ric, bloombergTicker, currency, exchangeMic)
- Future (instrumentId, isin, postTradeId, contractSize, lastTradeDate, tradingLines[], underlyingInstrumentIds[])
- FutureTradingLine (tradingLineId, ric, bloombergTicker, currency, exchangeMic)
- Exchange (mic, name)

Caching
- Frontend caches node payloads by node id in-memory.
- Backend file store caches loaded JSON per file in-process.

Mock Data
- See backend/data/*.json for mock records.

