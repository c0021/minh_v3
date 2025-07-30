// Risk Validation Dashboard JavaScript

class RiskValidationDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.data = {
            calibration: null,
            backtest: null,
            scenarios: null,
            config: null,
            performance: null
        };
        
        this.init();
    }
    
    init() {
        console.log('🛡️ Initializing Risk Validation Dashboard...');
        
        // Load initial data
        this.loadAllData();
        
        // Start real-time updates
        this.startUpdates();
        
        // Initialize charts
        this.initializeCharts();
        
        console.log('✅ Risk Validation Dashboard initialized');
    }
    
    async loadAllData() {
        try {
            // Load all data in parallel
            const [calibration, backtest, scenarios, config, performance] = await Promise.all([
                this.fetchKellyCalibration(),
                this.fetchBacktestComparison(),
                this.fetchRiskScenarios(),
                this.fetchCurrentConfig(),
                this.fetchPerformanceMetrics()
            ]);
            
            this.data.calibration = calibration;
            this.data.backtest = backtest;
            this.data.scenarios = scenarios;
            this.data.config = config;
            this.data.performance = performance;
            
            // Update all UI components
            this.updateCalibrationResults();
            this.updateBacktestComparison();
            this.updateRiskScenarios();
            this.updateCurrentConfig();
            this.updatePerformanceMetrics();
            this.updateSystemHealth();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async fetchKellyCalibration() {
        const response = await fetch('/api/risk-validation/kelly-calibration');
        if (!response.ok) throw new Error('Failed to fetch Kelly calibration');
        return await response.json();
    }
    
    async fetchBacktestComparison() {
        const response = await fetch('/api/risk-validation/backtest-comparison');
        if (!response.ok) throw new Error('Failed to fetch backtest comparison');
        return await response.json();
    }
    
    async fetchRiskScenarios() {
        const response = await fetch('/api/risk-validation/risk-scenarios');
        if (!response.ok) throw new Error('Failed to fetch risk scenarios');
        return await response.json();
    }
    
    async fetchCurrentConfig() {
        const response = await fetch('/api/risk-validation/current-parameters');
        if (!response.ok) throw new Error('Failed to fetch current config');
        return await response.json();
    }
    
    async fetchPerformanceMetrics() {
        const response = await fetch('/api/risk-validation/performance-metrics');
        if (!response.ok) throw new Error('Failed to fetch performance metrics');
        return await response.json();
    }
    
    initializeCharts() {
        this.initKellyCalibrationChart();
        this.initBacktestChart();
    }
    
    initKellyCalibrationChart() {
        const ctx = document.getElementById('kellyCalibrationChart');
        if (!ctx || !this.data.calibration) return;
        
        const data = this.data.calibration.calibration_results || [];
        
        this.charts.calibration = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => `${d.kelly_multiplier}x`),
                datasets: [
                    {
                        label: 'Annual Return (%)',
                        data: data.map(d => d.annual_return),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        yAxisID: 'y'
                    },
                    {
                        label: 'Max Drawdown (%)',
                        data: data.map(d => d.max_drawdown),
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        yAxisID: 'y'
                    },
                    {
                        label: 'Sharpe Ratio',
                        data: data.map(d => d.sharpe_ratio),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Kelly Multiplier Performance Comparison'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Return / Drawdown (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Sharpe Ratio'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }
    
    initBacktestChart() {
        const ctx = document.getElementById('backtestChart');
        if (!ctx || !this.data.backtest) return;
        
        const data = this.data.backtest.backtest_results || [];
        
        this.charts.backtest = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.strategy_name),
                datasets: [
                    {
                        label: 'Annual Return (%)',
                        data: data.map(d => d.annual_return),
                        backgroundColor: ['#28a745', '#6c757d'],
                        borderColor: ['#155724', '#495057'],
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Strategy Performance Comparison'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Annual Return (%)'
                        }
                    }
                }
            }
        });
    }
    
    updateCalibrationResults() {
        if (!this.data.calibration) return;
        
        const data = this.data.calibration;
        
        // Update optimal configuration display
        document.getElementById('optimal-multiplier').textContent = `${data.optimal_multiplier}x`;
        document.getElementById('optimal-return').textContent = `${data.summary?.best_return || 0}%`;
        document.getElementById('optimal-drawdown').textContent = `${data.summary?.best_drawdown || 0}%`;
        
        // Update status
        document.getElementById('calibration-status').textContent = data.status.toUpperCase();
        document.getElementById('calibration-status').className = `status-badge ${data.status === 'completed' ? 'success' : 'active'}`;
    }
    
    updateBacktestComparison() {
        if (!this.data.backtest) return;
        
        const data = this.data.backtest;
        const tbody = document.getElementById('strategy-rows');
        
        tbody.innerHTML = '';
        
        data.backtest_results?.forEach(strategy => {
            const row = document.createElement('tr');
            
            // Add highlighting for winner
            if (strategy.strategy_name === data.conclusion?.winner) {
                row.style.backgroundColor = '#d4edda';
            }
            
            row.innerHTML = `
                <td><strong>${strategy.strategy_name}</strong></td>
                <td>${strategy.annual_return.toFixed(1)}%</td>
                <td>${strategy.max_drawdown.toFixed(1)}%</td>
                <td>${strategy.sharpe_ratio.toFixed(2)}</td>
                <td><span class="status-badge ${strategy.performance_rating.toLowerCase()}">${strategy.performance_rating}</span></td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    updateRiskScenarios() {
        if (!this.data.scenarios) return;
        
        const data = this.data.scenarios;
        const container = document.getElementById('scenario-grid');
        
        container.innerHTML = '';
        
        data.risk_scenarios?.forEach(scenario => {
            const card = document.createElement('div');
            card.className = `scenario-card ${scenario.risk_level.toLowerCase()}-risk`;
            
            card.innerHTML = `
                <div class="scenario-name">${scenario.name}</div>
                <div class="scenario-description">${scenario.description}</div>
                <div class="scenario-metrics">
                    <div class="scenario-metric">
                        <span>Return:</span>
                        <span>${scenario.kelly_performance.return}%</span>
                    </div>
                    <div class="scenario-metric">
                        <span>Drawdown:</span>
                        <span>${scenario.kelly_performance.max_drawdown}%</span>
                    </div>
                    <div class="scenario-metric">
                        <span>Status:</span>
                        <span>${scenario.kelly_performance.status}</span>
                    </div>
                </div>
            `;
            
            container.appendChild(card);
        });
        
        // Update stress test summary
        const summary = data.stress_test_summary;
        if (summary) {
            document.getElementById('worst-drawdown').textContent = `${summary.worst_case_drawdown}%`;
            document.getElementById('scenarios-passed').textContent = `${summary.scenarios_passed}/${data.risk_scenarios?.length || 4}`;
            document.getElementById('overall-resilience').textContent = summary.overall_resilience;
        }
        
        // Update stress status badge
        const passedCount = summary?.scenarios_passed || 3;
        const totalCount = data.risk_scenarios?.length || 4;
        document.getElementById('stress-status').textContent = `${passedCount}/${totalCount} PASSED`;
        document.getElementById('stress-status').className = `status-badge ${passedCount === totalCount ? 'success' : passedCount >= totalCount * 0.75 ? 'good' : 'critical'}`;
    }
    
    updateCurrentConfig() {
        if (!this.data.config) return;
        
        const data = this.data.config;
        
        // Update Kelly configuration
        const kellyContainer = document.getElementById('kelly-config');
        kellyContainer.innerHTML = '';
        
        const kellyConfig = data.kelly_configuration || {};
        Object.entries(kellyConfig).forEach(([key, value]) => {
            const item = document.createElement('div');
            item.className = 'config-item';
            item.innerHTML = `
                <span class="config-label">${this.formatLabel(key)}:</span>
                <span class="config-value">${this.formatValue(value)}</span>
            `;
            kellyContainer.appendChild(item);
        });
        
        // Update risk configuration
        const riskContainer = document.getElementById('risk-config');
        riskContainer.innerHTML = '';
        
        const riskParams = data.risk_parameters || {};
        const importantParams = ['max_position_size', 'max_daily_loss', 'position_size_percent', 'enabled'];
        
        importantParams.forEach(key => {
            if (riskParams.hasOwnProperty(key)) {
                const item = document.createElement('div');
                item.className = 'config-item';
                item.innerHTML = `
                    <span class="config-label">${this.formatLabel(key)}:</span>
                    <span class="config-value">${this.formatValue(riskParams[key])}</span>
                `;
                riskContainer.appendChild(item);
            }
        });
    }
    
    updatePerformanceMetrics() {
        if (!this.data.performance) return;
        
        const data = this.data.performance.performance_metrics || {};
        
        // Update P&L metrics
        const pnl = data.current_pnl || {};
        document.getElementById('total-pnl').textContent = this.formatCurrency(pnl.total || 0);
        document.getElementById('today-pnl').textContent = this.formatCurrency(pnl.today || 0);
        document.getElementById('unrealized-pnl').textContent = this.formatCurrency(pnl.unrealized || 0);
        
        // Update Kelly performance metrics
        const kelly = data.kelly_performance || {};
        document.getElementById('avg-kelly').textContent = (kelly.avg_kelly_fraction || 0.125).toFixed(3);
        document.getElementById('avg-confidence').textContent = `${Math.round((kelly.avg_confidence || 0.72) * 100)}%`;
        document.getElementById('recs-today').textContent = kelly.recommendations_today || 0;
    }
    
    updateSystemHealth() {
        if (!this.data.performance) return;
        
        const health = this.data.performance.performance_metrics?.system_health || {};
        
        // Update health indicators
        document.getElementById('risk-violations').textContent = health.risk_violations || 0;
        document.getElementById('ml-status').textContent = health.ml_model_status || 'ACTIVE';
        document.getElementById('data-quality').textContent = health.data_quality || 'GOOD';
        document.getElementById('emergency-stops').textContent = health.emergency_stops || 0;
        
        // Update indicator colors
        this.updateIndicator('risk-violations-indicator', health.risk_violations || 0);
        this.updateIndicator('ml-status-indicator', health.ml_model_status === 'ACTIVE');
        this.updateIndicator('data-quality-indicator', health.data_quality === 'GOOD');
        this.updateIndicator('emergency-stops-indicator', (health.emergency_stops || 0) === 0);
        
        // Update overall health status
        const violations = health.risk_violations || 0;
        const emergencyStops = health.emergency_stops || 0;
        const mlActive = health.ml_model_status === 'ACTIVE';
        const dataGood = health.data_quality === 'GOOD';
        
        let healthStatus = 'HEALTHY';
        let healthClass = 'success';
        
        if (violations > 0 || emergencyStops > 0) {
            healthStatus = 'WARNING';
            healthClass = 'critical';
        } else if (!mlActive || !dataGood) {
            healthStatus = 'DEGRADED';
            healthClass = 'good';
        }
        
        const healthBadge = document.getElementById('health-status');
        healthBadge.textContent = healthStatus;
        healthBadge.className = `status-badge ${healthClass}`;
    }
    
    updateIndicator(id, condition) {
        const indicator = document.getElementById(id);
        if (!indicator) return;
        
        indicator.className = 'indicator';
        if (typeof condition === 'boolean') {
            if (!condition) indicator.classList.add('danger');
        } else if (typeof condition === 'number') {
            if (condition > 0) indicator.classList.add('danger');
        }
    }
    
    formatLabel(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatValue(value) {
        if (typeof value === 'boolean') {
            return value ? 'Enabled' : 'Disabled';
        }
        if (typeof value === 'number') {
            if (value < 1 && value > 0) {
                return value.toFixed(3);
            }
            return value.toString();
        }
        return value;
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }
    
    startUpdates() {
        // Update every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadAllData();
            document.getElementById('last-updated').textContent = 
                `Last Updated: ${new Date().toLocaleTimeString()}`;
        }, 30000);
        
        // Initial timestamp
        document.getElementById('last-updated').textContent = 
            `Last Updated: ${new Date().toLocaleTimeString()}`;
    }
    
    showError(message) {
        console.error('Dashboard Error:', message);
        // You could implement a toast notification here
    }
    
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Global functions
function refreshConfig() {
    if (window.dashboard) {
        window.dashboard.loadAllData();
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new RiskValidationDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});