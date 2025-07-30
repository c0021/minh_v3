// Enhanced Dashboard JavaScript Functions (<500 lines)

// Enhanced Dashboard API Functions
class EnhancedDashboard {
    constructor() {
        this.updateIntervals = new Map();
        this.isInitialized = false;
    }

    async initialize() {
        if (this.isInitialized) return;
        
        console.log('Initializing Enhanced Dashboard...');
        
        // Start all update intervals
        this.startUpdateIntervals();
        
        // Initialize slider controls
        this.initializeControls();
        
        this.isInitialized = true;
        console.log('Enhanced Dashboard initialized successfully');
    }

    startUpdateIntervals() {
        // Update autonomous section every 3 seconds
        this.updateIntervals.set('autonomous', 
            setInterval(() => this.updateAutonomousSection(), 3000));
        
        // Update pattern learning every 5 seconds
        this.updateIntervals.set('patterns', 
            setInterval(() => this.updatePatternLearning(), 5000));
        
        // Update historical data every 30 seconds
        this.updateIntervals.set('historical', 
            setInterval(() => this.updateHistoricalData(), 30000));
        
        // Update risk controls every 2 seconds
        this.updateIntervals.set('risk', 
            setInterval(() => this.updateRiskControls(), 2000));
    }

    stopUpdateIntervals() {
        for (let [name, interval] of this.updateIntervals) {
            clearInterval(interval);
            console.log(`Stopped ${name} update interval`);
        }
        this.updateIntervals.clear();
    }

    initializeControls() {
        // Confidence threshold slider
        const thresholdSlider = document.getElementById('confidence-threshold');
        const thresholdValue = document.getElementById('threshold-value');
        
        if (thresholdSlider && thresholdValue) {
            thresholdSlider.addEventListener('input', (e) => {
                thresholdValue.textContent = e.target.value;
            });
        }

        // Risk parameter sliders
        this.initializeRiskSliders();
    }

    initializeRiskSliders() {
        const sliders = [
            { id: 'daily-loss-limit', valueId: 'loss-limit-value', suffix: '%' },
            { id: 'max-position-size', valueId: 'position-size-value', suffix: ' contracts' },
            { id: 'volatility-threshold', valueId: 'volatility-value', suffix: '%' }
        ];

        sliders.forEach(slider => {
            const element = document.getElementById(slider.id);
            const valueElement = document.getElementById(slider.valueId);
            
            if (element && valueElement) {
                element.addEventListener('input', (e) => {
                    valueElement.textContent = e.target.value;
                });
            }
        });
    }

    // Autonomous Trading Section Updates
    async updateAutonomousSection() {
        try {
            const response = await fetch('/api/enhanced/autonomous/status');
            const data = await response.json();

            // Update status cards
            this.updateElement('autonomous-status', data.autonomous_enabled ? 'ACTIVE' : 'PAUSED');
            this.updateElement('todays-executions', data.executions_today);
            this.updateElement('current-ai-confidence', `${Math.round(data.current_confidence * 100)}%`);
            this.updateElement('ai-success-rate', `${Math.round(data.success_rate * 100)}%`);

            // Update confidence status
            const confidenceStatus = data.current_confidence >= 0.75 ? 'High Confidence' : 'Analyzing';
            this.updateElement('confidence-status', confidenceStatus);

            // Update AI decision stream
            this.updateAIDecisionStream(data.recent_decisions);

        } catch (error) {
            console.error('Error updating autonomous section:', error);
        }
    }

    updateAIDecisionStream(decisions) {
        const stream = document.getElementById('ai-decision-stream');
        if (!stream || !decisions) return;

        // Add new decisions
        decisions.forEach(decision => {
            const thoughtDiv = document.createElement('div');
            thoughtDiv.className = 'ai-thought';
            thoughtDiv.style.cssText = 'margin-bottom: 10px; padding: 8px; background: rgba(76, 175, 80, 0.1); border-left: 3px solid #4caf50; animation: fadeInUp 0.5s ease-out;';
            
            thoughtDiv.innerHTML = `
                <div style="color: #4caf50; font-weight: bold;">[${decision.type}] ${decision.title}</div>
                <div style="color: #e0e0e0;">${decision.message}</div>
            `;

            stream.appendChild(thoughtDiv);
            stream.scrollTop = stream.scrollHeight;

            // Keep only last 10 entries
            while (stream.children.length > 10) {
                stream.removeChild(stream.firstChild);
            }
        });
    }

