#!/usr/bin/env python3
"""
E2E Demo Script - Interactive demonstration of code suggester functionality
using sample files from the sample_files directory.

This script provides a comprehensive demonstration of how to test the code suggester
in real-world scenarios similar to IDE usage.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Tuple

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_suggester import CodeSuggester, MockLLMProvider


class E2EDemo:
    """End-to-End demonstration of code suggester functionality."""
    
    def __init__(self):
        self.suggester = CodeSuggester()
        self.sample_files_dir = Path(__file__).parent.parent / "sample_files"
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{'-'*40}")
        print(f" {title}")
        print(f"{'-'*40}")
    
    def demo_file_analysis(self, file_path: str, file_name: str):
        """Demonstrate file analysis capabilities."""
        self.print_section(f"Analyzing {file_name}")
        
        try:
            analyzer = self.suggester.analyze_file(file_path)
            structure = analyzer.extract_structure()
            
            print(f"📁 File: {file_name}")
            print(f"📊 Classes found: {len(structure['classes'])}")
            print(f"🔧 Functions found: {len(structure['functions'])}")
            print(f"📦 Imports found: {len(structure['imports'])}")
            print(f"🔢 Variables found: {len(structure['variables'])}")
            
            # Show classes
            if structure['classes']:
                print(f"\n📋 Classes:")
                for cls in structure['classes'][:3]:  # Show first 3
                    print(f"  • {cls['name']} (line {cls['lineno']}) - {len(cls['methods'])} methods")
            
            # Show functions
            if structure['functions']:
                print(f"\n🔧 Functions:")
                for func in structure['functions'][:5]:  # Show first 5
                    args_str = ', '.join(func['args'][:3])  # Show first 3 args
                    if len(func['args']) > 3:
                        args_str += '...'
                    print(f"  • {func['name']}({args_str}) (line {func['lineno']})") 
            
            # Show imports
            if structure['imports']:
                print(f"\n📦 Imports:")
                for imp in structure['imports'][:5]:  # Show first 5
                    if imp['type'] == 'import':
                        print(f"  • import {imp['name']}")
                    else:
                        print(f"  • from {imp['module']} import {imp['name']}")
                        
        except Exception as e:
            print(f"❌ Error analyzing {file_name}: {e}")
    
    def demo_suggestions(self, file_path: str, file_name: str, test_positions: List[Tuple[int, int, str]]):
        """Demonstrate code suggestions at various positions."""
        self.print_section(f"Testing Suggestions in {file_name}")
        
        for line, column, description in test_positions:
            print(f"\n🎯 Test: {description}")
            print(f"   Position: Line {line}, Column {column}")
            
            try:
                result = self.suggester.get_suggestion(file_path, line, column)
                
                suggestion = result['suggestion'].strip()
                if len(suggestion) > 100:
                    suggestion = suggestion[:100] + "..."
                
                print(f"   💡 Suggestion: {repr(suggestion)}")
                print(f"   📏 Prompt length: {result['prompt_length']}/{result['context_window']}")
                
                if result.get('truncated'):
                    print(f"   ⚠️  Context was truncated")
                    
                # Show relevant context info
                context = result['context']
                print(f"   🔍 Context: {len(context['context_before'])} chars before, {len(context['context_after'])} chars after")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demo_cli_integration(self, file_path: str, file_name: str):
        """Demonstrate CLI integration."""
        self.print_section(f"CLI Integration Test - {file_name}")
        
        import subprocess
        
        test_cases = [
            (10, 0, "text", "Basic text output"),
            (20, 10, "json", "JSON output format"),
        ]
        
        for line, column, output_format, description in test_cases:
            print(f"\n🖥️  {description}")
            print(f"   Command: python code_suggester.py {file_name} {line} {column} --output-format {output_format}")
            
            try:
                cmd = [
                    sys.executable, "code_suggester.py",
                    file_path, str(line), str(column),
                    "--output-format", output_format
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      cwd=os.path.dirname(os.path.dirname(__file__)), timeout=10)
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output_format == "json":
                        try:
                            json_data = json.loads(output)
                            print(f"   ✅ JSON Output: Valid ({len(output)} chars)")
                            print(f"   📋 Keys: {list(json_data.keys())}")
                        except json.JSONDecodeError:
                            print(f"   ❌ Invalid JSON output")
                    else:
                        print(f"   ✅ Text Output: {len(output)} chars")
                        if "Suggestion:" in output:
                            print(f"   📝 Contains suggestion content")
                else:
                    print(f"   ❌ CLI failed with return code {result.returncode}")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                        
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Command timed out")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demo_performance(self, file_path: str, file_name: str):
        """Demonstrate performance characteristics."""
        self.print_section(f"Performance Test - {file_name}")
        
        import time
        
        # Test multiple suggestions
        test_positions = [(10, 0), (20, 5), (30, 10), (40, 15), (50, 0)]
        
        print(f"🏃 Testing {len(test_positions)} suggestions...")
        
        start_time = time.time()
        successful_suggestions = 0
        
        for i, (line, column) in enumerate(test_positions, 1):
            try:
                result = self.suggester.get_suggestion(file_path, line, column)
                if 'suggestion' in result:
                    successful_suggestions += 1
                print(f"   Test {i}/5: ✅ {time.time() - start_time:.3f}s")
            except Exception as e:
                print(f"   Test {i}/5: ❌ {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(test_positions)
        
        print(f"\n📊 Performance Summary:")
        print(f"   ⏱️  Total time: {total_time:.3f}s")
        print(f"   ⚡ Avg per suggestion: {avg_time:.3f}s")
        print(f"   ✅ Success rate: {successful_suggestions}/{len(test_positions)} ({successful_suggestions/len(test_positions)*100:.1f}%)")
    
    def run_complete_demo(self):
        """Run the complete E2E demonstration."""
        self.print_header("🚀 Code Suggester E2E Demo")
        
        print("This demo showcases the code suggester functionality using sample files.")
        print("It demonstrates real-world usage scenarios similar to IDE integration.")
        
        # Check sample files
        simple_file = self.sample_files_dir / "simple_example.py"
        complex_file = self.sample_files_dir / "complex_example.py"
        
        if not simple_file.exists() or not complex_file.exists():
            print(f"❌ Sample files not found in {self.sample_files_dir}")
            return
        
        # Demo with simple file
        self.print_header("📝 Simple Example Demonstration")
        self.demo_file_analysis(str(simple_file), "simple_example.py")
        
        simple_test_positions = [
            (10, 0, "Empty line completion"),
            (20, 15, "Inside method body"),
            (62, 4, "After object creation"),
            (65, 20, "Method call position"),
        ]
        self.demo_suggestions(str(simple_file), "simple_example.py", simple_test_positions)
        self.demo_cli_integration(str(simple_file), "simple_example.py")
        self.demo_performance(str(simple_file), "simple_example.py")
        
        # Demo with complex file
        self.print_header("🧩 Complex Example Demonstration")
        self.demo_file_analysis(str(complex_file), "complex_example.py")
        
        complex_test_positions = [
            (50, 10, "Inside dataclass"),
            (100, 5, "Decorator area"),
            (150, 20, "Async method body"),
            (200, 0, "Complex class context"),
        ]
        self.demo_suggestions(str(complex_file), "complex_example.py", complex_test_positions)
        self.demo_cli_integration(str(complex_file), "complex_example.py")
        self.demo_performance(str(complex_file), "complex_example.py")
        
        # Context window demo
        self.print_header("🔧 Context Window Testing")
        self.demo_context_windows(str(complex_file))
        
        # Summary
        self.print_header("📋 Demo Summary")
        print("✅ File analysis: Structure extraction from Python files")
        print("✅ Code suggestions: Context-aware completion suggestions")
        print("✅ CLI integration: Command-line interface testing")
        print("✅ Performance: Speed and efficiency measurements")
        print("✅ Context management: Window size and truncation handling")
        print("\n🎉 E2E Demo completed successfully!")
        print("\nNext steps:")
        print("• Run unit tests: python test_code_suggester.py")
        print("• Run E2E tests: python test_e2e.py")
        print("• Try CLI manually: python code_suggester.py <file> <line> <column>")
    
    def demo_context_windows(self, file_path: str):
        """Demonstrate context window behavior."""
        print("🔧 Testing different context window sizes...")
        
        window_sizes = [500, 1000, 2000, 4000, 8000]
        
        for window_size in window_sizes:
            try:
                result = self.suggester.get_suggestion(file_path, 100, 10, window_size)
                truncated = "Yes" if result.get('truncated') else "No"
                print(f"   Window {window_size:4d}: Prompt {result['prompt_length']:4d} chars, Truncated: {truncated}")
            except Exception as e:
                print(f"   Window {window_size:4d}: ❌ Error: {e}")


def main():
    """Main entry point for the E2E demo."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Usage: python demo_e2e.py")
        print("Run a comprehensive end-to-end demonstration of the code suggester.")
        return
    
    demo = E2EDemo()
    try:
        demo.run_complete_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()