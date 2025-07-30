// Base JavaScript - Core Functions (<500 lines)

// Global variables
let ws = null;
let reconnectInterval = null;

// WebSocket connection management
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function() {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
        addLog('Connected to MinhOS server', 'success');
        
        // Clear reconnect interval
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = function() {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        addLog('Disconnected from server', 'error');
        
        // Attempt to reconnect
        if (!reconnectInterval) {
            reconnectInterval = setInterval(connectWebSocket, 5000);
        }
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        addLog('Connection error', 'error');
    };
}

function handleWebSocketMessage(data) {
    if (data.type === 'initial' || data.timestamp) {
        updateDashboard(data.type === 'initial' ? data.data : data);
    }
}

// Dashboard update functions
function updateDashboard(data) {
    // Update system status
    if (data.system) {
        document.getElementById('system-status').textContent = 
            data.system.health ? 'Healthy' : 'Degraded';
        
        const modeElement = document.getElementById('trading-mode');
        modeElement.textContent = data.system.mode.toUpperCase();
        modeElement.className = 'trading-mode mode-' + 
            (data.system.mode === 'manual' ? 'manual' : 
             data.system.mode === 'semi_auto' ? 'semi' : 'auto');
    }
    
    // Update trading info
    if (data.trading) {
        document.getElementById('positions-count').textContent = 
            data.trading.positions || '0';
        document.getElementById('total-pnl').textContent = 
            '$' + (data.trading.pnl || 0).toFixed(2);
    }
    
    // Update market data
    if (data.market) {
        updateMarketData(data.market);
    }
}

function updateMarketData(marketData) {
    // Update primary symbol price if available
    if (marketData.price && marketData.symbol) {
        const nqPriceElements = document.querySelectorAll('.market-symbol');
        nqPriceElements.forEach(element => {
            if (element.textContent === 'NQ') {
                const priceElement = element.nextElementSibling;
                if (priceElement && priceElement.classList.contains('market-price')) {
                    priceElement.textContent = '$' + marketData.price.toFixed(2);
                }
            }
        });
    }
}

// Connection status management
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-indicator');
    const text = document.getElementById('connection-text');
    
    if (connected) {
        indicator.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// Logging system
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    if (!logContainer) return;
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // Keep only last 100 entries
    while (logContainer.children.length > 100) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

// Trading control functions
async function setTradingMode(mode) {
    try {
        const response = await fetch('/api/trading/mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mode: mode })
        });
        
        const result = await response.json();
        if (result.success) {
            addLog(`Trading mode changed to ${mode}`, 'success');
        } else {
            addLog(`Failed to change trading mode: ${result.detail}`, 'error');
        }
    } catch (error) {
        addLog(`Error changing trading mode: ${error}`, 'error');
    }
}

async function emergencyStop() {
    if (!confirm('Are you sure you want to activate EMERGENCY STOP?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/trading/emergency-stop', {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            addLog('EMERGENCY STOP ACTIVATED', 'error');
        } else {
            addLog(`Failed to activate emergency stop: ${result.detail}`, 'error');
        }
    } catch (error) {
        addLog(`Error activating emergency stop: ${error}`, 'error');
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatPercent(value) {
    return (value * 100).toFixed(1) + '%';
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();
    addLog('Dashboard initialized', 'info');
});

// Export functions for use by other modules
window.MinhOSBase = {
    connectWebSocket,
    updateDashboard,
    updateConnectionStatus,
    addLog,
    setTradingMode,
    emergencyStop,
    formatCurrency,
    formatPercent,
    formatTime
};