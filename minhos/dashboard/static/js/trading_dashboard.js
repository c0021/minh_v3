// MinhOS Trading Dashboard Components
// ===================================
// Handles trading configuration, performance metrics, and trade history

class TradingDashboard {
    constructor() {
        this.config = null;
        this.performance = null;
        this.positions = [];
        this.tradeHistory = [];
        this.updateInterval = null;
    }

    async init() {
        await this.loadTradingConfig();
        await this.loadPerformance();
        await this.loadPositions();
        this.renderTradingPanel();
        this.startAutoUpdate();
    }

    async loadTradingConfig() {
        try {
            const response = await fetch('/api/trading/config');
            this.config = await response.json();
        } catch (error) {
            console.error('Failed to load trading config:', error);
            this.config = {
                auto_trade_enabled: false,
                trading_enabled: false,
                confidence_threshold: 75,
                max_position_size: 1,
                daily_loss_limit: 1000,
                risk_per_trade: 2
            };
        }
    }

    async loadPerformance() {
        try {
            const response = await fetch('/api/trading/performance');
            this.performance = await response.json();
        } catch (error) {
            console.error('Failed to load performance:', error);
            this.performance = {
                total_trades: 0,
                win_rate: 0,
                total_pnl: 0,
                sharpe_ratio: 0
            };
        }
    }

    async loadPositions() {
        try {
            const response = await fetch('/api/trading/positions');
            this.positions = await response.json();
        } catch (error) {
            console.error('Failed to load positions:', error);
            this.positions = [];
        }
    }

