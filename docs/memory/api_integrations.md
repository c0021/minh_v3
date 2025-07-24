# API Integrations Memory

**Purpose**: Track all external API integrations, configuration, and management decisions.

**Last Updated**: 2025-01-24  
**Status**: Planning Kimi K2 Integration  

---

## 🔑 Current API Integrations

### Sierra Chart Bridge ✅ ACTIVE
- **Purpose**: Market data and trade execution
- **Protocol**: Custom FastAPI bridge over Tailscale mesh network
- **Location**: Windows PC bridge → Linux MinhOS system
- **Status**: Stable, production-ready
- **Configuration**: `SIERRA_HOST` and `SIERRA_PORT` in `.env`

### Internal APIs ✅ ACTIVE
- **Dashboard API**: REST endpoints for UI data
- **WebSocket Streaming**: Real-time market data and AI updates
- **Decision Quality API**: Process evaluation and improvement data
- **Health Monitoring**: System status and performance metrics

## 🚀 Planned API Integrations

### NLP Provider System (Priority: HIGH) ✅ DESIGNED
- **Purpose**: API-agnostic natural language processing for chat interface
- **Architecture**: Swappable provider system with automatic fallbacks
- **Primary Provider**: Kimi K2 (API key available in `.env`)
- **Fallback Providers**: OpenAI, Anthropic, Local LLM (Ollama)
- **Use Cases**:
  - Intent parsing for trading commands
  - Parameter extraction from natural language  
  - Technical data formatting into conversational responses
  - Context-aware conversation management

### Provider Selection Strategy
```python
Provider Priority Order:
1. Kimi K2 (Primary) - Cost effective, trading focused
2. OpenAI GPT-3.5/4 (Fallback) - Reliable, well-tested
3. Anthropic Claude (Fallback) - High quality responses
4. Local LLM/Ollama (Final fallback) - Offline capability, no API costs
```

## 🏗️ Kimi K2 Integration Architecture

### Configuration Integration
```python
# minhos/core/config.py additions needed:
class AIConfig:
    kimi_k2_api_key: str = Field(env="KIMI_K2_API_KEY")
    kimi_k2_base_url: str = "https://api.moonshot.cn/v1"
    kimi_k2_model: str = "moonshot-v1-8k"
    enable_chat_interface: bool = True
    max_requests_per_minute: int = 60
    request_timeout: float = 30.0
```

### Service Integration Points
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   User Input    │────│  Kimi K2 API     │────│  MinhOS Services    │
│                 │    │                  │    │                     │
│ "Show me NVDA   │    │ • Intent: query  │    │ • ai_brain_service  │
│  RSI above 70"  │    │ • Symbol: NVDA   │    │ • sierra_client     │
│                 │    │ • Condition: RSI │    │ • dashboard_api     │
│                 │    │ • Threshold: 70  │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

### New Services Required
1. **`nlp_processor.py`**: Kimi K2 API client and request handling
2. **`chat_service.py`**: WebSocket endpoint for chat interface
3. **`intent_parser.py`**: Convert Kimi K2 responses to system commands
4. **`response_generator.py`**: Format system data for conversational output

## 💰 API Cost Management

### Kimi K2 Cost Strategy
- **Rate Limiting**: 60 requests per minute maximum
- **Request Caching**: Cache common queries to reduce API calls  
- **Response Optimization**: Minimize token usage through efficient prompts
- **Budget Monitoring**: Track daily/monthly API usage costs

### Cost Control Implementation
```python
# Rate limiting decorator
@rate_limit(requests_per_minute=60)
async def process_kimi_request(query: str) -> Dict:
    pass

# Caching layer
@cached(ttl=300)  # 5-minute cache
async def get_common_response(intent: str, params: Dict) -> str:
    pass
```

## 🔒 API Security & Configuration

### Environment Variables
```bash
# .env additions needed:
KIMI_K2_API_KEY=your_api_key_here
KIMI_K2_BASE_URL=https://api.moonshot.cn/v1
KIMI_K2_MODEL=moonshot-v1-8k
ENABLE_CHAT_INTERFACE=true
MAX_KIMI_REQUESTS_PER_MINUTE=60
```

### Security Practices
- **API Key Rotation**: Regular key rotation capability
- **Request Validation**: Sanitize all inputs before API calls
- **Error Handling**: Graceful degradation when API unavailable
- **Audit Logging**: Complete API request/response logging

## 📝 API Request Patterns

