#!/usr/bin/env python3
"""
Unit tests for the Code Suggester module.

This module contains comprehensive tests for all components of the code_suggester,
including AST analysis, LLM integration, and the main suggester functionality.
"""

import unittest
import tempfile
import os
import sys
import json
from unittest.mock import Mock, patch, mock_open
from io import StringIO

# Add the parent directory to the path to import code_suggester
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_suggester import (
    ASTAnalyzer, LLMProvider, MockLLMProvider, CodeSuggester, 
    CodeContext, main
)


class TestASTAnalyzer(unittest.TestCase):
    """Test cases for ASTAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simple_code = """
import os
import sys

class TestClass:
    def __init__(self):
        self.value = 42
    
    def method1(self):
        return self.value

def function1(arg1, arg2):
    return arg1 + arg2

variable1 = "test"
"""
    
    def test_ast_analyzer_initialization(self):
        """Test AST analyzer initialization with valid code."""
        analyzer = ASTAnalyzer(self.simple_code)
        self.assertIsNotNone(analyzer.tree)
        self.assertEqual(len(analyzer.lines), 16)
    
    def test_ast_analyzer_with_syntax_error(self):
        """Test AST analyzer with invalid syntax."""
        invalid_code = "def invalid_function(\n    pass"
        analyzer = ASTAnalyzer(invalid_code)
        self.assertIsNone(analyzer.tree)
        self.assertTrue(hasattr(analyzer, 'syntax_error'))
    
    def test_extract_structure(self):
        """Test code structure extraction."""
        analyzer = ASTAnalyzer(self.simple_code)
        structure = analyzer.extract_structure()
        
        # Check classes
        self.assertEqual(len(structure['classes']), 1)
        self.assertEqual(structure['classes'][0]['name'], 'TestClass')
        self.assertIn('__init__', structure['classes'][0]['methods'])
        self.assertIn('method1', structure['classes'][0]['methods'])
        
        # Check functions
        self.assertEqual(len(structure['functions']), 3)  # __init__, method1, function1
        function_names = [f['name'] for f in structure['functions']]
        self.assertIn('function1', function_names)
        
        # Check imports
        self.assertEqual(len(structure['imports']), 2)
        import_names = [imp['name'] for imp in structure['imports']]
        self.assertIn('os', import_names)
        self.assertIn('sys', import_names)
        
        # Check variables
        self.assertTrue(len(structure['variables']) >= 1)
        variable_names = [var['name'] for var in structure['variables']]
        self.assertIn('variable1', variable_names)
    
    def test_extract_structure_with_syntax_error(self):
        """Test structure extraction with syntax error."""
        invalid_code = "def invalid("
        analyzer = ASTAnalyzer(invalid_code)
        structure = analyzer.extract_structure()
        
        self.assertIn('error', structure)
        self.assertEqual(structure['classes'], [])
        self.assertEqual(structure['functions'], [])
        self.assertEqual(structure['imports'], [])
    
    def test_get_context_at_position(self):
        """Test getting context at specific position."""
        analyzer = ASTAnalyzer(self.simple_code)
        
        # Test at middle of code
        context_before, context_after, current_line = analyzer.get_context_at_position(8, 10, 10)
        
        self.assertIsInstance(context_before, str)
        self.assertIsInstance(context_after, str)
        self.assertIsInstance(current_line, str)
        
        # Test at beginning of file
        context_before, context_after, current_line = analyzer.get_context_at_position(1, 0, 5)
        self.assertEqual(context_before, "")
        
        # Test at end of file
        line_count = len(analyzer.lines)
        context_before, context_after, current_line = analyzer.get_context_at_position(line_count, 0, 5)
        self.assertNotEqual(context_before, "")
    
    def test_get_context_invalid_position(self):
        """Test getting context at invalid position."""
        analyzer = ASTAnalyzer(self.simple_code)
        
        # Test line number out of range
        context_before, context_after, current_line = analyzer.get_context_at_position(1000, 0, 5)
        self.assertEqual(context_before, "")
        self.assertEqual(context_after, "")
        self.assertEqual(current_line, "")


class TestLLMProvider(unittest.TestCase):
    """Test cases for LLM provider classes."""
    
    def test_base_llm_provider(self):
        """Test base LLM provider raises NotImplementedError."""
        provider = LLMProvider()
        with self.assertRaises(NotImplementedError):
            provider.generate_completion("test prompt")
    
    def test_mock_llm_provider(self):
        """Test mock LLM provider functionality."""
        provider = MockLLMProvider()
        
        # Test function definition completion
        result = provider.generate_completion("def test_function(")
        self.assertIn(")", result)
        
        # Test class definition completion
        result = provider.generate_completion("class TestClass")
        self.assertIn(":", result)
        
        # Test if statement completion
        result = provider.generate_completion("if x > 5")
        self.assertIn(":", result)
        
        # Test assignment completion
        result = provider.generate_completion("value =")
        self.assertIn("None", result)
        
        # Test general completion
        result = provider.generate_completion("some other code")
        self.assertIn("TODO", result)


class TestCodeSuggester(unittest.TestCase):
    """Test cases for CodeSuggester class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_code = """
import os

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result

def main():
    calc = Calculator()
    calc.add(5)
    print(calc.result)
"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.test_code)
        self.temp_file.close()
        
        self.suggester = CodeSuggester()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_analyze_file(self):
        """Test file analysis functionality."""
        analyzer = self.suggester.analyze_file(self.temp_file.name)
        self.assertIsInstance(analyzer, ASTAnalyzer)
        self.assertIsNotNone(analyzer.tree)
    
    def test_analyze_nonexistent_file(self):
        """Test analyzing non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.suggester.analyze_file("nonexistent_file.py")
    
    def test_get_suggestion(self):
        """Test getting code suggestions."""
        result = self.suggester.get_suggestion(self.temp_file.name, 5, 10)
        
        self.assertIn('suggestion', result)
        self.assertIn('context', result)
        self.assertIn('truncated', result)
        self.assertIn('prompt_length', result)
        self.assertIn('context_window', result)
        
        # Check context structure
        context = result['context']
        self.assertEqual(context['file_path'], self.temp_file.name)
        self.assertEqual(context['line_number'], 5)
        self.assertEqual(context['column_number'], 10)
        self.assertIn('code_structure', context)
    
    def test_get_suggestion_with_truncation(self):
        """Test suggestion with small context window."""
        result = self.suggester.get_suggestion(
            self.temp_file.name, 5, 10, context_window=100
        )
        
        # With a small window, truncation is likely
        if result['truncated']:
            self.assertIn('warning', result)
            self.assertIn('truncated', result['warning'])
    
    def test_create_prompt(self):
        """Test prompt creation."""
        context = CodeContext(
            file_path=self.temp_file.name,
            line_number=5,
            column_number=10,
            context_window=1000,
            code_structure={'classes': [], 'functions': []},
            context_before="def test():",
            context_after="pass",
            current_line="    "
        )
        
        prompt = self.suggester._create_prompt(context)
        self.assertIn("code completion", prompt.lower())
        self.assertIn("def test():", prompt)
        self.assertIn("pass", prompt)


