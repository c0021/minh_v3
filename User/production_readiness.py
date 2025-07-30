#!/usr/bin/env python3
"""
MinhOS Production Readiness Checker
===================================
Comprehensive production readiness assessment for MinhOS trading system.
Checks documentation, error handling, logging, testing, security, performance, 
monitoring, and recovery mechanisms.

Usage:
    python tools/production_readiness.py [options]
"""

import os
import sys
import ast
import json
import re
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

# Add the parent directory to the path so we can import from the project
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("production_readiness")


class ProductionReadinessChecker:
    """Comprehensive production readiness assessment for MinhOS"""
    
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path).resolve()
        self.results = {}
        self.overall_score = 0
        self.critical_issues = []
        self.recommendations = []
        
        # Critical files and directories
        self.critical_files = {
            'config': 'config.yaml',
            'main_entry': 'minh.py',
            'requirements': 'requirements.txt',
            'setup': 'setup.py',
            'database_schema': 'database/schema.sql'
        }
        
        # Critical services
        self.critical_services = [
            'backend_study_enhanced.py',
            'risk_manager.py',
            'trading_copilot.py',
            'http_server.py',
            'websocket_server.py'
        ]
        
        # Score weights
        self.weights = {
            'documentation': 0.15,
            'error_handling': 0.20,
            'logging': 0.15,
            'testing': 0.15,
            'security': 0.10,
            'performance': 0.10,
            'monitoring': 0.10,
            'recovery': 0.05
        }
    
    def check_all(self) -> Dict[str, Any]:
        """Run all production readiness checks"""
        logger.info("Starting production readiness assessment...")
        
        self.results = {
            "assessment_date": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "checks": {
                "documentation": self.check_documentation_coverage(),
                "error_handling": self.check_error_handling(),
                "logging": self.check_logging_coverage(),
                "testing": self.check_test_coverage(),
                "security": self.check_security(),
                "performance": self.check_performance_requirements(),
                "monitoring": self.check_monitoring_coverage(),
                "recovery": self.check_recovery_mechanisms()
            },
            "overall_score": 0,
            "grade": "",
            "critical_issues": [],
            "recommendations": []
        }
        
        # Calculate overall score
        self.overall_score = self._calculate_overall_score()
        self.results["overall_score"] = self.overall_score
        self.results["grade"] = self._get_grade()
        self.results["critical_issues"] = self.critical_issues
        self.results["recommendations"] = self.recommendations
        
        return self.results
    
    def check_documentation_coverage(self) -> Dict[str, Any]:
        """Check documentation coverage across the codebase"""
        logger.info("Checking documentation coverage...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        # Check for README and documentation files
        doc_files = {
            'README.md': self.root_path / 'README.md',
            'API_DOCS': self.root_path / 'docs' / 'API.md',
            'SETUP_GUIDE': self.root_path / 'docs' / 'setup',
            'TRADING_GUIDE': self.root_path / 'docs' / 'trading'
        }
        
        doc_score = 0
        for doc_name, doc_path in doc_files.items():
            if doc_path.exists():
                if doc_path.is_file():
                    doc_score += 10
                    result['details'][doc_name] = 'Found'
                elif doc_path.is_dir() and any(doc_path.iterdir()):
                    doc_score += 10
                    result['details'][doc_name] = 'Found (directory)'
                else:
                    result['issues'].append(f"Missing: {doc_name}")
            else:
                result['issues'].append(f"Missing: {doc_name}")
        
        # Check function docstring coverage
        python_files = list(self.root_path.rglob("*.py"))
        if python_files:
            total_functions = 0
            documented_functions = 0
            
            for py_file in python_files:
                if self._should_analyze_file(py_file):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                total_functions += 1
                                if self._has_docstring(node):
                                    documented_functions += 1
                    except Exception as e:
                        logger.warning(f"Error analyzing {py_file}: {e}")
            
            if total_functions > 0:
                docstring_coverage = (documented_functions / total_functions) * 100
                doc_score += min(40, docstring_coverage * 0.4)  # Max 40 points
                result['details']['function_docstring_coverage'] = f"{docstring_coverage:.1f}%"
                
                if docstring_coverage < 50:
                    result['issues'].append(f"Low docstring coverage: {docstring_coverage:.1f}%")
        
        result['score'] = min(100, doc_score)
        
        if result['score'] < 70:
            self.critical_issues.append("Documentation coverage below 70%")
            self.recommendations.append("Use `python tools/add_documentation.py --priority` to improve documentation")
        
        return result
    
    def check_error_handling(self) -> Dict[str, Any]:
        """Check error handling and exception management"""
        logger.info("Checking error handling...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        # Check critical services for proper error handling
        error_score = 0
        services_checked = 0
        
        for service_file in self.critical_services:
            service_path = self.root_path / 'services' / service_file
            if service_path.exists():
                services_checked += 1
                error_handling_score = self._analyze_error_handling(service_path)
                error_score += error_handling_score
                result['details'][service_file] = f"{error_handling_score:.1f}%"
                
                if error_handling_score < 60:
                    result['issues'].append(f"Poor error handling in {service_file}")
        
        if services_checked > 0:
            result['score'] = error_score / services_checked
        
        # Check for global exception handlers
        main_file = self.root_path / 'minh.py'
        if main_file.exists():
            has_global_handler = self._has_global_exception_handler(main_file)
            if has_global_handler:
                result['score'] += 10
                result['details']['global_exception_handler'] = 'Found'
            else:
                result['issues'].append("No global exception handler in main entry point")
        
        result['score'] = min(100, result['score'])
        
        if result['score'] < 70:
            self.critical_issues.append("Insufficient error handling")
            self.recommendations.append("Add comprehensive try-catch blocks and error logging")
        
        return result
    
    def check_logging_coverage(self) -> Dict[str, Any]:
        """Check logging implementation and coverage"""
        logger.info("Checking logging coverage...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        # Check for logging configuration
        logging_score = 0
        
        # Check for logging imports and setup
        python_files = list(self.root_path.rglob("*.py"))
        files_with_logging = 0
        
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for logging imports
                    if 'import logging' in content or 'from logging import' in content:
                        files_with_logging += 1
                        
                        # Check for logger setup
                        if 'getLogger' in content:
                            logging_score += 1
                        
                        # Check for different log levels
                        log_levels = ['debug', 'info', 'warning', 'error', 'critical']
                        for level in log_levels:
                            if f'logger.{level}' in content.lower():
                                logging_score += 0.5
                                break
                
                except Exception as e:
                    logger.warning(f"Error analyzing {py_file}: {e}")
        
        if files_with_logging > 0:
            result['score'] = min(100, (files_with_logging / len(self.critical_services)) * 100)
            result['details']['files_with_logging'] = files_with_logging
            result['details']['logging_calls'] = int(logging_score)
        
        # Check for log files and rotation
        logs_dir = self.root_path / 'logs'
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            result['details']['log_files_found'] = len(log_files)
            if log_files:
                result['score'] += 10
        else:
            result['issues'].append("No logs directory found")
        
        if result['score'] < 60:
            self.critical_issues.append("Insufficient logging coverage")
            self.recommendations.append("Add comprehensive logging with appropriate levels")
        
        return result
    
    def check_test_coverage(self) -> Dict[str, Any]:
        """Check test coverage and quality"""
        logger.info("Checking test coverage...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        # Check for test directories and files
        test_dirs = ['tests', 'test']
        test_files = []
        
        for test_dir in test_dirs:
            test_path = self.root_path / test_dir
            if test_path.exists():
                test_files.extend(list(test_path.rglob("test_*.py")))
                test_files.extend(list(test_path.rglob("*_test.py")))
        
        # Also check for test files in the root
        test_files.extend(list(self.root_path.glob("test_*.py")))
        
        if test_files:
            result['score'] = min(50, len(test_files) * 10)  # Max 50 points for having tests
            result['details']['test_files_found'] = len(test_files)
            
            # Check test quality
            test_quality_score = 0
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for test frameworks
                    if 'import unittest' in content or 'import pytest' in content:
                        test_quality_score += 5
                    
                    # Check for assertions
                    if 'assert' in content:
                        test_quality_score += 5
                    
                    # Check for test methods
                    if 'def test_' in content:
                        test_quality_score += 10
                
                except Exception as e:
                    logger.warning(f"Error analyzing test file {test_file}: {e}")
            
            result['score'] += min(50, test_quality_score)
        else:
            result['issues'].append("No test files found")
            self.critical_issues.append("No automated tests found")
        
        # Check for integration tests
        integration_test_files = []
        for test_file in test_files:
            if 'integration' in test_file.name.lower():
                integration_test_files.append(test_file)
        
        if integration_test_files:
            result['details']['integration_tests'] = len(integration_test_files)
        else:
            result['issues'].append("No integration tests found")
        
        if result['score'] < 40:
            self.recommendations.append("Implement comprehensive test suite with unit and integration tests")
        
        return result
    
    def check_security(self) -> Dict[str, Any]:
        """Check security measures and practices"""
        logger.info("Checking security measures...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        security_score = 0
        
        # Check for sensitive data exposure
        python_files = list(self.root_path.rglob("*.py"))
        security_issues = []
        
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for hardcoded secrets
                    secret_patterns = [
                        r'password\s*=\s*["\'][^"\']+["\']',
                        r'api_key\s*=\s*["\'][^"\']+["\']',
                        r'secret\s*=\s*["\'][^"\']+["\']',
                        r'token\s*=\s*["\'][^"\']+["\']'
                    ]
                    
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            security_issues.append(f"Potential hardcoded secret in {py_file}")
                            break
                
                except Exception as e:
                    logger.warning(f"Error analyzing {py_file}: {e}")
        
        if not security_issues:
            security_score += 30
        else:
            result['issues'].extend(security_issues)
        
        # Check for input validation
        validation_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for validation patterns
                    if any(pattern in content for pattern in ['validate', 'sanitize', 'isinstance', 'type(']) :
                        validation_score += 1
                
                except Exception:
                    pass
        
        if validation_score > 0:
            security_score += min(30, validation_score * 5)
        
        # Check for HTTPS usage
        https_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for HTTPS usage
                    if 'https://' in content:
                        https_score += 10
                        break
                
                except Exception:
                    pass
        
        security_score += https_score
        
        # Check for environment variable usage
        env_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for environment variable usage
                    if 'os.environ' in content or 'getenv' in content:
                        env_score += 10
                        break
                
                except Exception:
                    pass
        
        security_score += env_score
        
        result['score'] = min(100, security_score)
        result['details']['security_issues_found'] = len(security_issues)
        
        if result['score'] < 70:
            self.critical_issues.append("Security measures insufficient")
            self.recommendations.append("Implement proper input validation and secure configuration management")
        
        return result
    
    def check_performance_requirements(self) -> Dict[str, Any]:
        """Check performance-related requirements"""
        logger.info("Checking performance requirements...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        performance_score = 0
        
        # Check for performance monitoring
        python_files = list(self.root_path.rglob("*.py"))
        
        # Check for timing/profiling code
        timing_files = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for timing imports and usage
                    if any(pattern in content for pattern in ['time.time()', 'datetime.now()', 'perf_counter']):
                        timing_files += 1
                
                except Exception:
                    pass
        
        if timing_files > 0:
            performance_score += 20
            result['details']['files_with_timing'] = timing_files
        
        # Check for database optimization
        db_files = list(self.root_path.rglob("*.db"))
        if db_files:
            performance_score += 10
            result['details']['database_files'] = len(db_files)
        
        # Check for caching mechanisms
        caching_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for caching patterns
                    if any(pattern in content for pattern in ['cache', 'lru_cache', 'memoize']):
                        caching_score += 10
                        break
                
                except Exception:
                    pass
        
        performance_score += caching_score
        
        # Check for async/await usage
        async_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for async patterns
                    if any(pattern in content for pattern in ['async def', 'await ', 'asyncio']):
                        async_score += 10
                        break
                
                except Exception:
                    pass
        
        performance_score += async_score
        
        # Check for resource monitoring
        if PSUTIL_AVAILABLE:
            performance_score += 20
            result['details']['psutil_available'] = True
        else:
            result['issues'].append("psutil not available for system monitoring")
        
        result['score'] = min(100, performance_score)
        
        if result['score'] < 60:
            self.recommendations.append("Implement performance monitoring and optimization")
        
        return result
    
    def check_monitoring_coverage(self) -> Dict[str, Any]:
        """Check monitoring and observability"""
        logger.info("Checking monitoring coverage...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        monitoring_score = 0
        
        # Check for health check endpoints
        python_files = list(self.root_path.rglob("*.py"))
        health_endpoints = 0
        
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for health check patterns
                    if any(pattern in content for pattern in ['/health', '/status', 'health_check']):
                        health_endpoints += 1
                
                except Exception:
                    pass
        
        if health_endpoints > 0:
            monitoring_score += 30
            result['details']['health_endpoints_found'] = health_endpoints
        else:
            result['issues'].append("No health check endpoints found")
        
        # Check for metrics collection
        metrics_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for metrics patterns
                    if any(pattern in content for pattern in ['metrics', 'prometheus', 'statsd']):
                        metrics_score += 20
                        break
                
                except Exception:
                    pass
        
        monitoring_score += metrics_score
        
        # Check for alerting
        alerting_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for alerting patterns
                    if any(pattern in content for pattern in ['alert', 'notification', 'email', 'webhook']):
                        alerting_score += 20
                        break
                
                except Exception:
                    pass
        
        monitoring_score += alerting_score
        
        # Check for dashboard/UI monitoring
        dashboard_files = list(self.root_path.rglob("dashboard*.py"))
        if dashboard_files:
            monitoring_score += 30
            result['details']['dashboard_files'] = len(dashboard_files)
        
        result['score'] = min(100, monitoring_score)
        
        if result['score'] < 50:
            self.recommendations.append("Implement comprehensive monitoring and alerting")
        
        return result
    
    def check_recovery_mechanisms(self) -> Dict[str, Any]:
        """Check recovery and resilience mechanisms"""
        logger.info("Checking recovery mechanisms...")
        
        result = {
            "score": 0,
            "max_score": 100,
            "details": {},
            "issues": []
        }
        
        recovery_score = 0
        
        # Check for backup mechanisms
        backup_files = list(self.root_path.rglob("*backup*"))
        if backup_files:
            recovery_score += 20
            result['details']['backup_files'] = len(backup_files)
        
        # Check for restart scripts
        restart_scripts = []
        for pattern in ['restart*', 'start*', 'stop*']:
            restart_scripts.extend(list(self.root_path.rglob(pattern)))
        
        if restart_scripts:
            recovery_score += 20
            result['details']['restart_scripts'] = len(restart_scripts)
        
        # Check for error recovery code
        python_files = list(self.root_path.rglob("*.py"))
        recovery_patterns = 0
        
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for recovery patterns
                    if any(pattern in content for pattern in ['retry', 'recover', 'fallback', 'circuit_breaker']):
                        recovery_patterns += 1
                
                except Exception:
                    pass
        
        if recovery_patterns > 0:
            recovery_score += 30
            result['details']['recovery_patterns'] = recovery_patterns
        
        # Check for graceful shutdown
        shutdown_score = 0
        for py_file in python_files:
            if self._should_analyze_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for graceful shutdown patterns
                    if any(pattern in content for pattern in ['signal.signal', 'atexit', 'KeyboardInterrupt']):
                        shutdown_score += 30
                        break
                
                except Exception:
                    pass
        
        recovery_score += shutdown_score
        
        result['score'] = min(100, recovery_score)
        
        if result['score'] < 40:
            self.recommendations.append("Implement robust recovery and restart mechanisms")
        
        return result
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed"""
        skip_patterns = ['__pycache__', '.git', 'test_', 'venv', 'env', '.venv', 'build', 'dist']
        return not any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _has_docstring(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has a docstring"""
        return (func_node.body and 
                isinstance(func_node.body[0], ast.Expr) and
                isinstance(func_node.body[0].value, ast.Constant) and
                isinstance(func_node.body[0].value.value, str))
    
    def _analyze_error_handling(self, file_path: Path) -> float:
        """Analyze error handling quality in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Count try-except blocks
            try_blocks = 0
            functions = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    try_blocks += 1
                elif isinstance(node, ast.FunctionDef):
                    functions += 1
            
            if functions == 0:
                return 0
            
            # Calculate error handling coverage
            coverage = (try_blocks / functions) * 100
            return min(100, coverage)
        
        except Exception as e:
            logger.warning(f"Error analyzing error handling in {file_path}: {e}")
            return 0
    
    def _has_global_exception_handler(self, file_path: Path) -> bool:
        """Check if file has global exception handler"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for global exception handling patterns
            patterns = [
                'except Exception',
                'except BaseException',
                'sys.excepthook',
                'except:',
                'except KeyboardInterrupt'
            ]
            
            return any(pattern in content for pattern in patterns)
        
        except Exception:
            return False
    
    def _calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        total_score = 0
        
        for check_name, weight in self.weights.items():
            if check_name in self.results["checks"]:
                check_score = self.results["checks"][check_name]["score"]
                total_score += check_score * weight
        
        return round(total_score, 1)
    
    def _get_grade(self) -> str:
        """Get letter grade based on overall score"""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_readiness_report(self) -> str:
        """Generate comprehensive readiness report"""
        report = []
        report.append("# MinhOS Production Readiness Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Overall assessment
        report.append(f"## Overall Assessment")
        report.append(f"**Score**: {self.overall_score}/100")
        report.append(f"**Grade**: {self._get_grade()}")
        report.append("")
        
        # Status determination
        if self.overall_score >= 80:
            status = "✅ READY FOR PRODUCTION"
            status_color = "green"
        elif self.overall_score >= 70:
            status = "⚠️ NEEDS MINOR IMPROVEMENTS"
            status_color = "yellow"
        elif self.overall_score >= 60:
            status = "❌ NEEDS MAJOR IMPROVEMENTS"
            status_color = "orange"
        else:
            status = "🚫 NOT READY FOR PRODUCTION"
            status_color = "red"
        
        report.append(f"**Status**: {status}")
        report.append("")
        
        # Critical issues
        if self.critical_issues:
            report.append("## ⚠️ Critical Issues")
            for issue in self.critical_issues:
                report.append(f"- {issue}")
            report.append("")
        
        # Detailed scores
        report.append("## Detailed Assessment")
        report.append("")
        
        for check_name, result in self.results["checks"].items():
            score = result["score"]
            max_score = result["max_score"]
            percentage = (score / max_score) * 100
            
            # Emoji based on score
            if percentage >= 80:
                emoji = "✅"
            elif percentage >= 60:
                emoji = "⚠️"
            else:
                emoji = "❌"
            
            report.append(f"### {emoji} {check_name.replace('_', ' ').title()}")
            report.append(f"**Score**: {score}/{max_score} ({percentage:.1f}%)")
            
            # Details
            if result.get("details"):
                report.append("**Details**:")
                for key, value in result["details"].items():
                    report.append(f"- {key.replace('_', ' ').title()}: {value}")
            
            # Issues
            if result.get("issues"):
                report.append("**Issues**:")
                for issue in result["issues"]:
                    report.append(f"- {issue}")
            
            report.append("")
        
        # Recommendations
        if self.recommendations:
            report.append("## 📋 Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Next steps
        report.append("## 🎯 Next Steps")
        
        if self.overall_score < 60:
            report.append("**Priority**: Address critical issues immediately")
            report.append("1. Fix all critical security and error handling issues")
            report.append("2. Implement comprehensive logging and monitoring")
            report.append("3. Add automated testing")
            report.append("4. Improve documentation coverage")
        elif self.overall_score < 80:
            report.append("**Priority**: Implement remaining production requirements")
            report.append("1. Complete test coverage")
            report.append("2. Enhance monitoring and alerting")
            report.append("3. Implement recovery mechanisms")
            report.append("4. Performance optimization")
        else:
            report.append("**Priority**: Fine-tune and optimize")
            report.append("1. Monitor performance in production")
            report.append("2. Implement continuous improvement")
            report.append("3. Regular security audits")
            report.append("4. Documentation maintenance")
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "production_readiness_report.md") -> str:
        """Save the readiness report to file"""
        report_content = self.generate_readiness_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Also save JSON data
        json_filename = filename.replace('.md', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"Production readiness report saved to {filename}")
        logger.info(f"JSON data saved to {json_filename}")
        
        return report_content


def main():
    """Main function for production readiness checker"""
    parser = argparse.ArgumentParser(
        description="MinhOS Production Readiness Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--root', type=str, default='.',
                       help='Root directory of the project')
    parser.add_argument('--output', type=str, default='production_readiness_report.md',
                       help='Output filename for the report')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON only')
    
    args = parser.parse_args()
    
    # Initialize and run the checker
    checker = ProductionReadinessChecker(args.root)
    results = checker.check_all()
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        # Generate and save report
        report_content = checker.save_report(args.output)
        
        # Print summary
        print("=" * 60)
        print("MINHOS PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        print(f"Overall Score: {results['overall_score']}/100")
        print(f"Grade: {results['grade']}")
        print(f"Status: {'READY' if results['overall_score'] >= 80 else 'NOT READY'}")
        print(f"Critical Issues: {len(results['critical_issues'])}")
        print(f"Recommendations: {len(results['recommendations'])}")
        print(f"\nFull report saved to: {args.output}")
        
        # Show critical issues
        if results['critical_issues']:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in results['critical_issues']:
                print(f"  - {issue}")
        
        # Show top recommendations
        if results['recommendations']:
            print("\n📋 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(results['recommendations'][:3], 1):
                print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()