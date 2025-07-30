# Sierra Chart market data retrieval for Minh OS: Alternative solutions beyond DTC protocol

Your experience with Sierra Chart blocking DTC protocol for data access while allowing trade execution is confirmed by recent official statements. As of December 2024, Sierra Chart explicitly prohibits market data access through DTC due to exchange licensing requirements, even for localhost connections. This restriction affects CME, EUREX, NASDAQ, and other major exchanges.

## Why DTC is blocked for data but not trading

The core issue stems from different regulatory frameworks. Market data distribution requires specific exchange licenses and compliance monitoring that Sierra Chart cannot extend to third-party applications. Trading orders, however, flow through established broker relationships already covered by existing agreements. Sierra Chart Engineering stated definitively in December 2024: "Access cannot be allowed" for data via DTC, with no exceptions for personal use or same-machine access.

## Primary alternative: ACSIL (Advanced Custom Study Interface Language)

ACSIL emerges as Sierra Chart's officially recommended solution for programmatic data access. This C++ interface runs within Sierra Chart's process, providing direct memory access to all market data without licensing restrictions.

**Key ACSIL capabilities:**
- Direct access to real-time OHLCV data through `sc.BaseData[][]` arrays
- Market depth and time & sales data
- Cross-chart data access for multi-timeframe analysis
- Historical data retrieval
- Custom data export to files or network streams

**Implementation approach:**
```cpp
// Access current bar data
float open = sc.BaseData[SC_OPEN][sc.Index];
float high = sc.BaseData[SC_HIGH][sc.Index];
float volume = sc.BaseData[SC_VOLUME][sc.Index];

// Export to external system via file or socket
```

ACSIL studies compile to DLLs that can implement custom network protocols, write to files, or use Windows inter-process communication to share data with Minh OS.

## Secondary solution: Direct SCID file access

Sierra Chart stores all data in binary SCID files with a well-documented format. These files update every 5 seconds by default and support shared read access.

**SCID file structure:**
- 56-byte header containing file identification and versioning
- 40-byte records with microsecond timestamps and OHLCV data
- Location: Sierra Chart Data Files Folder
- Multiple community libraries available (Python, C++)

The `ReadSierraChartData` project on GitHub provides working implementations for parsing these files externally, offering a straightforward path for historical data access without any API restrictions.

## Community-developed Python solution: SC-Py

Despite DTC limitations, the community has developed SC-Py, a professional Python library that successfully accesses Sierra Chart data:

**SC-Py features:**
- Real-time and historical market data
- Time & sales, bid/ask quotes, market depth
- Chart data with various timeframes
- Order management capabilities
- Production-ready with active maintenance

This solution works by implementing local proxy methods and leveraging allowed connection types, though it requires careful configuration to avoid licensing issues.

## File-based export methods

Sierra Chart provides multiple built-in studies for continuous data export:

**Spreadsheet Studies approach:**
- Outputs all chart and study data to Excel-compatible format
- Automatic file saves at configurable intervals
- Supports tick-by-tick data with "1 trade per bar" setting
- Low implementation complexity

**"Write Bar and Study Data to File" study:**
- Continuous export of market data to text files
- Configurable formats and update frequencies
- Suitable for feeding external systems

These methods trade some latency for simplicity and reliability, making them ideal for non-HFT strategies.

## Recommended implementation strategy for Minh OS

Based on your requirements for a quantitative trading system, I recommend a hybrid approach:

**Phase 1: Immediate implementation**
Start with ACSIL for real-time data access. Develop a custom study that:
- Captures market data directly from Sierra Chart's memory
- Exports to a high-performance IPC mechanism (named pipes or memory-mapped files)
- Provides sub-millisecond latency for critical data

**Phase 2: Historical data pipeline**
Implement SCID file parsing for historical analysis:
- Use existing Python/C++ libraries to read binary data
- Build a separate process that monitors and parses updated files
- Create a data warehouse for backtesting and research

**Phase 3: Redundancy and scaling**
Add file-based export for redundancy:
- Configure Spreadsheet Studies for continuous export
- Implement file watchers in Minh OS
- Use as fallback when primary methods fail

## Technical implementation details

**ACSIL development setup:**
1. Install Visual Studio with C++ support
2. Configure Sierra Chart's ACS_Source folder
3. Use provided ACSIL examples as templates
4. Compile studies to DLL format
5. Load in Sierra Chart for testing

**Network communication from ACSIL:**
```cpp
// Socket creation within ACSIL study
SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
// Send market data to Minh OS
send(sock, data_buffer, size, 0);
```

**SCID file parsing (Python example):**
```python
struct.unpack('<Qffff4I', record_bytes)  # DateTime, OHLC, volumes
```

## Best practices for production deployment

1. **Avoid remote DTC connections** - Sierra Chart counts these as additional machines requiring extra licenses
2. **Use localhost proxy if needed** - Community workaround for external access while maintaining compliance
3. **Implement robust error handling** - File locks and Sierra Chart restarts require graceful recovery
4. **Monitor data staleness** - SCID files update periodically; implement freshness checks
5. **Respect licensing terms** - Ensure your implementation complies with both Sierra Chart and exchange requirements

## Recent changes and future considerations

Sierra Chart has progressively tightened DTC data access throughout 2024, with the December update confirming no exceptions for localhost access to CME data. However, they continue to enhance ACSIL capabilities and maintain strong support for file-based integration methods. The platform's commitment to these alternative methods suggests they will remain viable long-term solutions.

The combination of ACSIL for low-latency access and SCID parsing for historical data provides a robust, officially supported path forward for Minh OS integration without relying on the restricted DTC protocol for market data.