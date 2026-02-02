# Heatmap APIs and Tools for Trading
## Research Summary: Correlation, Market, Volume & Visualization Tools

**Date:** February 2, 2026  
**Focus:** Forex SMC + Crypto Trading Applications

---

## 1. CORRELATION HEATMAP APIs

### 1.1 Polygon.io - Correlation Matrix
**Status:** ✅ Available  
**Type:** REST API  
**Cost:** Free tier available, paid plans start $99/month  
**Real-Time:** Yes (Tier dependent)  
**Authentication:** API Key  
**Rate Limits:** Free: 5 requests/min, Pro: 600 requests/min  

**Features:**
- Correlation matrices for crypto assets
- Historical correlation data
- Multiple asset pairs (forex, crypto, stocks)
- JSON response format

**API Endpoint Example:**
```
GET /v1/correlations?symbols=BTC,ETH,XRP
```

**Applicability to Project:** ⭐⭐⭐⭐ - Good for correlation tracking across crypto assets, useful for Smart Money Concepts portfolio analysis.

---

### 1.2 Finnhub - Correlation Matrix
**Status:** ✅ Available  
**Type:** REST API  
**Cost:** Free tier, Premium $99-199/month  
**Real-Time:** Real-time for premium  
**Authentication:** API Key  
**Rate Limits:** Free: 60 requests/min  

**Features:**
- Asset pair correlation
- Supports crypto and forex
- 3-month to 5-year correlation windows
- CSV export

**Applicability to Project:** ⭐⭐⭐ - Good for forex/stock correlations, less detailed for crypto.

---

### 1.3 CoinGecko API - Historical Correlation
**Status:** ✅ Available (Free)  
**Type:** REST API  
**Cost:** Free tier (rate limited), Pro $20-100/month  
**Real-Time:** Delayed (not real-time for free tier)  
**Authentication:** Optional API Key for higher limits  
**Rate Limits:** Free: 10-50 calls/second  

**Features:**
- Cryptocurrency correlation data
- Market cap, volume correlation
- Historical data (1+ years)
- CORS-enabled for frontend integration

**API Endpoint Example:**
```
GET /api/v3/coins/markets?vs_currency=usd&order=market_cap_desc
```

**Applicability to Project:** ⭐⭐⭐⭐ - Excellent for crypto correlation analysis, free and well-documented.

---

### 1.4 AlphaVantage - Correlation
**Status:** ✅ Available  
**Type:** REST API  
**Cost:** Free tier, Premium $29.99/month  
**Real-Time:** Real-time for forex  
**Authentication:** API Key  
**Rate Limits:** Free: 5 requests/min, Premium: 500 requests/min  

**Features:**
- Forex pair correlation
- Stock correlation
- JSON/CSV formats
- Time series data

**Applicability to Project:** ⭐⭐⭐ - Good for forex correlation, strong on FX pairs.

---

### 1.5 Twelve Data - Correlation & Correlation Matrix
**Status:** ✅ Available  
**Type:** REST API / WebSocket  
**Cost:** Free tier, Starter $99/month  
**Real-Time:** Real-time via WebSocket  
**Authentication:** API Key  
**Rate Limits:** Free: 800/day, Starter: 10K/day  

**Features:**
- Real-time correlation matrix
- Forex, crypto, stocks
- WebSocket support for streaming
- Multiple time intervals

**Applicability to Project:** ⭐⭐⭐⭐ - Excellent for real-time correlation tracking, WebSocket support ideal for live trading.

---

### 1.6 Quandl - Correlation API
**Status:** ⚠️ Legacy/Limited  
**Type:** REST API  
**Cost:** Acquired by Nasdaq (limited availability)  
**Real-Time:** Historical only  
**Authentication:** API Key  

**Applicability to Project:** ⭐ - Not recommended, limited ongoing support.

---

## 2. MARKET HEATMAP APIs

### 2.1 FinViz - Market Heatmap
**Status:** ✅ Available (Limited API)  
**Type:** Web-scraping / Limited REST API  
**Cost:** Free (with ads), Elite $39.99/month  
**Real-Time:** Yes  
**Authentication:** None (free), Credentials (paid)  
**Rate Limits:** Browser-based, scraping not officially supported  