### Intent Classification
```python
# Example Kimi K2 request for intent parsing
async def parse_trading_intent(user_query: str) -> TradingIntent:
    prompt = f"""
    Parse this trading command and extract:
    - Intent: (query|execute|alert|analyze)
    - Symbol: (stock ticker if mentioned)
    - Indicator: (RSI|SMA|volume|etc if mentioned)  
    - Threshold: (numerical values)
    - Timeframe: (1m|5m|1h|1d if mentioned)
    
    Query: "{user_query}"
    
    Return as JSON.
    """
    
    response = await kimi_client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": prompt}]
    )
```

### Response Generation
```python
# Example response formatting
async def format_technical_response(data: Dict, query_context: str) -> str:
    prompt = f"""
    Convert this technical analysis data into a conversational response:
    
    Data: {json.dumps(data)}
    Original Query: "{query_context}"
    
    Make it natural, informative, and trading-focused.
    """
    
    response = await kimi_client.chat.completions.create(
        model="moonshot-v1-8k", 
        messages=[{"role": "user", "content": prompt}]
    )
```

## 🔄 API Integration Workflow

### Chat Interface Flow
1. **User Input**: Natural language query via WebSocket
2. **Intent Parsing**: Kimi K2 extracts intent and parameters
3. **System Query**: Converted to internal API calls
4. **Data Retrieval**: Fetch from AI brain, Sierra Chart, etc.
5. **Response Formatting**: Kimi K2 converts to conversational response
6. **User Output**: Formatted response via WebSocket

### Error Handling Strategy
```python
async def safe_kimi_request(query: str) -> Union[KimiResponse, FallbackResponse]:
    try:
        response = await kimi_client.request(query)
        return response
    except RateLimitError:
        return FallbackResponse("Rate limited, trying again in 60 seconds")
    except APIError as e:
        logger.error(f"Kimi API error: {e}")
        return FallbackResponse("Using basic command parsing")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return FallbackResponse("Chat interface temporarily unavailable")
```

## 📊 API Performance Monitoring

### Key Metrics to Track
- **Response Time**: Average Kimi K2 API response time
- **Success Rate**: Successful API requests percentage
- **Cost Tracking**: Daily/monthly API usage costs
- **Rate Limit Usage**: Requests per minute utilization
- **Error Rates**: Failed requests by error type

### Monitoring Implementation
```python
# API metrics collection
@track_api_metrics
async def kimi_request(query: str) -> ApiResponse:
    start_time = time.time()
    
    try:
        response = await kimi_client.request(query)
        metrics.record_success(time.time() - start_time)
        return response
    except Exception as e:
        metrics.record_error(type(e).__name__)
        raise
```

## 🎯 Future API Integrations

### Phase 2: Additional AI Services
- **OpenAI API**: Backup NLP service for redundancy
- **Anthropic Claude**: Alternative conversation model
- **Local LLM**: Ollama integration for offline capability

### Phase 3: Market Data Enhancement  
- **News APIs**: Fundamental analysis integration
- **Social Sentiment**: Twitter/Reddit sentiment analysis
- **Economic Data**: Federal Reserve economic indicators

### Phase 4: Execution Enhancement
- **Multiple Brokers**: Beyond Sierra Chart integration
- **Options Data**: Options chain and volatility data
- **Crypto Exchanges**: Cryptocurrency trading capability

## 💡 Integration Best Practices

### Design Principles
- **Loose Coupling**: APIs should be easily replaceable
- **Graceful Degradation**: System works without any single API
- **Rate Limiting**: Respect all API limits and costs
- **Monitoring**: Track performance and costs continuously

### Error Recovery Patterns
- **Circuit Breaker**: Automatically disable failing APIs
- **Retry Logic**: Exponential backoff for transient failures
- **Fallback Services**: Alternative approaches when APIs unavailable
- **User Communication**: Clear status updates for API issues

---

## 🎯 Integration Success Criteria

### Kimi K2 Integration Success
- [ ] Natural language commands successfully parsed
- [ ] Technical responses formatted conversationally  
- [ ] API costs within budget constraints
- [ ] Response time under 3 seconds average
- [ ] 95%+ uptime with graceful error handling

### Long-term API Strategy
- **Diversification**: Multiple API providers for redundancy
- **Cost Optimization**: Intelligent routing based on cost/performance
- **Local Alternatives**: Offline capabilities when possible
- **User Experience**: Seamless integration invisible to users

---

**Next Steps**: Begin Kimi K2 integration with basic intent parsing and response generation capabilities.