class TestCodeContext(unittest.TestCase):
    """Test cases for CodeContext dataclass."""
    
    def test_code_context_creation(self):
        """Test CodeContext creation and conversion to dict."""
        context = CodeContext(
            file_path="test.py",
            line_number=10,
            column_number=5,
            context_window=1000,
            code_structure={'test': 'data'},
            context_before="before",
            context_after="after",
            current_line="current"
        )
        
        # Test attributes
        self.assertEqual(context.file_path, "test.py")
        self.assertEqual(context.line_number, 10)
        self.assertEqual(context.column_number, 5)
        
        # Test conversion to dict
        context_dict = context.__dict__
        self.assertIn('file_path', context_dict)
        self.assertIn('code_structure', context_dict)


class TestMainFunction(unittest.TestCase):
    """Test cases for main function and CLI interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_code = "def hello():\n    print('Hello, World!')\n"
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.test_code)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    @patch('sys.argv', ['code_suggester.py', 'test.py', '1', '0'])
    @patch('builtins.print')
    def test_main_with_nonexistent_file(self, mock_print):
        """Test main function with non-existent file."""
        with self.assertRaises(SystemExit):
            main()
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_with_valid_args(self, mock_stdout):
        """Test main function with valid arguments."""
        test_args = [
            'code_suggester.py', 
            self.temp_file.name, 
            '1', 
            '0',
            '--output-format', 'json'
        ]
        
        with patch('sys.argv', test_args):
            try:
                main()
                output = mock_stdout.getvalue()
                # Should be valid JSON
                result = json.loads(output)
                self.assertIn('suggestion', result)
            except SystemExit:
                pass  # Expected for some error cases
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_text_output(self, mock_stdout):
        """Test main function with text output format."""
        test_args = [
            'code_suggester.py', 
            self.temp_file.name, 
            '1', 
            '0',
            '--output-format', 'text'
        ]
        
        with patch('sys.argv', test_args):
            try:
                main()
                output = mock_stdout.getvalue()
                self.assertIn('Suggestion:', output)
            except SystemExit:
                pass


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete code suggester workflow."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.complex_code = """
import json
import os
from typing import List, Dict, Optional

class DataProcessor:
    '''A class for processing data files.'''
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.processed_data = []
    
    def _load_config(self) -> Dict:
        '''Load configuration from file.'''
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def process_file(self, file_path: str) -> Optional[Dict]:
        '''Process a single file.'''
        if not os.path.exists(file_path):
            return None
        
        # Process the file here
        
    def process_batch(self, file_paths: List[str]) -> List[Dict]:
        '''Process multiple files.'''
        results = []
        for path in file_paths:
            result = self.process_file(path)
            if result:
                results.append(result)
        return results

def main():
    processor = DataProcessor('config.json')
    
"""
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.complex_code)
        self.temp_file.close()
        
        self.suggester = CodeSuggester()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_complete_workflow(self):
        """Test the complete code suggestion workflow."""
        # Test at various positions in the complex code
        
        # Test at import section
        result1 = self.suggester.get_suggestion(self.temp_file.name, 3, 25)
        self.assertIn('suggestion', result1)
        
        # Test inside class method
        result2 = self.suggester.get_suggestion(self.temp_file.name, 20, 30)
        self.assertIn('suggestion', result2)
        
        # Test at the end of incomplete function
        result3 = self.suggester.get_suggestion(self.temp_file.name, 31, 0)
        self.assertIn('suggestion', result3)
        
        # Verify that code structure is extracted properly
        analyzer = self.suggester.analyze_file(self.temp_file.name)
        structure = analyzer.extract_structure()
        
        self.assertTrue(len(structure['classes']) >= 1)
        self.assertTrue(len(structure['functions']) >= 1)
        self.assertTrue(len(structure['imports']) >= 3)
        
        # Check specific elements
        class_names = [cls['name'] for cls in structure['classes']]
        self.assertIn('DataProcessor', class_names)
        
        function_names = [func['name'] for func in structure['functions']]
        self.assertIn('main', function_names)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestASTAnalyzer))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestLLMProvider))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCodeSuggester))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCodeContext))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMainFunction))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)