    renderTradingPanel() {
        // Create trading control panel HTML
        const tradingPanelHTML = `
            <div class="trading-panel card">
                <div class="card-header">
                    <h3>⚙️ Trading Configuration</h3>
                </div>
                <div class="card-body">
                    <div class="trading-toggles">
                        <div class="toggle-item">
                            <label class="switch">
                                <input type="checkbox" id="auto-trade-toggle" 
                                       ${this.config.auto_trade_enabled ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                            <span class="toggle-label">Autonomous Trading</span>
                            <span class="toggle-status ${this.config.auto_trade_enabled ? 'active' : 'inactive'}">
                                ${this.config.auto_trade_enabled ? 'ACTIVE' : 'INACTIVE'}
                            </span>
                        </div>
                        <div class="toggle-item">
                            <label class="switch">
                                <input type="checkbox" id="trading-enabled-toggle" 
                                       ${this.config.trading_enabled ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                            <span class="toggle-label">Manual Trading</span>
                            <span class="toggle-status ${this.config.trading_enabled ? 'active' : 'inactive'}">
                                ${this.config.trading_enabled ? 'ACTIVE' : 'INACTIVE'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="config-params">
                        <div class="param-row">
                            <label>AI Confidence Threshold:</label>
                            <input type="number" id="confidence-threshold" 
                                   value="${this.config.confidence_threshold}" min="50" max="100" step="5">
                            <span>%</span>
                        </div>
                        <div class="param-row">
                            <label>Max Position Size:</label>
                            <input type="number" id="max-position-size" 
                                   value="${this.config.max_position_size}" min="1" max="10">
                            <span>contracts</span>
                        </div>
                        <div class="param-row">
                            <label>Daily Loss Limit:</label>
                            <input type="number" id="daily-loss-limit" 
                                   value="${this.config.daily_loss_limit}" min="100" step="100">
                            <span>$</span>
                        </div>
                        <div class="param-row">
                            <label>Risk Per Trade:</label>
                            <input type="number" id="risk-per-trade" 
                                   value="${this.config.risk_per_trade}" min="0.5" max="5" step="0.5">
                            <span>%</span>
                        </div>
                    </div>
                    
                    <div class="config-actions">
                        <button class="btn-save" onclick="tradingDashboard.saveConfig()">
                            💾 Save Configuration
                        </button>
                        <button class="btn-emergency" onclick="tradingDashboard.emergencyStop()">
                            🚨 EMERGENCY STOP
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Create performance metrics HTML
        const performanceHTML = `
            <div class="performance-panel card">
                <div class="card-header">
                    <h3>📊 Trading Performance</h3>
                </div>
                <div class="card-body">
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-label">Total Trades</div>
                            <div class="metric-value">${this.performance.total_trades}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Win Rate</div>
                            <div class="metric-value">${(this.performance.win_rate * 100).toFixed(1)}%</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Total P&L</div>
                            <div class="metric-value ${this.performance.total_pnl >= 0 ? 'positive' : 'negative'}">
                                $${this.performance.total_pnl.toFixed(2)}
                            </div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Sharpe Ratio</div>
                            <div class="metric-value">${this.performance.sharpe_ratio.toFixed(2)}</div>
                        </div>
                    </div>
                    
                    <div class="performance-details">
                        <div class="detail-row">
                            <span>Winning Trades:</span>
                            <span>${this.performance.winning_trades}</span>
                        </div>
                        <div class="detail-row">
                            <span>Losing Trades:</span>
                            <span>${this.performance.losing_trades}</span>
                        </div>
                        <div class="detail-row">
                            <span>Average Win:</span>
                            <span class="positive">$${this.performance.average_win.toFixed(2)}</span>
                        </div>
                        <div class="detail-row">
                            <span>Average Loss:</span>
                            <span class="negative">$${Math.abs(this.performance.average_loss).toFixed(2)}</span>
                        </div>
                        <div class="detail-row">
                            <span>Max Drawdown:</span>
                            <span class="negative">${(this.performance.max_drawdown * 100).toFixed(1)}%</span>
                        </div>
                        <div class="detail-row">
                            <span>Current Streak:</span>
                            <span class="${this.performance.current_streak >= 0 ? 'positive' : 'negative'}">
                                ${Math.abs(this.performance.current_streak)} ${this.performance.current_streak >= 0 ? 'wins' : 'losses'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Create positions table HTML
        const positionsHTML = `
            <div class="positions-panel card">
                <div class="card-header">
                    <h3>📈 Open Positions</h3>
                </div>
                <div class="card-body">
                    ${this.positions.length > 0 ? `
                        <table class="positions-table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Qty</th>
                                    <th>Entry</th>
                                    <th>Current</th>
                                    <th>P&L</th>
                                    <th>Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${this.positions.map(pos => `
                                    <tr>
                                        <td>${pos.symbol}</td>
                                        <td class="${pos.side.toLowerCase()}">${pos.side}</td>
                                        <td>${pos.quantity}</td>
                                        <td>$${pos.entry_price.toFixed(2)}</td>
                                        <td>$${pos.current_price.toFixed(2)}</td>
                                        <td class="${pos.unrealized_pnl >= 0 ? 'positive' : 'negative'}">
                                            $${pos.unrealized_pnl.toFixed(2)}
                                        </td>
                                        <td>${this.formatTime(pos.entry_time)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    ` : '<p class="no-data">No open positions</p>'}
                </div>
            </div>
        `;

        // Find or create container for trading dashboard
        let container = document.getElementById('trading-dashboard-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'trading-dashboard-container';
            container.className = 'trading-dashboard-section';
            
            // Insert after the main dashboard sections
            const mainContent = document.querySelector('.dashboard-container');
            if (mainContent) {
                mainContent.appendChild(container);
            }
        }

        container.innerHTML = tradingPanelHTML + performanceHTML + positionsHTML;

        // Attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Auto-trade toggle
        const autoTradeToggle = document.getElementById('auto-trade-toggle');
        if (autoTradeToggle) {
            autoTradeToggle.addEventListener('change', (e) => {
                this.config.auto_trade_enabled = e.target.checked;
                this.updateToggleStatus(e.target);
            });
        }

        // Trading enabled toggle
        const tradingToggle = document.getElementById('trading-enabled-toggle');
        if (tradingToggle) {
            tradingToggle.addEventListener('change', (e) => {
                this.config.trading_enabled = e.target.checked;
                this.updateToggleStatus(e.target);
            });
        }
    }

    updateToggleStatus(toggle) {
        const statusElement = toggle.parentElement.parentElement.querySelector('.toggle-status');
        if (toggle.checked) {
            statusElement.textContent = 'ACTIVE';
            statusElement.classList.remove('inactive');
            statusElement.classList.add('active');
        } else {
            statusElement.textContent = 'INACTIVE';
            statusElement.classList.remove('active');
            statusElement.classList.add('inactive');
        }
    }

    async saveConfig() {
        // Gather all config values
        this.config.confidence_threshold = parseFloat(document.getElementById('confidence-threshold').value);
        this.config.max_position_size = parseInt(document.getElementById('max-position-size').value);
        this.config.daily_loss_limit = parseFloat(document.getElementById('daily-loss-limit').value);
        this.config.risk_per_trade = parseFloat(document.getElementById('risk-per-trade').value);

        try {
            const response = await fetch('/api/trading/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.config)
            });

            if (response.ok) {
                this.showNotification('Configuration saved successfully', 'success');
            } else {
                throw new Error('Failed to save configuration');
            }
        } catch (error) {
            console.error('Error saving config:', error);
            this.showNotification('Failed to save configuration', 'error');
        }
    }

    async emergencyStop() {
        if (!confirm('⚠️ EMERGENCY STOP will close all positions and disable trading. Continue?')) {
            return;
        }

        try {
            const response = await fetch('/api/trading/emergency-stop', {
                method: 'POST'
            });

            if (response.ok) {
                this.showNotification('🚨 EMERGENCY STOP ACTIVATED', 'error');
                // Reload config to show disabled state
                await this.loadTradingConfig();
                this.renderTradingPanel();
            }
        } catch (error) {
            console.error('Error triggering emergency stop:', error);
            this.showNotification('Failed to trigger emergency stop', 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }

    startAutoUpdate() {
        // Update every 5 seconds
        this.updateInterval = setInterval(async () => {
            await this.loadPerformance();
            await this.loadPositions();
            this.renderTradingPanel();
        }, 5000);
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize on page load
let tradingDashboard;
document.addEventListener('DOMContentLoaded', () => {
    tradingDashboard = new TradingDashboard();
    tradingDashboard.init();
});