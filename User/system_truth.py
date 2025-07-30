#!/usr/bin/env python
"""
System Truth - The system interrogates itself and reports reality
No documentation to maintain - only queries of actual state
"""
import os
import sys
import yaml
import json
import importlib.util
import ast
from datetime import datetime
from pathlib import Path

# Optional imports with graceful fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class SystemTruth:
    """The system documents itself by reporting what actually exists"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent.parent  # Go up one level from src/
        self.truth = {
            "generated": datetime.now().isoformat(),
            "working_directory": str(self.root_path),
            "services": {},
            "files": {},
            "config": {},
            "health": {},
            "dependencies": {},
            "recent_errors": [],
            "api_endpoints": {}
        }
    
    def discover_services(self):
        """Find all service files and analyze them"""
        print("Discovering services...")
        
        # Common service directories
        service_dirs = ["services", "core", ".", "dashboard", "src", "scripts"]
        service_files = []
        
        for dir_name in service_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                for file_path in dir_path.rglob("*.py"):
                    # Skip __pycache__ and test files
                    if "__pycache__" not in str(file_path) and not file_path.name.startswith("test_"):
                        service_files.append(file_path)
        
        for file_path in service_files:
            try:
                relative_path = file_path.relative_to(self.root_path)
                
                # Get file info
                stat = file_path.stat()
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.splitlines()
                
                # Analyze the file
                file_info = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "lines": len(lines),
                    "type": self._determine_file_type(file_path, content),
                    "ports": self._extract_ports(content),
                    "endpoints": self._extract_endpoints(content),
                    "imports": self._extract_imports(content),
                    "functions": self._extract_functions(content)
                }
                
                self.truth["files"][str(relative_path)] = file_info
                
                # If it's a service, add to services
                if file_info["type"] == "service":
                    self.truth["services"][file_path.stem] = {
                        "file": str(relative_path),
                        "port": file_info["ports"][0] if file_info["ports"] else None,
                        "endpoints": file_info["endpoints"]
                    }
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def _determine_file_type(self, file_path, content):
        """Determine what type of file this is"""
        name = file_path.name.lower()
        
        if "server" in name or "service" in name:
            return "service"
        elif name == "minh.py":
            return "launcher"
        elif name == "monitor.py":
            return "monitor"
        elif "config" in name:
            return "config"
        elif "test" in name:
            return "test"
        elif "if __name__ == '__main__':" in content:
            return "executable"
        else:
            return "library"
    
    def _extract_ports(self, content):
        """Extract port numbers from code"""
        import re
        ports = []
        
        # Look for port assignments
        port_patterns = [
            r'port\s*=\s*(\d+)',
            r'PORT\s*=\s*(\d+)',
            r':(\d{4})\b',  # 4-digit numbers that might be ports
            r'localhost:(\d+)'
        ]
        
        for pattern in port_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                port = int(match)
                if 1000 < port < 65535 and port not in ports:
                    ports.append(port)
        
        return sorted(set(ports))
    
    def _extract_endpoints(self, content):
        """Extract API endpoints from code"""
        import re
        endpoints = []
        
        # Patterns for different frameworks
        patterns = [
            r'@app\.route\([\'"]([^\'"]*)[\'"]\)',  # Flask
            r'@app\.get\([\'"]([^\'"]*)[\'"]\)',    # FastAPI
            r'@app\.post\([\'"]([^\'"]*)[\'"]\)',   # FastAPI
            r'self\.path == [\'"]([^\'"]*)[\'"]',    # BaseHTTPRequestHandler
            r'self\.path\.startswith\([\'"]([^\'"]*)[\'"]\)',  # Prefix matching
            r'/api/[a-zA-Z0-9-]+'  # Common API endpoint pattern - fixed escape sequences
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            endpoints.extend(matches)
        
        return sorted(set(endpoints))
    
    def _extract_imports(self, content):
        """Extract imported modules"""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass
        return sorted(set(imports))
    
    def _extract_functions(self, content):
        """Extract function names"""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            pass
        return functions
    
    def check_health(self):
        """Check what services are actually running with enhanced metrics"""
        print("Checking service health...")
        
        # MinhOS v3 health check endpoints
        health_checks = [
            ("sierra_bridge", "http://localhost:8765/health", 8765),
            ("sierra_bridge_market", "http://localhost:8765/market-data", 8765),
            ("minhos_dashboard", "http://localhost:8888/health", 8888),
            ("minhos_api", "http://localhost:8888/api/status", 8888),
            ("live_integration", "http://localhost:9005/health", 9005),
            ("sierra_client", "http://localhost:9003/health", 9003),
            ("multi_chart", "http://localhost:9004/health", 9004),
            ("ai_brain", "http://localhost:9006/health", 9006),
            ("trading_engine", "http://localhost:9007/health", 9007),
        ]
        
        for name, url, port in health_checks:
            service_metrics = {
                "status": "unknown",
                "response_time_ms": None,
                "status_code": None,
                "error": None,
                "last_checked": datetime.now().isoformat()
            }
            
            try:
                if url.startswith("ws://"):
                    # WebSocket check - simplified
                    import socket
                    import time
                    
                    start_time = time.time()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    response_time = (time.time() - start_time) * 1000
                    
                    if result == 0:
                        service_metrics.update({
                            "status": "running (websocket)",
                            "response_time_ms": response_time
                        })
                    else:
                        service_metrics.update({
                            "status": "down (connection refused)",
                            "error": "Connection refused"
                        })
                else:
                    # HTTP check with enhanced metrics
                    if REQUESTS_AVAILABLE:
                        import time
                        start_time = time.time()
                        resp = requests.get(url, timeout=1)
                        response_time = (time.time() - start_time) * 1000
                        
                        service_metrics.update({
                            "status": f"running (HTTP {resp.status_code})",
                            "response_time_ms": response_time,
                            "status_code": resp.status_code
                        })
                        
                        # Try to get more info
                        if "health" in url:
                            try:
                                data = resp.json()
                                if isinstance(data, dict):
                                    self.truth["health"][f"{name}_details"] = data
                            except:
                                pass
                    else:
                        # Fallback to socket check if requests not available
                        import socket
                        import time
                        
                        start_time = time.time()
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex(('localhost', port))
                        sock.close()
                        response_time = (time.time() - start_time) * 1000
                        
                        if result == 0:
                            service_metrics.update({
                                "status": "running (socket check)",
                                "response_time_ms": response_time
                            })
                        else:
                            service_metrics.update({
                                "status": "down (connection refused)",
                                "error": "Connection refused"
                            })
                
                self.truth["health"][f"{name}:{port}"] = service_metrics
                        
            except Exception as e:
                service_metrics.update({
                    "status": f"down ({type(e).__name__})",
                    "error": str(e)
                })
                self.truth["health"][f"{name}:{port}"] = service_metrics
    
    def read_configs(self):
        """Read all configuration files"""
        print("Reading configurations...")
        
        config_patterns = ["*.yaml", "*.yml", "*.json", ".env*"]
        config_dirs = ["config", ".", "startup", "scripts"]
        
        for dir_name in config_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                for pattern in config_patterns:
                    for config_file in dir_path.glob(pattern):
                        try:
                            relative_path = config_file.relative_to(self.root_path)
                            
                            if config_file.suffix in ['.yaml', '.yml']:
                                with open(config_file, 'r') as f:
                                    data = yaml.safe_load(f)
                                    self.truth["config"][str(relative_path)] = data
                            
                            elif config_file.suffix == '.json':
                                with open(config_file, 'r') as f:
                                    data = json.load(f)
                                    self.truth["config"][str(relative_path)] = data
                            
                            elif config_file.name == '.env':
                                # Don't expose secrets, just show what vars exist
                                with open(config_file, 'r') as f:
                                    lines = f.readlines()
                                    vars_defined = []
                                    for line in lines:
                                        if '=' in line and not line.strip().startswith('#'):
                                            var_name = line.split('=')[0].strip()
                                            vars_defined.append(var_name)
                                    self.truth["config"][".env"] = {
                                        "variables_defined": vars_defined
                                    }
                        except Exception as e:
                            print(f"Error reading {config_file}: {e}")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("Checking dependencies...")
        
        # Read requirements.txt if exists
        req_file = self.root_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            self.truth["dependencies"]["required"] = requirements
            
            # Check which are actually installed
            installed = []
            missing = []
            
            for req in requirements:
                # Simple check - just try to extract package name
                package_name = req.split('==')[0].split('>=')[0].split('<=')[0]
                
                # Handle special cases for package imports
                import_map = {
                    'pyyaml': 'yaml',
                    'python-dotenv': 'dotenv',
                    'websocket-client': 'websocket',
                    'python-dateutil': 'dateutil'
                }
                
                import_name = import_map.get(package_name.lower(), package_name.replace('-', '_'))
                
                try:
                    # Safely attempt to import - don't let one bad import crash everything
                    try:
                        __import__(import_name)
                        installed.append(package_name)
                    except ImportError:
                        missing.append(package_name)
                    except Exception as e:
                        # Handle other import errors (like version incompatibilities)
                        print(f"Error checking {package_name}: {str(e)[:100]}...")
                        missing.append(f"{package_name} (error: {type(e).__name__})")
                except:
                    # Ultimate fallback
                    missing.append(f"{package_name} (unknown error)")
            
            self.truth["dependencies"]["installed"] = installed
            self.truth["dependencies"]["missing"] = missing
    
    def check_recent_errors(self):
        """Check for recent errors in log files"""
        print("Checking for recent errors...")
        
        log_dirs = ["logs", "."]
        for dir_name in log_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                for log_file in dir_path.glob("*.log"):
                    try:
                        # Only check last 100 lines of each log
                        with open(log_file, 'r') as f:
                            lines = f.readlines()[-100:]
                        
                        for line in lines:
                            if any(word in line.lower() for word in ['error', 'exception', 'failed', 'critical']):
                                self.truth["recent_errors"].append({
                                    "file": str(log_file.name),
                                    "line": line.strip()
                                })
                    except:
                        pass
        
        # Keep only last 10 errors
        self.truth["recent_errors"] = self.truth["recent_errors"][-10:]
    
    def validate_port_consistency(self):
        """Validate port consistency across the system
        This helps ensure all components reference the same ports
        """
        print("Validating port consistency...")
        
        # Define the expected ports for MinhOS v3 services
        expected_ports = {
            "sierra_bridge": 8765,
            "minhos_dashboard": 8888,
            "live_integration": 9005,
            "sierra_client": 9003,
            "multi_chart_collector": 9004,
            "ai_brain_service": 9006,
            "trading_engine": 9007,
            "state_manager": 9008,
            "risk_manager": 9009
        }
        
        # Initialize validation results
        self.truth["port_validation"] = {
            "status": "passed",
            "inconsistencies": []
        }
        
        # Track actual port inconsistencies - use more precise detection
        inconsistency_count = 0
        
        # Scan all Python files for specific port misconfigurations
        for file_path, file_info in self.truth["files"].items():
            file_ports = file_info.get("ports", [])
            
            # Only check Python files
            if not str(file_path).endswith(".py"):
                continue
                
            # If we have extracted ports from this file
            if file_ports:
                try:
                    abs_path = self.root_path / file_path
                    if abs_path.exists():
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Very conservative port validation - only flag actual server startup issues
                            # This minimizes false positives while catching real problems
                            
                            import re
                            
                            # Only check for server startup patterns that might be wrong
                            # Pattern: HTTPServer((host, port)) or similar server instantiation
                            server_patterns = [
                                r'HTTPServer\([^,]+,\s*(\d{4})\)',  # HTTPServer(('localhost', 8000))
                                r'run\([^,]+,\s*port\s*=\s*(\d{4})\)',  # app.run(host='localhost', port=8000)
                                r'serve_forever\([^,]+,\s*(\d{4})\)',  # serve_forever(host, port)
                                r'websocket.*serve\([^,]+,\s*(\d{4})\)',  # websocket.serve(handler, host, port)
                            ]
                            
                            filename = str(file_path).lower()
                            
                            for pattern in server_patterns:
                                matches = re.findall(pattern, content)
                                for port_str in matches:
                                    port = int(port_str)
                                    
                                    # Only flag if the filename strongly suggests this is the wrong service
                                    if "websocket_server.py" in filename and port != expected_ports["websocket"]:
                                        inconsistency = {
                                            "service": "websocket",
                                            "file": file_path,
                                            "incorrect_port": port,
                                            "expected_port": expected_ports["websocket"]
                                        }
                                        self.truth["port_validation"]["inconsistencies"].append(inconsistency)
                                        inconsistency_count += 1
                                    elif "backend_study.py" in filename and port != expected_ports["backend_study"]:
                                        inconsistency = {
                                            "service": "backend_study", 
                                            "file": file_path,
                                            "incorrect_port": port,
                                            "expected_port": expected_ports["backend_study"]
                                        }
                                        self.truth["port_validation"]["inconsistencies"].append(inconsistency)
                                        inconsistency_count += 1
                                    elif "http_server.py" in filename and port != expected_ports["http_server"]:
                                        inconsistency = {
                                            "service": "http_server",
                                            "file": file_path,
                                            "incorrect_port": port,
                                            "expected_port": expected_ports["http_server"]
                                        }
                                        self.truth["port_validation"]["inconsistencies"].append(inconsistency)
                                        inconsistency_count += 1
                                    elif ("dashboard" in filename and "main.py" in filename or "server.py" in filename) and port != expected_ports["dashboard"]:
                                        inconsistency = {
                                            "service": "dashboard",
                                            "file": file_path,
                                            "incorrect_port": port,
                                            "expected_port": expected_ports["dashboard"]
                                        }
                                        self.truth["port_validation"]["inconsistencies"].append(inconsistency)
                                        inconsistency_count += 1
                except Exception as e:
                    print(f"Error scanning {file_path} for port consistency: {e}")
        
        # Update validation status
        if inconsistency_count > 0:
            self.truth["port_validation"]["status"] = "failed"
            self.truth["port_validation"]["message"] = f"Found {inconsistency_count} port inconsistencies"
        else:
            self.truth["port_validation"]["status"] = "passed"
            self.truth["port_validation"]["message"] = "All port references are consistent"
    
    def generate_report(self):
        """Generate the complete truth report"""
        print("\nGenerating system truth report...\n")
        
        # Run all discovery methods
        self.discover_services()
        self.check_health()
        self.read_configs()
        
        try:
            self.check_dependencies()
        except Exception as e:
            print(f"Error checking dependencies: {e}")
            self.truth["dependencies"]["error"] = f"Failed to check: {type(e).__name__}: {str(e)[:200]}"
            
        self.check_recent_errors()
        
        # Build the markdown report
        report_lines = [
            "# MinhOS System Truth Report",
            f"Generated: {self.truth['generated']}",
            f"Working Directory: {self.truth['working_directory']}",
            "",
            "## Executive Summary",
            ""
        ]
        
        # Quick stats
        total_files = len(self.truth['files'])
        service_files = len([f for f in self.truth['files'].values() if f['type'] == 'service'])
        running_services = len([h for h in self.truth['health'].values() if 'running' in str(h)])
        total_services = len(self.truth['health'])
        
        report_lines.extend([
            f"- Total Files: {total_files}",
            f"- Service Files: {service_files}",
            f"- Services Running: {running_services}/{total_services}",
            f"- Config Files: {len(self.truth['config'])}",
            f"- Recent Errors: {len(self.truth['recent_errors'])}",
            ""
        ])
        
        # Service health
        report_lines.extend([
            "## Service Health",
            "",
            "| Service | Port | Status |",
            "|---------|------|--------|"
        ])
        
        for service, status in sorted(self.truth['health'].items()):
            if not service.endswith('_details'):
                port = service.split(':')[-1] if ':' in service else 'N/A'
                service_name = service.split(':')[0]
                status_emoji = "[UP]" if "running" in str(status) else "[DOWN]"
                report_lines.append(f"| {service_name} | {port} | {status_emoji} {status} |")
        
        # File structure
        report_lines.extend([
            "",
            "## File Structure",
            "",
            "```"
        ])
        
        # Group files by directory
        from collections import defaultdict
        by_dir = defaultdict(list)
        
        for filepath, info in sorted(self.truth['files'].items()):
            dir_name = os.path.dirname(filepath) or "."
            by_dir[dir_name].append((os.path.basename(filepath), info))
        
        for dir_name, files in sorted(by_dir.items()):
            report_lines.append(f"{dir_name}/")
            for filename, info in sorted(files):
                type_emoji = {
                    "service": "[SVC]",
                    "launcher": "[LAUNCH]",
                    "monitor": "[MONITOR]",
                    "config": "[CONFIG]",
                    "executable": "[EXEC]",
                    "library": "[LIB]",
                    "test": "[TEST]"
                }.get(info['type'], "[FILE]")
                
                ports = f" (ports: {','.join(map(str, info['ports']))})" if info['ports'] else ""
                report_lines.append(f"  {type_emoji} {filename} - {info['lines']} lines{ports}")
        
        report_lines.append("```")
        
        # Configuration summary
        if self.truth['config']:
            report_lines.extend([
                "",
                "## Configuration Files",
                ""
            ])
            
            for config_path, config_data in sorted(self.truth['config'].items()):
                report_lines.append(f"### {config_path}")
                if config_path == ".env":
                    report_lines.append(f"Variables defined: {', '.join(config_data['variables_defined'])}")
                else:
                    report_lines.append("```yaml")
                    report_lines.append(yaml.dump(config_data, default_flow_style=False))
                    report_lines.append("```")
        
        # API Endpoints discovered
        all_endpoints = []
        for file_info in self.truth['files'].values():
            all_endpoints.extend(file_info.get('endpoints', []))
        
        if all_endpoints:
            report_lines.extend([
                "",
                "## API Endpoints Discovered",
                ""
            ])
            for endpoint in sorted(set(all_endpoints)):
                report_lines.append(f"- {endpoint}")
        
        # Dependencies
        if self.truth['dependencies']:
            report_lines.extend([
                "",
                "## Dependencies",
                ""
            ])
            
            if self.truth['dependencies'].get('missing'):
                report_lines.extend([
                    "### [WARNING] Missing Dependencies",
                    ""
                ])
                for dep in self.truth['dependencies']['missing']:
                    report_lines.append(f"- {dep}")
                report_lines.append("")
            
            report_lines.extend([
                "### Required Dependencies",
                ""
            ])
            for dep in self.truth['dependencies'].get('required', []):
                status = "[INSTALLED]" if dep.split('==')[0].split('>=')[0] in self.truth['dependencies'].get('installed', []) else "[MISSING]"
                report_lines.append(f"- {status} {dep}")
        
        # Port Validation
        if 'port_validation' in self.truth:
            report_lines.extend([
                "",
                "## Port Configuration Validation",
                ""
            ])
            
            status = self.truth['port_validation']['status']
            message = self.truth['port_validation'].get('message', '')
            status_emoji = "✅" if status == "passed" else "⚠️"
            
            report_lines.append(f"**Status: {status_emoji} {status.upper()}** - {message}")
            report_lines.append("")
            
            # Expected ports
            report_lines.extend([
                "### Expected Port Configuration",
                "",
                "| Service | Expected Port |",
                "|---------|--------------|"  
            ])
            
            expected_ports = {
                "sierra_bridge": 8765,
                "minhos_dashboard": 8888,
                "live_integration": 9005,
                "sierra_client": 9003,
                "multi_chart_collector": 9004,
                "ai_brain_service": 9006,
                "trading_engine": 9007,
                "state_manager": 9008,
                "risk_manager": 9009
            }
            
            for service, port in sorted(expected_ports.items()):
                report_lines.append(f"| {service} | {port} |")
            
            # Show inconsistencies if found
            inconsistencies = self.truth['port_validation'].get('inconsistencies', [])
            if inconsistencies:
                report_lines.extend([
                    "",
                    "### Port Inconsistencies Found",
                    "",
                    "| Service | File | Incorrect Port | Expected Port |",
                    "|---------|------|---------------|--------------|"  
                ])
                
                for issue in inconsistencies:
                    report_lines.append(f"| {issue['service']} | {issue['file']} | {issue['incorrect_port']} | {issue['expected_port']} |")
                    
                report_lines.extend([
                    "",
                    "⚠️ **Action Required**: Update the above files to use the correct ports."
                ])
        
        # Recent errors
        if self.truth['recent_errors']:
            report_lines.extend([
                "",
                "## Recent Errors",
                ""
            ])
            for error in self.truth['recent_errors'][-5:]:  # Last 5 errors
                report_lines.append(f"- **{error['file']}**: `{error['line'][:100]}...`")
        
        # How to use this report
        report_lines.extend([
            "",
            "## Using This Report",
            "",
            "1. **For AI Context**: Copy this entire report when asking for help",
            "2. **For Debugging**: Check service health and recent errors",
            "3. **For Development**: See file structure and dependencies",
            "4. **For Verification**: Compare actual state vs expected state",
            "",
            "To regenerate: `python system_truth.py`"
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, filename="SYSTEM_TRUTH.md"):
        """Save the report to file"""
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Also save as JSON for programmatic access
        with open(filename.replace('.md', '.json'), 'w', encoding='utf-8') as f:
            json.dump(self.truth, f, indent=2, default=str)
        
        print(f"\n[SUCCESS] Report saved to {filename}")
        print(f"[SUCCESS] JSON data saved to {filename.replace('.md', '.json')}")
        
        return report
    
    def get_system_health_summary(self):
        """Get a concise system health summary for integration with context generator"""
        running_services = []
        down_services = []
        
        for service, status in self.truth['health'].items():
            if not service.endswith('_details'):
                if 'running' in str(status):
                    running_services.append(service)
                else:
                    down_services.append(service)
        
        return {
            'running_services': running_services,
            'down_services': down_services,
            'total_services': len(running_services) + len(down_services),
            'health_percentage': round(len(running_services) / (len(running_services) + len(down_services)) * 100) if (running_services or down_services) else 0,
            'recent_errors': len(self.truth['recent_errors']),
            'missing_dependencies': len(self.truth['dependencies'].get('missing', [])),
            'port_validation_status': self.truth.get('port_validation', {}).get('status', 'unknown')
        }
    
    def check_data_flow_bottlenecks(self):
        """Identify data flow bottlenecks and performance issues"""
        print("Analyzing data flow bottlenecks...")
        
        bottlenecks = {
            "sierra_chart_data_age": self._check_sierra_chart_data_freshness(),
            "database_performance": self._check_database_performance(),
            "service_response_times": self._analyze_service_response_times(),
            "queue_backlogs": self._check_queue_backlogs(),
            "disk_io_bottlenecks": self._check_disk_io()
        }
        
        self.truth["data_flow_bottlenecks"] = bottlenecks
        return bottlenecks
    
    def _check_sierra_chart_data_freshness(self):
        """Check how fresh Sierra Chart data is"""
        data_files = [
            self.root_path / "database" / "latest_market_data.json",
            self.root_path / "database" / "market_data_history.json"
        ]
        
        freshness_info = {}
        
        for data_file in data_files:
            if data_file.exists():
                try:
                    stat = data_file.stat()
                    age_seconds = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds()
                    
                    # Also check content if it's JSON
                    if data_file.suffix == '.json':
                        try:
                            with open(data_file, 'r') as f:
                                data = json.load(f)
                                if 'received_at' in data:
                                    content_age = datetime.now() - datetime.fromisoformat(data['received_at'].replace('Z', '+00:00'))
                                    freshness_info[str(data_file)] = {
                                        "file_age_seconds": age_seconds,
                                        "content_age_seconds": content_age.total_seconds(),
                                        "is_stale": content_age.total_seconds() > 60
                                    }
                        except:
                            freshness_info[str(data_file)] = {
                                "file_age_seconds": age_seconds,
                                "content_age_seconds": None,
                                "is_stale": age_seconds > 60
                            }
                    else:
                        freshness_info[str(data_file)] = {
                            "file_age_seconds": age_seconds,
                            "is_stale": age_seconds > 60
                        }
                except Exception as e:
                    freshness_info[str(data_file)] = {"error": str(e)}
        
        return freshness_info
    
    def _check_database_performance(self):
        """Check database performance metrics"""
        db_performance = {}
        
        # Check SQLite database if exists
        sqlite_db = self.root_path / "data" / "minhos_state.db"
        if sqlite_db.exists():
            try:
                import time
                start_time = time.time()
                
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Get database size
                db_size = sqlite_db.stat().st_size
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                table_info = {}
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    table_info[table_name] = row_count
                
                # Simple performance test
                cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                query_time = time.time() - start_time
                
                conn.close()
                
                db_performance["sqlite"] = {
                    "size_bytes": db_size,
                    "tables": table_info,
                    "query_time_ms": query_time * 1000,
                    "performance_rating": "good" if query_time < 0.1 else "slow"
                }
                
            except Exception as e:
                db_performance["sqlite"] = {"error": str(e)}
        
        return db_performance
    
    def _analyze_service_response_times(self):
        """Analyze service response times for bottlenecks"""
        response_times = {}
        
        # Get response times from health check data
        for service_key, health_data in self.truth.get("health", {}).items():
            if isinstance(health_data, dict) and "response_time_ms" in health_data:
                response_time = health_data["response_time_ms"]
                if response_time is not None:
                    service_name = service_key.split(":")[0]
                    response_times[service_name] = {
                        "response_time_ms": response_time,
                        "is_slow": response_time > 1000,  # Consider >1s as slow
                        "rating": self._rate_response_time(response_time)
                    }
        
        return response_times
    
    def _rate_response_time(self, response_time_ms):
        """Rate response time performance"""
        if response_time_ms < 100:
            return "excellent"
        elif response_time_ms < 500:
            return "good"
        elif response_time_ms < 1000:
            return "acceptable"
        else:
            return "slow"
    
    def _check_queue_backlogs(self):
        """Check for any queue backlogs (placeholder for future implementation)"""
        # This would check message queues, event queues, etc.
        # For now, return placeholder
        return {"message": "Queue monitoring not implemented yet"}
    
    def _check_disk_io(self):
        """Check disk I/O performance"""
        disk_io = {}
        
        try:
            # Check disk space
            import shutil
            disk_usage = shutil.disk_usage(self.root_path)
            
            disk_io["disk_space"] = {
                "total_bytes": disk_usage.total,
                "used_bytes": disk_usage.used,
                "free_bytes": disk_usage.free,
                "usage_percent": (disk_usage.used / disk_usage.total) * 100
            }
            
            # Check log file sizes (potential I/O bottleneck)
            logs_dir = self.root_path / "logs"
            if logs_dir.exists():
                log_sizes = {}
                for log_file in logs_dir.glob("*.log"):
                    log_sizes[log_file.name] = log_file.stat().st_size
                
                disk_io["log_file_sizes"] = log_sizes
                disk_io["total_log_size"] = sum(log_sizes.values())
            
        except Exception as e:
            disk_io["error"] = str(e)
        
        return disk_io
    
    def track_configuration_drift(self):
        """Track configuration changes over time"""
        print("Tracking configuration drift...")
        
        # Create a hash of current configuration
        current_config_hash = self._calculate_config_hash()
        
        # Store configuration snapshot
        config_snapshot = {
            "timestamp": datetime.now().isoformat(),
            "config_hash": current_config_hash,
            "config_files": {},
            "environment_vars": self._get_environment_variables(),
            "system_info": self._get_system_info()
        }
        
        # Capture current configuration state
        config_files = ["config.yaml", "requirements.txt", "setup.py"]
        for config_file in config_files:
            file_path = self.root_path / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    config_snapshot["config_files"][config_file] = {
                        "content_hash": hash(content),
                        "size": len(content),
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                except Exception as e:
                    config_snapshot["config_files"][config_file] = {"error": str(e)}
        
        # Load previous snapshot if exists
        drift_file = self.root_path / "config_drift_history.json"
        config_history = []
        
        if drift_file.exists():
            try:
                with open(drift_file, 'r') as f:
                    config_history = json.load(f)
            except:
                pass
        
        # Compare with previous snapshot
        drift_info = {"has_drift": False, "changes": []}
        
        if config_history:
            last_snapshot = config_history[-1]
            if last_snapshot["config_hash"] != current_config_hash:
                drift_info["has_drift"] = True
                
                # Detect specific changes
                for file_name, current_info in config_snapshot["config_files"].items():
                    if file_name in last_snapshot["config_files"]:
                        last_info = last_snapshot["config_files"][file_name]
                        if current_info.get("content_hash") != last_info.get("content_hash"):
                            drift_info["changes"].append({
                                "file": file_name,
                                "type": "modified",
                                "last_modified": current_info.get("last_modified")
                            })
        
        # Add current snapshot to history
        config_history.append(config_snapshot)
        
        # Keep only last 10 snapshots
        config_history = config_history[-10:]
        
        # Save updated history
        try:
            with open(drift_file, 'w') as f:
                json.dump(config_history, f, indent=2)
        except Exception as e:
            drift_info["save_error"] = str(e)
        
        self.truth["configuration_drift"] = drift_info
        return drift_info
    
    def _calculate_config_hash(self):
        """Calculate a hash of all configuration files"""
        import hashlib
        
        hasher = hashlib.md5()
        config_files = ["config.yaml", "requirements.txt", "setup.py"]
        
        for config_file in config_files:
            file_path = self.root_path / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
                except:
                    pass
        
        return hasher.hexdigest()
    
    def _get_environment_variables(self):
        """Get relevant environment variables"""
        env_vars = {}
        relevant_vars = ["PATH", "PYTHONPATH", "HOME", "USER"]
        
        for var in relevant_vars:
            env_vars[var] = os.environ.get(var, "NOT_SET")
        
        return env_vars
    
    def _get_system_info(self):
        """Get basic system information"""
        import platform
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }
    
    def export_for_context_generator(self):
        """Export system truth data in format suitable for context generator"""
        return {
            'system_health': self.get_system_health_summary(),
            'services': self.truth['services'],
            'health_details': self.truth['health'],
            'config_files': list(self.truth['config'].keys()),
            'recent_errors': self.truth['recent_errors'][-5:],  # Last 5 errors
            'dependencies': self.truth['dependencies'],
            'port_validation': self.truth.get('port_validation', {}),
            'data_flow_bottlenecks': self.truth.get('data_flow_bottlenecks', {}),
            'configuration_drift': self.truth.get('configuration_drift', {}),
            'generated_at': self.truth['generated']
        }


# Add specific information about unified dashboard endpoints
def add_dashboard_endpoints(truth):
    """Add known unified dashboard endpoints to the API endpoints list"""
    if "api_endpoints" not in truth.truth:
        truth.truth["api_endpoints"] = {}
    
    # Add known MinhOS v3 dashboard endpoints
    truth.truth["api_endpoints"]["minhos_dashboard"] = [
        "/",
        "/health",
        "/ws",
        "/api/system_status",
        "/api/market_data", 
        "/api/ai_status",
        "/api/risk_status",
        "/api/system_health"
    ]
    
    return truth


def main():
    """Run system truth analysis"""
    print("=" * 60)
    print("MinhOS System Truth - Analyzing system state...")
    print("=" * 60)
    print()

    truth = SystemTruth()
    
    # Run all discovery methods
    truth.discover_services()
    truth.check_health()
    truth.read_configs()
    
    # Validate port consistency
    truth.validate_port_consistency()
    
    try:
        truth.check_dependencies()
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        truth.truth["dependencies"]["error"] = f"Failed to check: {type(e).__name__}: {str(e)[:200]}"
        
    truth.check_recent_errors()
    
    # Enhanced system analysis
    try:
        truth.check_data_flow_bottlenecks()
    except Exception as e:
        print(f"Error checking data flow bottlenecks: {e}")
        truth.truth["data_flow_bottlenecks"] = {"error": str(e)}
    
    try:
        truth.track_configuration_drift()
    except Exception as e:
        print(f"Error tracking configuration drift: {e}")
        truth.truth["configuration_drift"] = {"error": str(e)}
    
    # Add specific unified dashboard information
    truth = add_dashboard_endpoints(truth)
    
    report = truth.save_report()
    
    # Print a sample of the report
    lines = report.split('\n')
    print('\n'.join(lines[:20]))
    print(f"...and {len(lines)-20} more lines")

    # Quick health check
    running = [s for s, status in truth.truth['health'].items() if 'running' in str(status)]
    down = [s for s, status in truth.truth['health'].items() if 'down' in str(status)]
    
    if running:
        print(f"\n[UP] Running Services ({len(running)}):")
        for service in running:
            print(f"   - {service}")
    
    if down:
        print(f"\n[DOWN] Down Services ({len(down)}):")
        for service in down:
            print(f"   - {service}")
    
    if truth.truth['dependencies'].get('missing'):
        print(f"\n[WARNING] Missing Dependencies:")
        for dep in truth.truth['dependencies']['missing']:
            print(f"   - {dep}")
    
    print("\n" + "=" * 60)
    print("Full report saved to SYSTEM_TRUTH.md")
    print("=" * 60)
    
    # Check for port inconsistencies and exit with error code if found
    if truth.truth.get('port_validation', {}).get('status') == "failed":
        inconsistencies = truth.truth.get('port_validation', {}).get('inconsistencies', [])
        print("\n[CRITICAL ERROR] Port inconsistencies detected!")
        print(f"Found {len(inconsistencies)} port inconsistencies that must be fixed.")
        print("Run 'python fix_all_ports.py' to automatically fix these issues.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())