**Features:**
- Stock sector heatmaps
- Real-time performance
- Visual treemap format
- Color-coded gain/loss

**Applicability to Project:** ⭐⭐ - Limited API access; mainly web-based. Not ideal for programmatic integration.

---

### 2.2 CoinGecko - Crypto Market Heatmap
**Status:** ✅ Available  
**Type:** REST API  
**Cost:** Free (rate limited), Pro $10-99/month  
**Real-Time:** Near real-time  
**Authentication:** Optional API Key  
**Rate Limits:** Free: 10-50 calls/second  

**Features:**
- Top cryptocurrency gainers/losers
- Market cap distribution
- Market dominance data
- Sector performance

**API Endpoints:**
```
GET /api/v3/coins/markets?vs_currency=usd&order=market_cap_desc
GET /api/v3/global (global market data)
GET /api/v3/coins/markets?order=gecko_desc&per_page=250 (gainers/losers)
```

**Applicability to Project:** ⭐⭐⭐⭐⭐ - Excellent, free, real-time crypto market heatmap data. Perfect for SMC crypto analysis.

---

### 2.3 CoinMarketCap - Market Heatmap & Gainers/Losers
**Status:** ✅ Available  
**Type:** REST API  
**Cost:** Free tier, Professional $28-999/month  
**Real-Time:** Real-time (Professional tier)  
**Authentication:** API Key (free accounts available)  
**Rate Limits:** Free: 30 requests/min, Pro: 10K/min  

**Features:**
- Top gainers/losers
- Market sector performance
- Trending cryptocurrencies
- Cryptocurrency listings with change %

**API Endpoints:**
```
GET /v1/cryptocurrency/listings/latest
GET /v1/cryptocurrency/trending/latest
GET /v1/cryptocurrency/market-pairs/latest
```

**Applicability to Project:** ⭐⭐⭐⭐ - Comprehensive market data, good for identifying trending assets.

---

### 2.4 Alpha Vantage - Sector Performance
**Status:** ✅ Available  
**Type:** REST API  
**Cost:** Free tier available, Premium $29.99/month  
**Real-Time:** Real-time  
**Authentication:** API Key  
**Rate Limits:** Free: 5 requests/min  

**Features:**
- Market-wide sector performance
- Top gainers/losers
- Market sentiment

**Applicability to Project:** ⭐⭐ - More stock-focused; limited crypto support.

---

### 2.5 Gecko Terminal (CoinGecko) - Advanced Heatmap
**Status:** ✅ Available  
**Type:** Web + GraphQL API  
**Cost:** Free (Gecko Terminal Pro: $30/month)  
**Real-Time:** Real-time  
**Authentication:** Optional  

**Features:**
- Network value flow visualization
- Token heatmap
- Trading pair analysis
- Real-time price changes

**Applicability to Project:** ⭐⭐⭐⭐ - Great for visualizing crypto market trends and pair correlations.

---

## 3. VOLUME PROFILE & ORDER FLOW HEATMAPS

### 3.1 Bybit API - Order Book Heatmap Data
**Status:** ✅ Available  
**Type:** REST API + WebSocket  
**Cost:** Free  
**Real-Time:** Real-time via WebSocket  
**Authentication:** API Key (optional for public endpoints)  
**Rate Limits:** Very generous, 120 requests/second  

**Features:**
- Order book data
- Real-time order flow
- Market depth visualization
- Trade history

**WebSocket Streams:**
```
ws://stream.bybit.com/v5/public/linear
Subscribe to: orderbook.1 (level 1), orderbook.50 (50 levels)
```

**Applicability to Project:** ⭐⭐⭐⭐⭐ - Excellent for volume profile and order flow analysis, perfect for SMC confluence.

---

### 3.2 Binance API - Order Book & Depth Data
**Status:** ✅ Available  
**Type:** REST API + WebSocket  
**Cost:** Free  
**Real-Time:** Real-time via WebSocket  
**Authentication:** API Key (optional for public data)  
**Rate Limits:** 1200 requests/minute (spot trading)  

**Features:**
- Real-time order book
- Depth snapshots
- Volume aggregation
- Kline (candlestick) data with volume

**WebSocket Endpoints:**
```
wss://stream.binance.com:9443/ws/<symbol>@depth
wss://stream.binance.com:9443/ws/<symbol>@klines_1m
```