    // Pattern Learning Section Updates
    async updatePatternLearning() {
        try {
            const response = await fetch('/api/enhanced/patterns/status');
            const data = await response.json();

            // Update pattern metrics
            this.updateElement('patterns-learned', data.patterns_learned);
            this.updateElement('pattern-success-rate', `${Math.round(data.success_rate * 100)}%`);
            this.updateElement('learning-speed', data.learning_speed);
            this.updateElement('current-regime', data.current_regime);

            // Update learning performance metrics
            this.updateElement('pattern-accuracy', `${Math.round(data.learning_metrics.pattern_accuracy * 100)}%`);
            this.updateElement('adaptation-speed', `${Math.round(data.learning_metrics.adaptation_speed * 100)}%`);
            this.updateElement('regime-accuracy', `${Math.round(data.learning_metrics.regime_accuracy * 100)}%`);

            // Update recent patterns
            this.updateRecentPatterns(data.recent_patterns);

        } catch (error) {
            console.error('Error updating pattern learning:', error);
        }
    }

    updateRecentPatterns(patterns) {
        const container = document.getElementById('recent-patterns');
        if (!container || !patterns) return;

        const html = patterns.map(pattern => `
            <div class="pattern-item" style="margin-bottom: 15px; padding: 10px; background: rgba(156, 39, 176, 0.1); border-radius: 6px; border-left: 3px solid #9c27b0;">
                <div style="font-weight: bold; color: #e0e0e0;">${pattern.name}</div>
                <div style="font-size: 12px; color: #a0a0a0; margin: 5px 0;">Discovered: ${pattern.discovered} | Confidence: ${Math.round(pattern.confidence * 100)}%</div>
                <div style="font-size: 13px; color: #b0b0b0;">${pattern.description}</div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Historical Data Section Updates
    async updateHistoricalData() {
        try {
            const response = await fetch('/api/enhanced/historical-data/scope');
            const data = await response.json();

            // Update data metrics
            this.updateElement('historical-depth', data.historical_depth_years);
            this.updateElement('archive-size', `${data.archive_size_gb} GB`);

            // Update data sources
            this.updateDataSources(data.data_sources);

        } catch (error) {
            console.error('Error updating historical data:', error);
        }
    }

    updateDataSources(sources) {
        // Update latency if available
        const latencyElement = document.getElementById('feed-latency');
        const gapsElement = document.getElementById('gaps-filled');

        if (sources && sources.length > 0) {
            const liveFeed = sources.find(s => s.name === 'Live Market Feed');
            const gapFill = sources.find(s => s.name === 'Gap Fill Engine');

            if (latencyElement && liveFeed) {
                latencyElement.textContent = liveFeed.latency || '12ms';
            }

            if (gapsElement && gapFill) {
                gapsElement.textContent = gapFill.gaps_filled_today || '0';
            }
        }
    }

    // Risk Controls Section Updates
    async updateRiskControls() {
        try {
            const response = await fetch('/api/enhanced/risk/advanced-status');
            const data = await response.json();

            // Update risk status
            this.updateElement('circuit-breaker-status', data.circuit_breaker_status);
            this.updateElement('risk-budget-used', `${Math.round(data.risk_budget_used * 100)}%`);
            this.updateElement('current-position-size', data.position_size);
            this.updateElement('max-drawdown', `${Math.round(data.max_drawdown * 100)}%`);

            // Update risk metrics
            this.updateRiskMetrics(data.risk_metrics);

            // Update risk alerts
            this.updateRiskAlerts(data.active_alerts);

        } catch (error) {
            console.error('Error updating risk controls:', error);
        }
    }

    updateRiskMetrics(metrics) {
        if (!metrics) return;

        // Update portfolio heat
        this.updateElement('portfolio-heat', metrics.portfolio_heat);
        this.updateProgressBar('portfolio-heat-bar', metrics.portfolio_heat_value);

        // Update stress level
        this.updateElement('stress-level', metrics.stress_level);
        this.updateProgressBar('stress-level-bar', metrics.stress_level_value);

        // Update correlation risk
        this.updateElement('correlation-risk', metrics.correlation_risk);
        this.updateProgressBar('correlation-risk-bar', metrics.correlation_risk_value);
    }

    updateRiskAlerts(alerts) {
        const container = document.getElementById('risk-alerts-container');
        if (!container) return;

        if (!alerts || alerts.length === 0) {
            container.innerHTML = `
                <div style="font-size: 13px; color: #4caf50; text-align: center; padding: 10px;">
                    ✅ No active risk alerts
                </div>
            `;
        } else {
            const html = alerts.map(alert => `
                <div class="risk-alert" style="margin-bottom: 10px; padding: 10px; background: rgba(244, 67, 54, 0.2); border-radius: 4px; border-left: 3px solid #f44336;">
                    <div style="font-weight: bold; color: #f44336;">${alert.title}</div>
                    <div style="font-size: 12px; color: #e0e0e0; margin-top: 5px;">${alert.message}</div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }
    }

