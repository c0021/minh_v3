#!/usr/bin/env python3
"""
MinhOS Documentation Generator
============================
Automatically analyzes Python files and adds intelligent docstrings based on code analysis.
Prioritizes critical paths (trading logic, risk management, data flow).

Usage:
    python tools/add_documentation.py [options]
"""

import os
import sys
import ast
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("doc_generator")

class FunctionAnalyzer:
    """Analyzes Python functions to generate intelligent docstrings"""
    
    def __init__(self):
        self.trading_keywords = ['trade', 'buy', 'sell', 'order', 'position', 'signal', 'strategy', 'market', 'price']
        self.risk_keywords = ['risk', 'limit', 'stop', 'exposure', 'validation', 'check', 'threshold']
        self.data_keywords = ['data', 'parse', 'process', 'fetch', 'load', 'save', 'update', 'transform']
        self.ai_keywords = ['analyze', 'predict', 'learn', 'pattern', 'intelligence', 'brain', 'neural']
        
    def analyze_function(self, func_node: ast.FunctionDef, file_content: str) -> Dict:
        """Analyze a function node and extract information for documentation"""
        analysis = {
            'name': func_node.name,
            'line_number': func_node.lineno,
            'args': self._extract_args(func_node),
            'return_type': self._extract_return_type(func_node),
            'docstring': self._extract_docstring(func_node),
            'complexity': self._calculate_complexity(func_node),
            'category': self._categorize_function(func_node.name, file_content),
            'calls': self._extract_function_calls(func_node),
            'raises': self._extract_exceptions(func_node),
            'decorators': self._extract_decorators(func_node)
        }
        return analysis
    
    def _extract_args(self, func_node: ast.FunctionDef) -> List[Dict]:
        """Extract function arguments with type hints"""
        args = []
        
        # Handle regular arguments
        for arg in func_node.args.args:
            arg_info = {
                'name': arg.arg,
                'type': self._extract_type_annotation(arg.annotation) if arg.annotation else None,
                'default': None
            }
            args.append(arg_info)
        
        # Handle defaults
        defaults = func_node.args.defaults
        if defaults:
            # Match defaults to args (defaults are for the last N args)
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                arg_index = len(args) - num_defaults + i
                if arg_index >= 0 and arg_index < len(args):
                    args[arg_index]['default'] = ast.unparse(default)
        
        return args
    
    def _extract_type_annotation(self, annotation) -> str:
        """Extract type annotation as string"""
        if annotation:
            return ast.unparse(annotation)
        return None
    
    def _extract_return_type(self, func_node: ast.FunctionDef) -> str:
        """Extract return type annotation"""
        if func_node.returns:
            return ast.unparse(func_node.returns)
        return None
    
    def _extract_docstring(self, func_node: ast.FunctionDef) -> str:
        """Extract existing docstring if present"""
        if (func_node.body and 
            isinstance(func_node.body[0], ast.Expr) and
            isinstance(func_node.body[0].value, ast.Constant) and
            isinstance(func_node.body[0].value.value, str)):
            return func_node.body[0].value.value
        return None
    
    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _categorize_function(self, func_name: str, file_content: str) -> str:
        """Categorize function based on name and context"""
        name_lower = func_name.lower()
        
        # Check function name against keywords
        if any(keyword in name_lower for keyword in self.trading_keywords):
            return "trading"
        elif any(keyword in name_lower for keyword in self.risk_keywords):
            return "risk"
        elif any(keyword in name_lower for keyword in self.data_keywords):
            return "data"
        elif any(keyword in name_lower for keyword in self.ai_keywords):
            return "ai"
        elif name_lower.startswith('_'):
            return "internal"
        elif name_lower in ['__init__', '__str__', '__repr__']:
            return "magic"
        else:
            return "general"
    
    def _extract_function_calls(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract function calls made within the function"""
        calls = []
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        return list(set(calls))
    
    def _extract_exceptions(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract exceptions that might be raised"""
        exceptions = []
        for node in ast.walk(func_node):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    exceptions.append(node.exc.func.id)
        return list(set(exceptions))
    
    def _extract_decorators(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract function decorators"""
        decorators = []
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)
        return decorators


class DocstringGenerator:
    """Generates intelligent docstrings based on function analysis"""
    
    def generate_docstring(self, analysis: Dict) -> str:
        """Generate a comprehensive docstring based on function analysis"""
        docstring_parts = []
        
        # Function description
        description = self._generate_description(analysis)
        docstring_parts.append(description)
        
        # Arguments section
        if analysis['args']:
            docstring_parts.append("")
            docstring_parts.append("Args:")
            for arg in analysis['args']:
                arg_doc = self._generate_arg_documentation(arg)
                docstring_parts.append(f"    {arg_doc}")
        
        # Returns section
        if analysis['return_type']:
            docstring_parts.append("")
            docstring_parts.append("Returns:")
            return_doc = self._generate_return_documentation(analysis)
            docstring_parts.append(f"    {return_doc}")
        
        # Raises section
        if analysis['raises']:
            docstring_parts.append("")
            docstring_parts.append("Raises:")
            for exception in analysis['raises']:
                docstring_parts.append(f"    {exception}: Description of when this exception is raised")
        
        # Examples section for complex functions
        if analysis['complexity'] > 3 or analysis['category'] in ['trading', 'risk', 'ai']:
            docstring_parts.append("")
            docstring_parts.append("Example:")
            example = self._generate_example(analysis)
            docstring_parts.append(f"    {example}")
        
        # Performance considerations for critical functions
        if analysis['category'] in ['trading', 'risk', 'data'] and analysis['complexity'] > 2:
            docstring_parts.append("")
            docstring_parts.append("Note:")
            note = self._generate_performance_note(analysis)
            docstring_parts.append(f"    {note}")
        
        # Build final docstring
        docstring = '"""' + '\n'.join(docstring_parts) + '\n"""'
        return docstring
    
    def _generate_description(self, analysis: Dict) -> str:
        """Generate function description based on analysis"""
        name = analysis['name']
        category = analysis['category']
        
        # Generate category-specific descriptions
        if category == 'trading':
            if 'buy' in name.lower() or 'sell' in name.lower():
                return f"Execute {name.lower()} trading operation with risk management and validation"
            elif 'signal' in name.lower():
                return f"Generate or process trading signal based on market analysis"
            elif 'strategy' in name.lower():
                return f"Implement trading strategy logic with position management"
            else:
                return f"Handle trading-related operations for {name}"
        
        elif category == 'risk':
            if 'check' in name.lower() or 'validate' in name.lower():
                return f"Validate risk parameters and trading constraints"
            elif 'limit' in name.lower():
                return f"Apply risk limits and position sizing constraints"
            else:
                return f"Manage risk controls and safety measures"
        
        elif category == 'data':
            if 'parse' in name.lower():
                return f"Parse and validate incoming data from external sources"
            elif 'process' in name.lower():
                return f"Process and transform data for downstream consumption"
            elif 'fetch' in name.lower() or 'load' in name.lower():
                return f"Retrieve data from storage or external sources"
            else:
                return f"Handle data operations and transformations"
        
        elif category == 'ai':
            if 'analyze' in name.lower():
                return f"Perform intelligent analysis using AI/ML algorithms"
            elif 'predict' in name.lower():
                return f"Generate predictions based on historical patterns"
            elif 'learn' in name.lower():
                return f"Update AI models with new market data"
            else:
                return f"Execute AI-driven analysis and decision making"
        
        elif category == 'internal':
            return f"Internal helper function for {name[1:] if name.startswith('_') else name}"
        
        elif category == 'magic':
            if name == '__init__':
                return "Initialize the instance with required parameters"
            elif name == '__str__':
                return "Return string representation of the object"
            elif name == '__repr__':
                return "Return detailed string representation for debugging"
        
        else:
            # Generate generic description
            if name.startswith('get_'):
                return f"Retrieve {name[4:].replace('_', ' ')}"
            elif name.startswith('set_'):
                return f"Set {name[4:].replace('_', ' ')}"
            elif name.startswith('is_') or name.startswith('has_'):
                return f"Check if {name[3:].replace('_', ' ')}"
            elif name.startswith('create_'):
                return f"Create {name[7:].replace('_', ' ')}"
            elif name.startswith('update_'):
                return f"Update {name[7:].replace('_', ' ')}"
            elif name.startswith('delete_'):
                return f"Delete {name[7:].replace('_', ' ')}"
            else:
                return f"Handle {name.replace('_', ' ')}"
    
    def _generate_arg_documentation(self, arg: Dict) -> str:
        """Generate documentation for a function argument"""
        name = arg['name']
        arg_type = arg['type'] or 'Any'
        default = arg['default']
        
        doc = f"{name} ({arg_type})"
        
        if default:
            doc += f", optional"
        
        doc += f": Description of {name}"
        
        if default:
            doc += f". Defaults to {default}"
        
        return doc
    
    def _generate_return_documentation(self, analysis: Dict) -> str:
        """Generate return value documentation"""
        return_type = analysis['return_type'] or 'Any'
        category = analysis['category']
        
        if category == 'trading':
            return f"{return_type}: Trading execution result with status and details"
        elif category == 'risk':
            return f"{return_type}: Risk assessment result or validation status"
        elif category == 'data':
            return f"{return_type}: Processed data in specified format"
        elif category == 'ai':
            return f"{return_type}: Analysis result or prediction output"
        else:
            return f"{return_type}: Function execution result"
    
    def _generate_example(self, analysis: Dict) -> str:
        """Generate usage example for complex functions"""
        name = analysis['name']
        args = analysis['args']
        category = analysis['category']
        
        # Generate simple example call
        if args:
            arg_names = [arg['name'] for arg in args if arg['name'] != 'self']
            if arg_names:
                example_args = ', '.join(arg_names)
                return f"result = {name}({example_args})"
        
        return f"result = {name}()"
    
    def _generate_performance_note(self, analysis: Dict) -> str:
        """Generate performance considerations note"""
        category = analysis['category']
        complexity = analysis['complexity']
        
        if category == 'trading':
            return "Critical trading function - ensure proper error handling and logging"
        elif category == 'risk':
            return "Risk management function - must be highly reliable and fast"
        elif category == 'data':
            return "Data processing function - consider memory usage with large datasets"
        elif complexity > 5:
            return "Complex function - consider breaking down into smaller functions"
        else:
            return "Performance considerations depend on usage context"


class MinhOSDocumentationGenerator:
    """Main documentation generator for MinhOS"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.analyzer = FunctionAnalyzer()
        self.docstring_generator = DocstringGenerator()
        
        # Priority order for documentation
        self.priority_modules = [
            "services/backend_study_enhanced.py",
            "services/risk_manager.py", 
            "services/trading_copilot.py",
            "core/ai/meta_intelligence_trading.py",
            "services/state_manager.py",
            "services/ai_brain_service.py",
            "services/market_data_watcher.py",
            "services/http_server.py",
            "services/websocket_server.py",
            "dashboard/main.py"
        ]
        
        self.stats = {
            'files_processed': 0,
            'functions_documented': 0,
            'functions_updated': 0,
            'functions_skipped': 0
        }
    
    def scan_undocumented_functions(self) -> Dict[str, List[Dict]]:
        """Scan all Python files and identify undocumented functions"""
        undocumented = {}
        
        # Process priority modules first
        for module_path in self.priority_modules:
            full_path = self.root_path / module_path
            if full_path.exists():
                functions = self._analyze_file(full_path)
                undocumented_functions = [f for f in functions if not f['docstring']]
                if undocumented_functions:
                    undocumented[module_path] = undocumented_functions
        
        # Then process all other Python files
        for py_file in self.root_path.rglob("*.py"):
            if self._should_process_file(py_file):
                relative_path = py_file.relative_to(self.root_path)
                if str(relative_path) not in undocumented:
                    functions = self._analyze_file(py_file)
                    undocumented_functions = [f for f in functions if not f['docstring']]
                    if undocumented_functions:
                        undocumented[str(relative_path)] = undocumented_functions
        
        return undocumented
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        # Skip certain directories and files
        skip_patterns = [
            '__pycache__',
            '.git',
            'test_',
            'tests/',
            'venv/',
            'env/',
            '.venv/',
            'build/',
            'dist/'
        ]
        
        file_str = str(file_path)
        return not any(pattern in file_str for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a single Python file for functions"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis = self.analyzer.analyze_function(node, content)
                    functions.append(analysis)
            
            self.stats['files_processed'] += 1
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
        
        return functions
    
    def add_documentation(self, file_path: str, dry_run: bool = False, min_complexity: int = 0, verbose: bool = False) -> bool:
        """Add documentation to a specific file"""
        full_path = self.root_path / file_path
        
        if not full_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.splitlines()
            
            # Process functions in reverse order to avoid line number shifts
            functions_to_document = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis = self.analyzer.analyze_function(node, content)
                    
                    # Skip functions that shouldn't be documented
                    if analysis.get('skip_documentation', False):
                        if verbose:
                            logger.info(f"Skipping simple __init__ method: {analysis['name']}")
                        continue
                    
                    # Apply minimum complexity threshold
                    if analysis['complexity'] < min_complexity:
                        if verbose:
                            logger.info(f"Skipping function below complexity threshold: {analysis['name']} (complexity: {analysis['complexity']})")
                        continue
                    
                    # Only document functions without docstrings
                    if not analysis['docstring']:
                        functions_to_document.append(analysis)
                        if verbose:
                            logger.info(f"Will document: {analysis['name']} (complexity: {analysis['complexity']}, category: {analysis['category']})")
            
            # Sort by line number in reverse order
            functions_to_document.sort(key=lambda x: x['line_number'], reverse=True)
            
            # Add docstrings
            for func_analysis in functions_to_document:
                docstring = self.docstring_generator.generate_docstring(func_analysis)
                
                # Find the line after the function definition
                func_line = func_analysis['line_number'] - 1  # Convert to 0-based
                
                # Find the first line of the function body
                insert_line = func_line + 1
                while insert_line < len(lines) and lines[insert_line].strip() == '':
                    insert_line += 1
                
                # Insert the docstring
                indent = self._get_function_indent(lines, func_line)
                docstring_lines = docstring.split('\n')
                formatted_docstring = []
                
                for i, line in enumerate(docstring_lines):
                    if i == 0:
                        formatted_docstring.append(f"{indent}\"\"\"{line}")
                    elif i == len(docstring_lines) - 1:
                        formatted_docstring.append(f"{indent}{line}\"\"\"")
                    else:
                        formatted_docstring.append(f"{indent}{line}")
                
                # Insert the formatted docstring
                for i, doc_line in enumerate(formatted_docstring):
                    lines.insert(insert_line + i, doc_line)
                
                self.stats['functions_documented'] += 1
                logger.info(f"Added docstring to {func_analysis['name']} in {file_path}")
            
            if not dry_run and functions_to_document:
                # Write the updated content back to the file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                logger.info(f"Updated {file_path} with {len(functions_to_document)} new docstrings")
                return True
            
        except Exception as e:
            logger.error(f"Error adding documentation to {file_path}: {e}")
            return False
        
        return len(functions_to_document) > 0
    
    def _get_function_indent(self, lines: List[str], func_line: int) -> str:
        """Get the indentation level of a function"""
        func_def_line = lines[func_line]
        indent = ''
        for char in func_def_line:
            if char in [' ', '\t']:
                indent += char
            else:
                break
        return indent + '    '  # Add one level of indentation for docstring
    
    def generate_documentation_report(self) -> str:
        """Generate a comprehensive documentation report"""
        undocumented = self.scan_undocumented_functions()
        
        report = []
        report.append("# MinhOS Documentation Coverage Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary statistics
        total_files = len(undocumented)
        total_functions = sum(len(functions) for functions in undocumented.values())
        
        report.append("## Summary")
        report.append(f"- Files needing documentation: {total_files}")
        report.append(f"- Functions needing documentation: {total_functions}")
        report.append("")
        
        # Priority modules
        report.append("## Priority Modules (Critical Trading Components)")
        for module_path in self.priority_modules:
            if module_path in undocumented:
                functions = undocumented[module_path]
                report.append(f"### {module_path}")
                report.append(f"**{len(functions)} functions need documentation**")
                
                # Categorize functions by importance
                critical_functions = [f for f in functions if f['category'] in ['trading', 'risk', 'ai']]
                if critical_functions:
                    report.append("**Critical Functions:**")
                    for func in critical_functions:
                        report.append(f"- `{func['name']}` (line {func['line_number']}) - {func['category']}")
                
                report.append("")
        
        # Other modules
        other_modules = {k: v for k, v in undocumented.items() if k not in self.priority_modules}
        if other_modules:
            report.append("## Other Modules")
            for module_path, functions in other_modules.items():
                report.append(f"### {module_path}")
                report.append(f"**{len(functions)} functions need documentation**")
                
                # Show most complex functions first
                functions.sort(key=lambda x: x['complexity'], reverse=True)
                for func in functions[:5]:  # Show top 5 most complex
                    report.append(f"- `{func['name']}` (complexity: {func['complexity']}, category: {func['category']})")
                
                if len(functions) > 5:
                    report.append(f"- ... and {len(functions) - 5} more functions")
                
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("1. **Start with Priority Modules**: Focus on trading, risk, and AI modules first")
        report.append("2. **Document Critical Functions**: Prioritize functions with 'trading', 'risk', or 'ai' categories")
        report.append("3. **Complex Functions**: Functions with complexity > 5 should be documented and potentially refactored")
        report.append("4. **Run Documentation Generator**: Use `python tools/add_documentation.py --auto` to generate docstrings")
        report.append("")
        
        # Usage instructions
        report.append("## Usage Instructions")
        report.append("```bash")
        report.append("# Generate documentation for all priority modules")
        report.append("python tools/add_documentation.py --priority")
        report.append("")
        report.append("# Generate documentation for specific file")
        report.append("python tools/add_documentation.py --file services/trading_copilot.py")
        report.append("")
        report.append("# Dry run to preview changes")
        report.append("python tools/add_documentation.py --dry-run --priority")
        report.append("```")
        
        return "\n".join(report)
    
    def document_priority_modules(self, dry_run: bool = False, min_complexity: int = 0, verbose: bool = False) -> None:
        """Document all priority modules"""
        logger.info("Starting documentation of priority modules...")
        
        for module_path in self.priority_modules:
            full_path = self.root_path / module_path
            if full_path.exists():
                logger.info(f"Processing {module_path}...")
                success = self.add_documentation(
                    module_path, 
                    dry_run=dry_run,
                    min_complexity=min_complexity,
                    verbose=verbose
                )
                if success:
                    logger.info(f"Successfully documented {module_path}")
                else:
                    logger.info(f"No documentation needed for {module_path}")
            else:
                logger.warning(f"Priority module not found: {module_path}")
        
        logger.info("Priority module documentation complete!")
        logger.info(f"Statistics: {self.stats}")


def main():
    """Main function for the documentation generator"""
    parser = argparse.ArgumentParser(
        description="MinhOS Documentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--root', type=str, default='.',
                       help='Root directory of the project')
    parser.add_argument('--file', type=str,
                       help='Document a specific file')
    parser.add_argument('--priority', action='store_true',
                       help='Document priority modules only')
    parser.add_argument('--report', action='store_true',
                       help='Generate documentation coverage report')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')
    parser.add_argument('--min-complexity', type=int, default=0,
                       help='Minimum complexity threshold for documentation (default: 0)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    # Initialize the documentation generator
    doc_gen = MinhOSDocumentationGenerator(args.root)
    
    if args.report:
        # Generate documentation report
        report = doc_gen.generate_documentation_report()
        
        # Save report to file
        report_file = Path(args.root) / "docs" / "DOCUMENTATION_COVERAGE.md"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Documentation coverage report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("DOCUMENTATION COVERAGE SUMMARY")
        print("="*60)
        print(report.split("## Summary")[1].split("## Priority Modules")[0])
        
    elif args.file:
        # Document specific file
        success = doc_gen.add_documentation(
            args.file, 
            dry_run=args.dry_run,
            min_complexity=args.min_complexity,
            verbose=args.verbose
        )
        if success:
            print(f"Successfully documented {args.file}")
        else:
            print(f"No documentation needed for {args.file}")
    
    elif args.priority:
        # Document priority modules
        doc_gen.document_priority_modules(
            dry_run=args.dry_run,
            min_complexity=args.min_complexity,
            verbose=args.verbose
        )
    
    else:
        # Show help and generate report
        parser.print_help()
        print("\nGenerating documentation coverage report...")
        report = doc_gen.generate_documentation_report()
        print(report.split("## Summary")[1].split("## Priority Modules")[0])


if __name__ == "__main__":
    main()