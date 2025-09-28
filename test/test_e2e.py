#!/usr/bin/env python3
"""
End-to-End (E2E) tests for the Code Suggester using sample files.

This module provides comprehensive E2E testing scenarios including:
- Code suggestion accuracy validation
- Real-world code completion scenarios
- IDE-like interaction testing
- Parser behavior validation on different code constructs
"""

import unittest
import json
import os
import sys
import subprocess
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add the parent directory to the path to import code_suggester
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_suggester import CodeSuggester, MockLLMProvider


class E2ETestScenario:
    """Represents an E2E test scenario."""
    
    def __init__(self, name: str, file_path: str, line: int, column: int, 
                 expected_elements: List[str], description: str):
        self.name = name
        self.file_path = file_path
        self.line = line
        self.column = column
        self.expected_elements = expected_elements
        self.description = description


class TestE2ECodeSuggestion(unittest.TestCase):
    """End-to-end tests using sample files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.suggester = CodeSuggester()
        self.sample_files_dir = Path(__file__).parent.parent / "sample_files"
        
        # Verify sample files exist
        self.simple_file = self.sample_files_dir / "simple_example.py"
        self.complex_file = self.sample_files_dir / "complex_example.py"
        
        self.assertTrue(self.simple_file.exists(), f"Simple example file not found: {self.simple_file}")
        self.assertTrue(self.complex_file.exists(), f"Complex example file not found: {self.complex_file}")
    
    def test_simple_file_structure_extraction(self):
        """Test structure extraction from simple example file."""
        analyzer = self.suggester.analyze_file(str(self.simple_file))
        structure = analyzer.extract_structure()
        
        # Verify classes
        self.assertGreaterEqual(len(structure['classes']), 1)
        class_names = [cls['name'] for cls in structure['classes']]
        self.assertIn('Calculator', class_names)
        
        # Verify methods in Calculator class
        calculator_class = next(cls for cls in structure['classes'] if cls['name'] == 'Calculator')
        expected_methods = ['__init__', 'add', 'subtract', 'multiply', 'divide', 'clear', 'get_history']
        for method in expected_methods:
            self.assertIn(method, calculator_class['methods'], f"Method {method} not found in Calculator")
        
        # Verify functions
        function_names = [func['name'] for func in structure['functions']]
        self.assertIn('create_calculator', function_names)
        self.assertIn('main', function_names)
        
        # Verify imports
        import_names = [imp['name'] for imp in structure['imports']]
        self.assertIn('os', import_names)
        self.assertIn('sys', import_names)
    
    def test_complex_file_structure_extraction(self):
        """Test structure extraction from complex example file."""
        analyzer = self.suggester.analyze_file(str(self.complex_file))
        structure = analyzer.extract_structure()
        
        # Verify classes
        class_names = [cls['name'] for cls in structure['classes']]
        expected_classes = ['Status', 'Task', 'BaseProcessor', 'TaskProcessor']
        for cls_name in expected_classes:
            self.assertIn(cls_name, class_names, f"Class {cls_name} not found")
        
        # Verify functions
        function_names = [func['name'] for func in structure['functions']]
        expected_functions = ['retry', 'database_transaction']
        for func_name in expected_functions:
            self.assertIn(func_name, function_names, f"Function {func_name} not found")
        
        # Verify complex imports
        import_names = [imp['name'] for imp in structure['imports'] if imp['type'] == 'import']
        module_imports = [imp['module'] for imp in structure['imports'] if imp['type'] == 'from_import' and imp['module']]
        
        self.assertIn('asyncio', import_names)
        self.assertIn('typing', module_imports)
        self.assertIn('dataclasses', module_imports)
    
    def test_suggestion_scenarios_simple_file(self):
        """Test various suggestion scenarios with simple file."""
        test_cases = [
            # Test inside class method
            E2ETestScenario(
                "class_method_body",
                str(self.simple_file),
                20, 0,  # Inside add method
                ["suggestion", "context"],
                "Suggestion inside Calculator.add method"
            ),
            
            # Test at end of function
            E2ETestScenario(
                "function_end",
                str(self.simple_file),
                60, 0,  # Inside main function
                ["suggestion", "context"],
                "Suggestion inside main function"
            ),
            
            # Test class method parameter area
            E2ETestScenario(
                "method_parameter",
                str(self.simple_file),
                18, 25,  # In add method parameters
                ["suggestion", "context"],
                "Suggestion in method parameter area"
            ),
        ]
        
        for scenario in test_cases:
            with self.subTest(scenario=scenario.name):
                result = self.suggester.get_suggestion(
                    scenario.file_path, 
                    scenario.line, 
                    scenario.column
                )
                
                # Verify basic structure
                for element in scenario.expected_elements:
                    self.assertIn(element, result, f"Missing {element} in {scenario.name}")
                
                # Verify context contains relevant information
                context = result['context']
                self.assertEqual(context['file_path'], scenario.file_path)
                self.assertEqual(context['line_number'], scenario.line)
                self.assertEqual(context['column_number'], scenario.column)
                
                # Verify code structure was extracted
                self.assertIn('code_structure', context)
                self.assertIn('classes', context['code_structure'])
    
    def test_suggestion_scenarios_complex_file(self):
        """Test various suggestion scenarios with complex file."""
        test_cases = [
            # Test inside async method
            E2ETestScenario(
                "async_method",
                str(self.complex_file),
                130, 10,  # Inside async process method
                ["suggestion", "context"],
                "Suggestion inside async process method"
            ),
            
            # Test decorator area
            E2ETestScenario(
                "decorator_area",
                str(self.complex_file),
                85, 0,  # Around retry decorator
                ["suggestion", "context"],
                "Suggestion near decorator definition"
            ),
            
            # Test generic class area
            E2ETestScenario(
                "generic_class",
                str(self.complex_file),
                75, 20,  # Inside BaseProcessor class
                ["suggestion", "context"],
                "Suggestion inside generic base class"
            ),
        ]
        
        for scenario in test_cases:
            with self.subTest(scenario=scenario.name):
                result = self.suggester.get_suggestion(
                    scenario.file_path, 
                    scenario.line, 
                    scenario.column
                )
                
                # Verify basic structure
                for element in scenario.expected_elements:
                    self.assertIn(element, result, f"Missing {element} in {scenario.name}")
                
                # Verify context contains complex constructs
                context = result['context']
                code_structure = context['code_structure']
                
                # Should detect complex classes and imports
                self.assertGreater(len(code_structure['classes']), 2)
                self.assertGreater(len(code_structure['imports']), 5)
    
    def test_cli_integration_simple_file(self):
        """Test CLI integration with simple file."""
        test_positions = [
            (10, 0),   # Empty line
            (20, 15),  # Inside method
            (50, 5),   # Inside function
        ]
        
        for line, column in test_positions:
            with self.subTest(position=(line, column)):
                # Test text output
                result = subprocess.run([
                    sys.executable, "code_suggester.py",
                    str(self.simple_file), str(line), str(column)
                ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                
                self.assertEqual(result.returncode, 0, f"CLI failed at position {line},{column}")
                self.assertIn("Suggestion:", result.stdout)
                self.assertIn("Prompt length:", result.stdout)
                
                # Test JSON output
                result_json = subprocess.run([
                    sys.executable, "code_suggester.py",
                    str(self.simple_file), str(line), str(column),
                    "--output-format", "json"
                ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                
                self.assertEqual(result_json.returncode, 0, f"CLI JSON failed at position {line},{column}")
                
                # Parse and validate JSON
                try:
                    json_data = json.loads(result_json.stdout)
                    self.assertIn("suggestion", json_data)
                    self.assertIn("context", json_data)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON output at position {line},{column}: {e}")
    
    def test_cli_integration_complex_file(self):
        """Test CLI integration with complex file."""
        test_positions = [
            (50, 10),  # Inside dataclass
            (100, 20), # Inside decorator
            (150, 5),  # Inside async method
        ]
        
        for line, column in test_positions:
            with self.subTest(position=(line, column)):
                # Test with different context windows
                for context_window in [500, 1000, 2000]:
                    result = subprocess.run([
                        sys.executable, "code_suggester.py",
                        str(self.complex_file), str(line), str(column),
                        "--context-window", str(context_window),
                        "--output-format", "json"
                    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                    
                    self.assertEqual(result.returncode, 0, 
                                   f"CLI failed at {line},{column} with window {context_window}")
                    
                    # Verify JSON and context window handling
                    try:
                        json_data = json.loads(result.stdout)
                        self.assertEqual(json_data["context"]["context_window"], context_window)
                        self.assertLessEqual(json_data["prompt_length"], context_window)
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON at {line},{column}, window {context_window}: {e}")
    
    def test_context_extraction_accuracy(self):
        """Test accuracy of context extraction at various positions."""
        # Test with simple file
        analyzer = self.suggester.analyze_file(str(self.simple_file))
        
        # Test context at beginning of class
        context_before, context_after, current_line = analyzer.get_context_at_position(12, 0, 10)
        self.assertIn("Calculator", context_after)
        self.assertIn("import", context_before)
        
        # Test context at method definition
        context_before, context_after, current_line = analyzer.get_context_at_position(18, 10, 10)
        self.assertIn("def add", current_line)
        self.assertIn("__init__", context_before)
        
        # Test context extraction with complex file
        analyzer_complex = self.suggester.analyze_file(str(self.complex_file))
        
        # Test context around dataclass
        context_before, context_after, current_line = analyzer_complex.get_context_at_position(45, 0, 15)
        self.assertIn("dataclass", context_before.lower())
        self.assertIn("task", context_after.lower())
    
    def test_performance_with_sample_files(self):
        """Test performance characteristics with sample files."""
        import time
        
        # Test suggestion speed with both files
        files_to_test = [
            (str(self.simple_file), "simple"),
            (str(self.complex_file), "complex")
        ]
        
        for file_path, file_type in files_to_test:
            with self.subTest(file_type=file_type):
                # Test multiple positions
                test_positions = [(10, 0), (20, 10), (30, 5), (40, 15), (50, 0)]
                
                start_time = time.time()
                
                for line, column in test_positions:
                    result = self.suggester.get_suggestion(file_path, line, column)
                    self.assertIn('suggestion', result)
                    self.assertIn('context', result)
                
                end_time = time.time()
                total_time = end_time - start_time
                avg_time_per_suggestion = total_time / len(test_positions)
                
                # Performance assertions
                self.assertLess(avg_time_per_suggestion, 0.1, 
                               f"Suggestion too slow for {file_type} file: {avg_time_per_suggestion:.3f}s")
                
                print(f"{file_type.capitalize()} file - Avg time per suggestion: {avg_time_per_suggestion:.3f}s")
    
    def test_error_handling_scenarios(self):
        """Test error handling with sample files."""
        # Test with invalid positions
        error_cases = [
            # Line out of range
            (str(self.simple_file), 1000, 0, "Line out of range"),
            
            # Negative line
            (str(self.simple_file), -1, 0, "Negative line"),
            
            # Very large column
            (str(self.simple_file), 10, 10000, "Large column"),
        ]
        
        for file_path, line, column, description in error_cases:
            with self.subTest(case=description):
                # Should not crash, should handle gracefully
                result = self.suggester.get_suggestion(file_path, line, column)
                self.assertIn('suggestion', result)
                self.assertIn('context', result)
    
    def test_code_structure_consistency(self):
        """Test that code structure extraction is consistent across multiple calls."""
        for file_path in [str(self.simple_file), str(self.complex_file)]:
            with self.subTest(file=file_path):
                # Get structure multiple times
                structures = []
                for _ in range(3):
                    analyzer = self.suggester.analyze_file(file_path)
                    structure = analyzer.extract_structure()
                    structures.append(structure)
                
                # Verify consistency
                first_structure = structures[0]
                for i, structure in enumerate(structures[1:], 1):
                    self.assertEqual(len(structure['classes']), len(first_structure['classes']),
                                   f"Class count inconsistent in run {i}")
                    self.assertEqual(len(structure['functions']), len(first_structure['functions']),
                                   f"Function count inconsistent in run {i}")
                    self.assertEqual(len(structure['imports']), len(first_structure['imports']),
                                   f"Import count inconsistent in run {i}")


class TestE2ERealWorldScenarios(unittest.TestCase):
    """Test real-world IDE-like scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.suggester = CodeSuggester()
        self.sample_files_dir = Path(__file__).parent.parent / "sample_files"
    
    def test_method_completion_scenario(self):
        """Test method completion like in an IDE."""
        simple_file = self.sample_files_dir / "simple_example.py"
        
        # Simulate typing "calc." and expecting method suggestions
        # Position after "calc = create_calculator()" line
        result = self.suggester.get_suggestion(str(simple_file), 62, 0)
        
        # Verify that code structure includes Calculator methods
        context = result['context']
        code_structure = context['code_structure']
        
        calculator_class = next(
            (cls for cls in code_structure['classes'] if cls['name'] == 'Calculator'), 
            None
        )
        self.assertIsNotNone(calculator_class, "Calculator class not found in structure")
        
        # Should find all Calculator methods
        expected_methods = ['add', 'subtract', 'multiply', 'divide', 'clear', 'get_history']
        if calculator_class is not None:
            for method in expected_methods:
                self.assertIn(method, calculator_class['methods'],
                             f"Method {method} not available for completion")
    
    def test_import_completion_scenario(self):
        """Test import completion scenario."""
        complex_file = self.sample_files_dir / "complex_example.py"
        
        # Test at import section
        result = self.suggester.get_suggestion(str(complex_file), 15, 0)
        
        # Verify imports are properly detected
        context = result['context']
        code_structure = context['code_structure']
        
        # Should detect various import types
        import_modules = set()
        for imp in code_structure['imports']:
            if imp['type'] == 'import':
                import_modules.add(imp['name'])
            elif imp['type'] == 'from_import' and imp['module']:
                import_modules.add(imp['module'])
        
        expected_modules = ['asyncio', 'contextlib', 'functools', 'typing']
        for module in expected_modules:
            self.assertIn(module, import_modules, f"Module {module} not detected in imports")
    
    def test_class_inheritance_scenario(self):
        """Test class inheritance completion scenario."""
        complex_file = self.sample_files_dir / "complex_example.py"
        
        # Test around TaskProcessor class that inherits from BaseProcessor
        result = self.suggester.get_suggestion(str(complex_file), 120, 0)
        
        context = result['context']
        code_structure = context['code_structure']
        
        # Find TaskProcessor class
        task_processor = next(
            (cls for cls in code_structure['classes'] if cls['name'] == 'TaskProcessor'),
            None
        )
        self.assertIsNotNone(task_processor, "TaskProcessor class not found")
        
        # Should detect BaseProcessor as base class
        if task_processor is not None:
            self.assertIn('BaseProcessor', task_processor['bases'],
                         "BaseProcessor inheritance not detected")


if __name__ == '__main__':
    # Create comprehensive test suite
    suite = unittest.TestSuite()
    
    # Add E2E test cases
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestE2ECodeSuggestion))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestE2ERealWorldScenarios))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n" + "="*70)
    print(f"E2E TEST SUMMARY")
    print(f"="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)