    // Utility Functions
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateProgressBar(id, percentage) {
        const bar = document.getElementById(id);
        if (bar) {
            bar.style.width = `${percentage * 100}%`;
            
            // Color coding
            if (percentage < 0.5) {
                bar.style.background = '#4caf50';
            } else if (percentage < 0.8) {
                bar.style.background = '#ff9800';
            } else {
                bar.style.background = '#f44336';
            }
        }
    }

    // Control Functions (called from dashboard)
    async pauseAutonomousTrading() {
        if (!confirm('Pause autonomous trading? Manual mode will be activated.')) {
            return;
        }

        try {
            const response = await fetch('/api/enhanced/autonomous/pause', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.MinhOSBase.addLog('Autonomous trading paused', 'warning');
                this.updateElement('autonomous-status', 'PAUSED');
            }
        } catch (error) {
            console.error('Error pausing autonomous trading:', error);
            window.MinhOSBase.addLog('Failed to pause autonomous trading', 'error');
        }
    }

    async triggerEmergencyStop() {
        if (!confirm('EMERGENCY STOP - This will halt all trading immediately. Continue?')) {
            return;
        }

        try {
            const response = await fetch('/api/enhanced/risk/emergency-stop', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.MinhOSBase.addLog('EMERGENCY STOP ACTIVATED', 'error');
                this.updateElement('circuit-breaker-status', 'TRIGGERED');
            }
        } catch (error) {
            console.error('Error triggering emergency stop:', error);
            window.MinhOSBase.addLog('Failed to trigger emergency stop', 'error');
        }
    }

    async runRiskStressTest() {
        window.MinhOSBase.addLog('Running risk stress test...', 'info');
        
        try {
            const response = await fetch('/api/enhanced/risk/stress-test', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.MinhOSBase.addLog('Risk stress test completed', 'success');
            }
        } catch (error) {
            console.error('Error running stress test:', error);
            window.MinhOSBase.addLog('Stress test failed', 'error');
        }
    }

    // Modal/new page functions
    viewPatternLibrary() {
        window.open('/pattern-library', '_blank');
    }

    viewAILog() {
        window.open('/ai-log', '_blank');
    }

    viewRiskReport() {
        window.open('/risk-report', '_blank');
    }
}

// Global enhanced dashboard instance
window.EnhancedDashboard = new EnhancedDashboard();

// Enhanced dashboard functions for global access
window.pauseAutonomousTrading = () => window.EnhancedDashboard.pauseAutonomousTrading();
window.triggerEmergencyStop = () => window.EnhancedDashboard.triggerEmergencyStop();
window.runRiskStressTest = () => window.EnhancedDashboard.runRiskStressTest();
window.viewPatternLibrary = () => window.EnhancedDashboard.viewPatternLibrary();
window.viewAILog = () => window.EnhancedDashboard.viewAILog();
window.viewRiskReport = () => window.EnhancedDashboard.viewRiskReport();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.EnhancedDashboard.initialize();
    }, 1000); // Wait for base dashboard to load
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    window.EnhancedDashboard.stopUpdateIntervals();
});