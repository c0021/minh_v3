/**
 * ML Performance Dashboard JavaScript
 * 
 * Handles real-time monitoring of ML model performance, accuracy tracking,
 * and system health visualization.
 */

class MLPerformanceDashboard {
    constructor() {
        this.updateInterval = 10000; // 10 seconds
        this.chartData = {
            accuracy: [],
            latency: [],
            predictions: []
        };
        this.charts = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startAutoRefresh();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('ml-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAllData());
        }
        
        // Time range selector
        const timeRangeSelect = document.getElementById('ml-time-range');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.loadPerformanceHistory(parseInt(e.target.value));
            });
        }
        
        // Model toggle switches
        document.querySelectorAll('.model-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.toggleModelDisplay(e.target.dataset.model, e.target.checked);
            });
        });
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.updateSystemStatus(),
                this.updateCurrentPerformance(),
                this.updateModelAccuracy(),
                this.updateRecentPredictions()
            ]);
        } catch (error) {
            console.error('Error loading initial ML dashboard data:', error);
            this.showError('Failed to load ML performance data');
        }
    }
    
    async updateSystemStatus() {
        try {
            const response = await fetch('/api/ml/status');
            const data = await response.json();
            
            this.renderSystemStatus(data);
        } catch (error) {
            console.error('Error updating ML system status:', error);
        }
    }
    
    async updateCurrentPerformance() {
        try {
            const response = await fetch('/api/ml/performance/current');
            const data = await response.json();
            
            this.renderCurrentPerformance(data);
        } catch (error) {
            console.error('Error updating current ML performance:', error);
        }
    }
    
    async updateModelAccuracy() {
        try {
            const response = await fetch('/api/ml/models/accuracy');
            const data = await response.json();
            
            this.renderModelAccuracy(data);
        } catch (error) {
            console.error('Error updating model accuracy:', error);
        }
    }
    
    async updateRecentPredictions() {
        try {
            const response = await fetch('/api/ml/predictions/recent?limit=20');
            const data = await response.json();
            
            this.renderRecentPredictions(data);
        } catch (error) {
            console.error('Error updating recent predictions:', error);
        }
    }
    
    async loadPerformanceHistory(hours = 24) {
        try {
            const response = await fetch(`/api/ml/performance/history?hours=${hours}`);
            const data = await response.json();
            
            this.renderPerformanceHistory(data);
        } catch (error) {
            console.error('Error loading performance history:', error);
        }
    }
    
    renderSystemStatus(data) {
        const container = document.getElementById('ml-system-status');
        if (!container) return;
        
        const healthColor = this.getHealthColor(data.system_health);
        const healthIcon = this.getHealthIcon(data.system_health);
        
        container.innerHTML = `
            <div class="ml-status-grid">
                <div class="status-card overall-health" style="border-left: 4px solid ${healthColor}">
                    <div class="status-header">
                        <h3>${healthIcon} System Health</h3>
                        <span class="health-badge ${data.system_health}">${data.system_health.toUpperCase()}</span>
                    </div>
                    <div class="status-metrics">
                        <div class="metric">
                            <span class="label">Total Predictions:</span>
                            <span class="value">${data.total_predictions.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Avg Confidence:</span>
                            <span class="value">${(data.avg_confidence * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="status-card">
                    <h4>🧠 LSTM Neural Network</h4>
                    <div class="component-status ${data.lstm_enabled ? 'enabled' : 'disabled'}">
                        <span class="status-indicator ${data.lstm_enabled ? 'green' : 'red'}"></span>
                        ${data.lstm_enabled ? 'Operational' : 'Disabled'}
                    </div>
                </div>
                
                <div class="status-card">
                    <h4>🎯 Ensemble Models</h4>
                    <div class="component-status ${data.ensemble_enabled ? 'enabled' : 'disabled'}">
                        <span class="status-indicator ${data.ensemble_enabled ? 'green' : 'red'}"></span>
                        ${data.ensemble_enabled ? 'Operational' : 'Disabled'}
                    </div>
                </div>
                
                <div class="status-card">
                    <h4>💰 Kelly Criterion</h4>
                    <div class="component-status ${data.kelly_enabled ? 'enabled' : 'disabled'}">
                        <span class="status-indicator ${data.kelly_enabled ? 'green' : 'red'}"></span>
                        ${data.kelly_enabled ? 'Operational' : 'Disabled'}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderCurrentPerformance(data) {
        const container = document.getElementById('ml-current-performance');
        if (!container) return;
        
        container.innerHTML = `
            <div class="performance-grid">
                ${this.renderLSTMPerformance(data.lstm)}
                ${this.renderEnsemblePerformance(data.ensemble)}
                ${this.renderKellyPerformance(data.kelly)}
            </div>
            
            <div class="system-metrics">
                <h4>System Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">${data.system_metrics.total_predictions}</span>
                        <span class="metric-label">Total Predictions</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">${data.system_metrics.avg_latency.toFixed(1)}ms</span>
                        <span class="metric-label">Avg Latency</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">${data.system_metrics.memory_usage.toFixed(1)}MB</span>
                        <span class="metric-label">Memory Usage</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderLSTMPerformance(lstm) {
        return `
            <div class="model-performance-card lstm">
                <div class="model-header">
                    <h4>🧠 LSTM Neural Network</h4>
                    <span class="status-badge ${lstm.enabled ? 'enabled' : 'disabled'}">
                        ${lstm.enabled ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="model-metrics">
                    <div class="metric-row">
                        <span>Trained:</span>
                        <span class="${lstm.trained ? 'green' : 'orange'}">${lstm.trained ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="metric-row">
                        <span>Predictions:</span>
                        <span>${lstm.predictions || 0}</span>
                    </div>
                    <div class="metric-row">
                        <span>Data Buffer:</span>
                        <span>${lstm.data_buffer_size || 0} points</span>
                    </div>
                    <div class="metric-row">
                        <span>Confidence Threshold:</span>
                        <span>${((lstm.confidence_threshold || 0.6) * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderEnsemblePerformance(ensemble) {
        const baseModels = ensemble.base_models || [];
        const modelWeights = ensemble.model_weights || {};
        
        return `
            <div class="model-performance-card ensemble">
                <div class="model-header">
                    <h4>🎯 Ensemble Models</h4>
                    <span class="status-badge ${ensemble.enabled ? 'enabled' : 'disabled'}">
                        ${ensemble.enabled ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="model-metrics">
                    <div class="metric-row">
                        <span>Trained:</span>
                        <span class="${ensemble.trained ? 'green' : 'orange'}">${ensemble.trained ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="metric-row">
                        <span>Predictions:</span>
                        <span>${ensemble.predictions || 0}</span>
                    </div>
                    <div class="metric-row">
                        <span>Base Models:</span>
                        <span>${baseModels.length} models</span>
                    </div>
                    <div class="metric-row">
                        <span>Features:</span>
                        <span>${ensemble.feature_count || 0}</span>
                    </div>
                </div>
                ${baseModels.length > 0 ? `
                    <div class="base-models">
                        <h5>Base Models:</h5>
                        ${baseModels.map(model => `
                            <div class="base-model">
                                <span>${model}</span>
                                <span>${((modelWeights[model] || 0) * 100).toFixed(1)}%</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    renderKellyPerformance(kelly) {
        return `
            <div class="model-performance-card kelly">
                <div class="model-header">
                    <h4>💰 Kelly Criterion</h4>
                    <span class="status-badge ${kelly.enabled ? 'enabled' : 'disabled'}">
                        ${kelly.enabled ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="model-metrics">
                    <div class="metric-row">
                        <span>System Ready:</span>
                        <span class="${kelly.system_ready ? 'green' : 'orange'}">${kelly.system_ready ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="metric-row">
                        <span>Position Calculations:</span>
                        <span>${kelly.total_predictions || 0}</span>
                    </div>
                    <div class="metric-row">
                        <span>Win Rate:</span>
                        <span class="${(kelly.win_rate || 0) > 0.5 ? 'green' : 'red'}">${((kelly.win_rate || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric-row">
                        <span>Total P&L:</span>
                        <span class="${(kelly.total_pnl || 0) >= 0 ? 'green' : 'red'}">$${(kelly.total_pnl || 0).toFixed(0)}</span>
                    </div>
                    <div class="metric-row">
                        <span>Drawdown:</span>
                        <span class="red">${((kelly.current_drawdown || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric-row">
                        <span>Kelly Multiplier:</span>
                        <span>${(kelly.kelly_multiplier || 1.0).toFixed(2)}x</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderRecentPredictions(data) {
        const container = document.getElementById('ml-recent-predictions');
        if (!container) return;
        
        const predictions = data.predictions || [];
        
        container.innerHTML = `
            <div class="predictions-header">
                <h4>Recent ML Predictions</h4>
                <div class="prediction-stats">
                    <span>Total: ${data.total_predictions}</span>
                    <span>ML Enhanced: ${data.ml_enhanced_count}/${data.total_predictions}</span>
                    <span>Avg Confidence: ${(data.avg_confidence * 100).toFixed(1)}%</span>
                </div>
            </div>
            
            <div class="predictions-table">
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Signal</th>
                            <th>Confidence</th>
                            <th>ML Enhanced</th>
                            <th>Kelly Position</th>
                            <th>Win Prob</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${predictions.slice(-10).reverse().map(pred => `
                            <tr class="prediction-row ${pred.ml_enhanced ? 'ml-enhanced' : ''}">
                                <td>${new Date(pred.timestamp).toLocaleTimeString()}</td>
                                <td>
                                    <span class="signal-badge ${pred.signal_type.toLowerCase()}">
                                        ${pred.signal_type}
                                    </span>
                                </td>
                                <td>
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" style="width: ${pred.confidence * 100}%"></div>
                                        <span>${(pred.confidence * 100).toFixed(1)}%</span>
                                    </div>
                                </td>
                                <td>
                                    ${pred.ml_enhanced ? 
                                        '<span class="ml-badge">🤖 ML</span>' : 
                                        '<span class="traditional-badge">📊 Traditional</span>'
                                    }
                                </td>
                                <td>${(pred.kelly_position * 100).toFixed(1)}%</td>
                                <td>${(pred.kelly_win_prob * 100).toFixed(1)}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    getHealthColor(health) {
        const colors = {
            'optimal': '#10b981',
            'good': '#22c55e',
            'limited': '#f59e0b',
            'disabled': '#ef4444',
            'critical': '#dc2626'
        };
        return colors[health] || '#6b7280';
    }
    
    getHealthIcon(health) {
        const icons = {
            'optimal': '✅',
            'good': '🟢',
            'limited': '🟡',
            'disabled': '🔴',
            'critical': '💥'
        };
        return icons[health] || '❓';
    }
    
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshAllData();
        }, this.updateInterval);
    }
    
    async refreshAllData() {
        try {
            await this.loadInitialData();
            this.updateLastRefreshTime();
        } catch (error) {
            console.error('Error refreshing ML dashboard:', error);
        }
    }
    
    updateLastRefreshTime() {
        const refreshTime = document.getElementById('ml-last-refresh');
        if (refreshTime) {
            refreshTime.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }
    
    showError(message) {
        // Show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
    
    destroy() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
    }
}

// Initialize ML Performance Dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ml-performance-dashboard')) {
        window.mlDashboard = new MLPerformanceDashboard();
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MLPerformanceDashboard;
}