**Applicability to Project:** ⭐⭐⭐⭐⭐ - Industry standard, excellent for volume profile and order flow heatmap generation.

---

### 3.3 Kraken API - Order Book & Volume
**Status:** ✅ Available  
**Type:** REST API + WebSocket  
**Cost:** Free  
**Real-Time:** Real-time via WebSocket  
**Authentication:** API Key optional for public data  
**Rate Limits:** 15 API calls per second  

**Features:**
- Real-time order book snapshots
- Trade data with volume
- Spread data
- Historical trades

**Applicability to Project:** ⭐⭐⭐⭐ - Good for decentralized volume profile data.

---

### 3.4 ATAS (Advanced Time & Sales)
**Status:** ✅ Available (Paid only)  
**Type:** Proprietary + REST API  
**Cost:** $99-499/month  
**Real-Time:** Real-time  
**Authentication:** Login credentials  

**Features:**
- Professional volume profile heatmaps
- Order book heatmaps
- Time & Sales analysis
- Cluster analysis

**Applicability to Project:** ⭐⭐⭐ - Professional-grade but expensive; overkill for many use cases.

---

### 3.5 Bookmap
**Status:** ✅ Available  
**Type:** Specialized Trading Software + API  
**Cost:** Free basic, Pro $99-299/month  
**Real-Time:** Real-time  
**Authentication:** Account login  

**Features:**
- 3D order book heatmaps
- Cluster detection
- DOM (Depth of Market) visualization
- Large trade tracking

**API Integration:** Limited; mainly visual tool, not API-first.

**Applicability to Project:** ⭐⭐⭐ - Excellent visualization but limited API access for backtesting.

---

### 3.6 Gemini API - Order Book Data
**Status:** ✅ Available  
**Type:** REST API + WebSocket  
**Cost:** Free  
**Real-Time:** Real-time via WebSocket  
**Authentication:** Optional (API Key for trading)  
**Rate Limits:** Generous for public data  

**Features:**
- Real-time order book
- Trade execution data
- Volume by price level

**Applicability to Project:** ⭐⭐⭐ - Good supplementary data source.

---

## 4. TRADINGVIEW HEATMAP INTEGRATION

### 4.1 TradingView API Limitations
**Status:** ⚠️ Limited Official Support  

**Key Points:**
- TradingView does NOT offer a direct REST API for heatmap data extraction
- They have a **Lightweight Charts** library (JavaScript) for charting
- Pine Script (TradingView's scripting language) has limitations on external API calls
- Main integration method: **Web scraping** (not officially supported, violates ToS)

**What You CAN Do:**
1. **Embed Lightweight Charts** - Use their free JavaScript library for custom heatmaps
2. **Webhooks** - TradingView can send alerts via webhooks, but NOT heatmap data
3. **Third-party integrations** - Use services that parse TradingView heatmaps

**Applicability to Project:** ⭐ - Not viable for programmatic heatmap data extraction. Better to use native APIs.

---

### 4.2 TradingView Lightweight Charts (JavaScript Library)
**Status:** ✅ Available  
**Type:** JavaScript Library  
**Cost:** Free  
**Authentication:** None  

**GitHub:** `https://github.com/tradingview/lightweight-charts`

**Use Case:** Build your own heatmap visualization using TV charting library + external data.

**Example (Pseudo):**
```javascript
import { createChart } from 'lightweight-charts';

const chart = createChart(container);
// Add your heatmap data from Binance/Bybit APIs
```

**Applicability to Project:** ⭐⭐⭐ - Good for visualization, but you provide the data from other APIs.

---

### 4.3 TradingView Alerts & Webhooks
**Status:** ✅ Available (Limited)  
**Type:** Webhook  
**Cost:** Premium feature ($14.95/month minimum)  

**Capabilities:**
- Send alerts to external webhooks
- Can post JSON with alert data
- NOT suitable for heatmap data
- Better for: Trade signals, confluence alerts

**Applicability to Project:** ⭐⭐ - Useful for alerts, not heatmaps.

---

## 5. PYTHON VISUALIZATION LIBRARIES FOR HEATMAPS

### 5.1 Seaborn (NumPy/Pandas)
**Status:** ✅ Industry Standard  
**Installation:** `pip install seaborn matplotlib`  
**Cost:** Free (Open Source)  
**Use Case:** Statistical heatmaps, correlation matrices  

**Example:**
```python
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Correlation matrix heatmap
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.show()
```

**Features:**
- Correlation matrices
- Clustering dendrograms
- Customizable color palettes
- Statistical annotations
- Great for backtesting correlation analysis

**Applicability to Project:** ⭐⭐⭐⭐⭐ - Essential for correlation heatmap generation from backtest data.

---

### 5.2 Plotly (Interactive Heatmaps)
**Status:** ✅ Modern Interactive  
**Installation:** `pip install plotly`  
**Cost:** Free (Open Source), Commercial dashboards available  
**Use Case:** Interactive web-based heatmaps  

**Example:**
```python
import plotly.graph_objects as go
import pandas as pd

fig = go.Figure(data=go.Heatmap(
    z=correlation_matrix.values,
    x=correlation_matrix.columns,
    y=correlation_matrix.index,
    colorscale='RdBu'
))
fig.show()
```

**Features:**
- Interactive hover tooltips
- Web-exportable HTML
- 3D heatmaps
- Real-time updates possible
- Great for dashboards

**Applicability to Project:** ⭐⭐⭐⭐⭐ - Perfect for interactive trading dashboards and real-time heatmap visualization.

---

### 5.3 Matplotlib (Low-Level Control)
**Status:** ✅ Foundational  
**Installation:** `pip install matplotlib`  
**Cost:** Free (Open Source)  
**Use Case:** Custom heatmaps, publication-quality graphics  

**Example:**
```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
im = ax.imshow(data, cmap='viridis')
plt.colorbar(im)
```

**Features:**
- Maximum control
- Non-interactive (save to file)
- Lightweight
- Integrates with Seaborn/Plotly

**Applicability to Project:** ⭐⭐⭐ - Good for static heatmaps in reports.

---

### 5.4 PyHeatMap
**Status:** ✅ Lightweight  
**Installation:** `pip install pyheatmap`  
**Cost:** Free (Open Source)  
**Use Case:** Simple heatmap generation from coordinates  

**Applicability to Project:** ⭐ - Overkill for trading, more suited for geographic heatmaps.

---

### 5.5 Altair (Vega-Lite)
**Status:** ✅ Modern, Declarative  
**Installation:** `pip install altair`  
**Cost:** Free (Open Source)  
**Use Case:** Declarative interactive visualizations  

**Example:**
```python
import altair as alt
import pandas as pd

alt.Chart(data).mark_rect().encode(
    x='ticker:O',
    y='date:O',
    color='correlation:Q'
).interactive()
```

**Features:**
- Clean declarative syntax
- Web-exportable
- Interactive selections
- Great for exploration

**Applicability to Project:** ⭐⭐⭐⭐ - Good for exploratory analysis and dashboard prototyping.

---

### 5.6 Folium (Geo-Based Heatmaps)
**Status:** ✅ Specialized  
**Installation:** `pip install folium`  
**Cost:** Free (Open Source)  
**Use Case:** Geographic heatmap overlays (not relevant for trading)

**Applicability to Project:** ⭐ - Not applicable.

---

### 5.7 Bokeh
**Status:** ✅ Interactive & Server-Side  
**Installation:** `pip install bokeh`  
**Cost:** Free (Open Source)  
**Use Case:** Interactive dashboards with real-time updates  

**Example:**
```python
from bokeh.plotting import figure
from bokeh.models import HoverTool

p = figure(title='Heatmap')
# Custom heatmap implementation with bokeh rectangles
```

**Features:**
- Real-time streaming capability
- Server-side interactivity
- WebSocket support
- Production dashboards

**Applicability to Project:** ⭐⭐⭐⭐⭐ - Excellent for real-time trading dashboards with live heatmap updates.

---

## 6. RECOMMENDED STACK FOR YOUR PROJECT

### Recommended Combination for Forex SMC + Crypto Trading:

**For Real-Time Data Collection:**
1. **Binance API** (order book, volume) - primary crypto venue
2. **Bybit API** (order flow, derivatives) - secondary crypto venue
3. **Twelve Data** (correlation) - real-time correlation matrices
4. **CoinGecko API** (market heatmap) - free, comprehensive crypto data

**For Backtesting & Analysis:**
1. **Seaborn** - correlation matrix heatmaps
2. **Plotly** - interactive backtest result visualization
3. **Bokeh** - real-time dashboard with live heatmap updates

**For Live Trading Dashboard:**
1. **Bokeh/Plotly** - front-end visualization
2. **Binance/Bybit WebSocket** - real-time data feeds
3. **Custom Python correlation engine** - real-time correlation calculations

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: Correlation Heatmap (Highest Priority)
```python
# Use: CoinGecko (free) + Seaborn/Plotly
# Goal: Build correlation matrix for forex/crypto pairs
# Features: 1-hour, 4-hour, daily correlation visualization
```

### Phase 2: Market Performance Heatmap
```python
# Use: CoinGecko API + Plotly/Bokeh
# Goal: Real-time gainers/losers heatmap
# Features: Color-coded by performance %, sector grouping
```

### Phase 3: Volume Profile Heatmap
```python
# Use: Binance WebSocket + Custom aggregation + Plotly
# Goal: Order book depth visualization
# Features: Price level clustering, support/resistance identification
```

### Phase 4: SMC Confluence Heatmap
```python
# Use: All above + custom SMC logic
# Goal: Multi-factor confluence heatmap
# Features: Correlation + Volume + Price Action layers
```

---

## 8. COST SUMMARY

| Tool | Monthly Cost | Real-Time | Best For |
|------|-------------|-----------|----------|
| **CoinGecko** | Free-$99 | Near real-time | Crypto correlation & market data |
| **CoinMarketCap** | Free-$999 | Real-time (Pro) | Trending assets, market sentiment |
| **Binance API** | Free | Real-time | Order book, volume profile |
| **Bybit API** | Free | Real-time | Derivatives order flow |
| **Twelve Data** | Free-$99 | Real-time | Forex correlation |
| **Polygon.io** | Free-$99 | Real-time (Pro) | Crypto correlation matrix |
| **Seaborn** | Free | N/A | Static heatmap generation |
| **Plotly** | Free-$999 | Real-time capable | Interactive dashboards |
| **Bokeh** | Free | Real-time capable | Live trading dashboards |

**Total Estimated Monthly Cost for Full Setup:** $0-100 (using free tiers primarily)

---

## 9. RECOMMENDATIONS BY USE CASE

### For SMC + Correlation Analysis:
✅ **CoinGecko API** (free) → **Seaborn** (visualization) → **Plotly** (interactive)

### For Real-Time Volume Profile:
✅ **Binance WebSocket** → Custom aggregation → **Plotly** real-time heatmap

### For Live Trading Dashboard:
✅ **Bybit API + Binance API** → **Bokeh** (server with WebSocket) → Dashboard

### For Backtesting Confluence:
✅ **Historical data from Binance** → **Seaborn/Plotly** correlation analysis → Multi-factor confluence heatmap

---

## 10. API AUTHENTICATION SUMMARY

| Provider | Auth Type | Key Requirement | Free Tier |
|----------|-----------|-----------------|-----------|
| CoinGecko | API Key (optional) | No key needed for basic | Yes |
| CoinMarketCap | API Key | Required (free signup) | Yes |
| Binance | None (public data) | Optional for private | Yes |
| Bybit | None (public data) | Optional for private | Yes |
| Twelve Data | API Key | Required (free tier) | Yes |
| Polygon.io | API Key | Required | Yes |
| Seaborn | N/A (library) | N/A | Yes |
| Plotly | N/A (library) | Optional (Cloud) | Yes |
| Bokeh | N/A (library) | N/A | Yes |

---

## CONCLUSION

For your **Forex SMC + Crypto Trading** project, the optimal approach is:

1. **Free data collection**: CoinGecko + Binance + Bybit APIs
2. **Correlation analysis**: Python with Seaborn for static, Plotly for interactive
3. **Real-time dashboards**: Bokeh server with WebSocket integration
4. **Volume profiling**: Direct order book feeds from Binance/Bybit

**No major software costs required** — the entire stack can be built using free APIs and open-source libraries. The only optional paid subscriptions would be for enhanced rate limits or premium features as you scale.
