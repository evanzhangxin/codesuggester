#!/usr/bin/env python3
"""
Performance and stress tests for the Code Suggester.

This module contains tests to evaluate the performance and scalability
of the code suggester with large files and complex code structures.
"""

import unittest
import tempfile
import os
import sys
import time
from io import StringIO

# Add the parent directory to the path to import code_suggester
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_suggester import CodeSuggester, ASTAnalyzer


class TestPerformance(unittest.TestCase):
    """Performance tests for code suggester."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.suggester = CodeSuggester(context_window=4096)
    
    def generate_large_code(self, num_classes=10, num_methods_per_class=10) -> str:
        """Generate large Python code for testing."""
        code_lines = [
            "import os",
            "import sys", 
            "import json",
            "import collections",
            "from typing import List, Dict, Optional, Union",
            "",
        ]
        
        for class_idx in range(num_classes):
            code_lines.append(f"class TestClass{class_idx}:")
            code_lines.append(f'    """Test class {class_idx} for performance testing."""')
            code_lines.append("")
            code_lines.append("    def __init__(self):")
            code_lines.append(f"        self.class_id = {class_idx}")
            code_lines.append("        self.data = {}")
            code_lines.append("")
            
            for method_idx in range(num_methods_per_class):
                code_lines.append(f"    def method_{method_idx}(self, param1, param2=None):")
                code_lines.append(f'        """Method {method_idx} implementation."""')
                code_lines.append(f"        result = param1 + {method_idx}")
                code_lines.append("        if param2:")
                code_lines.append("            result += param2")
                code_lines.append("        self.data[f'method_{method_idx}'] = result")
                code_lines.append("        return result")
                code_lines.append("")
            
            code_lines.append("")
        
        # Add some functions
        for func_idx in range(5):
            code_lines.append(f"def global_function_{func_idx}(arg1, arg2, *args, **kwargs):")
            code_lines.append(f'    """Global function {func_idx}."""')
            code_lines.append(f"    return arg1 + arg2 + {func_idx}")
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def test_large_file_analysis(self):
        """Test AST analysis performance with large files."""
        # Generate large code
        large_code = self.generate_large_code(50, 20)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(large_code)
        temp_file.close()
        
        try:
            # Time the analysis
            start_time = time.time()
            analyzer = self.suggester.analyze_file(temp_file.name)
            structure = analyzer.extract_structure()
            analysis_time = time.time() - start_time
            
            # Verify results
            self.assertEqual(len(structure['classes']), 50)
            self.assertTrue(len(structure['functions']) > 100)  # Methods + global functions
            
            # Performance assertion (should complete in reasonable time)
            self.assertLess(analysis_time, 5.0, f"Analysis took {analysis_time:.2f}s, expected < 5s")
            
            print(f"Large file analysis completed in {analysis_time:.3f}s")
            print(f"Analyzed {len(structure['classes'])} classes and {len(structure['functions'])} functions")
            
        finally:
            os.unlink(temp_file.name)
    
    def test_suggestion_performance(self):
        """Test suggestion generation performance."""
        # Generate medium-sized code
        code = self.generate_large_code(10, 10)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            # Test multiple suggestions to get average performance
            times = []
            for i in range(10):
                start_time = time.time()
                result = self.suggester.get_suggestion(temp_file.name, 20 + i, 10)
                suggestion_time = time.time() - start_time
                times.append(suggestion_time)
                
                # Verify result structure
                self.assertIn('suggestion', result)
                self.assertIn('context', result)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            # Performance assertions
            self.assertLess(avg_time, 1.0, f"Average suggestion time {avg_time:.3f}s, expected < 1s")
            self.assertLess(max_time, 2.0, f"Max suggestion time {max_time:.3f}s, expected < 2s")
            
            print(f"Average suggestion time: {avg_time:.3f}s")
            print(f"Max suggestion time: {max_time:.3f}s")
            
        finally:
            os.unlink(temp_file.name)
    
    def test_context_window_limits(self):
        """Test behavior with different context window sizes."""
        code = self.generate_large_code(20, 15)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            # Test with various context window sizes
            window_sizes = [500, 1000, 2000, 4000, 8000]
            
            for window_size in window_sizes:
                start_time = time.time()
                result = self.suggester.get_suggestion(
                    temp_file.name, 50, 10, context_window=window_size
                )
                elapsed_time = time.time() - start_time
                
                self.assertIn('suggestion', result)
                self.assertLessEqual(result['prompt_length'], window_size)
                
                if result['truncated']:
                    self.assertIn('warning', result)
                
                print(f"Window size {window_size}: {elapsed_time:.3f}s, "
                      f"prompt length: {result['prompt_length']}, "
                      f"truncated: {result['truncated']}")
        
        finally:
            os.unlink(temp_file.name)
    
    def test_memory_usage(self):
        """Test memory usage with large files."""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate very large code
        large_code = self.generate_large_code(100, 30)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(large_code)
        temp_file.close()
        
        try:
            # Analyze large file
            analyzer = self.suggester.analyze_file(temp_file.name)
            structure = analyzer.extract_structure()
            
            # Get memory after analysis
            after_analysis_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate multiple suggestions
            for i in range(20):
                result = self.suggester.get_suggestion(temp_file.name, 100 + i, 10)
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_increase = final_memory - initial_memory
            
            print(f"Initial memory: {initial_memory:.1f} MB")
            print(f"After analysis: {after_analysis_memory:.1f} MB")
            print(f"Final memory: {final_memory:.1f} MB")
            print(f"Total increase: {memory_increase:.1f} MB")
            
            # Memory usage shouldn't grow excessively
            self.assertLess(memory_increase, 200, 
                           f"Memory usage increased by {memory_increase:.1f}MB, expected < 200MB")
            
        finally:
            os.unlink(temp_file.name)
            gc.collect()
    
    def test_concurrent_suggestions(self):
        """Test behavior with concurrent suggestion requests."""
        import threading
        import queue
        
        code = self.generate_large_code(15, 10)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            results_queue = queue.Queue()
            errors_queue = queue.Queue()
            
            def worker(thread_id):
                """Worker function for concurrent testing."""
                try:
                    suggester = CodeSuggester()  # Each thread gets its own instance
                    for i in range(5):
                        result = suggester.get_suggestion(
                            temp_file.name, 
                            10 + thread_id + i, 
                            5 + i
                        )
                        results_queue.put((thread_id, i, result))
                except Exception as e:
                    errors_queue.put((thread_id, str(e)))
            
            # Start multiple threads
            threads = []
            num_threads = 4
            
            start_time = time.time()
            
            for thread_id in range(num_threads):
                thread = threading.Thread(target=worker, args=(thread_id,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # Check results
            total_results = results_queue.qsize()
            total_errors = errors_queue.qsize()
            
            print(f"Concurrent test completed in {total_time:.3f}s")
            print(f"Total results: {total_results}")
            print(f"Total errors: {total_errors}")
            
            # Verify we got expected number of results
            self.assertEqual(total_results, num_threads * 5)
            self.assertEqual(total_errors, 0)
            
            # Performance check
            self.assertLess(total_time, 10.0, 
                           f"Concurrent test took {total_time:.3f}s, expected < 10s")
            
        finally:
            os.unlink(temp_file.name)


class TestStressConditions(unittest.TestCase):
    """Stress tests for edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.suggester = CodeSuggester()
    
    def test_malformed_python_files(self):
        """Test handling of malformed Python files."""
        malformed_codes = [
            "def incomplete_function(",
            "class IncompleteClass",
            "if True\n    print('missing colon')",
            "def func():\n    return\n    # orphaned code",
            "import )\n# syntax error",
        ]
        
        for idx, code in enumerate(malformed_codes):
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file.write(code)
            temp_file.close()
            
            try:
                # Should not crash, even with malformed code
                result = self.suggester.get_suggestion(temp_file.name, 1, 0)
                self.assertIn('suggestion', result)
                
                # Analyze the structure
                analyzer = self.suggester.analyze_file(temp_file.name)
                structure = analyzer.extract_structure()
                
                # Should handle gracefully
                if 'error' in structure:
                    print(f"Malformed code {idx}: {structure['error']}")
                else:
                    print(f"Malformed code {idx}: Parsed successfully")
                    
            finally:
                os.unlink(temp_file.name)
    
    def test_extremely_long_lines(self):
        """Test handling of extremely long lines."""
        # Create code with very long lines
        long_line = "x = " + " + ".join([f"var_{i}" for i in range(1000)])
        code = f"# Very long line test\n{long_line}\nprint('done')"
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            result = self.suggester.get_suggestion(temp_file.name, 2, 100)
            self.assertIn('suggestion', result)
            
            # Should handle long lines without issues
            self.assertIsInstance(result['context']['current_line'], str)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_deeply_nested_code(self):
        """Test handling of deeply nested code structures."""
        # Create deeply nested code
        nested_code = []
        nested_code.append("def outer_function():")
        
        indent = "    "
        for i in range(20):
            nested_code.append(f"{indent * (i + 1)}if condition_{i}:")
        
        nested_code.append(f"{indent * 21}return 'deeply_nested'")
        
        code = "\n".join(nested_code)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            result = self.suggester.get_suggestion(temp_file.name, 15, 10)
            self.assertIn('suggestion', result)
            
            # Should handle deep nesting
            analyzer = self.suggester.analyze_file(temp_file.name)
            structure = analyzer.extract_structure()
            self.assertTrue(len(structure['functions']) >= 1)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        unicode_code = '''
# -*- coding: utf-8 -*-
"""
Unicode test: αβγδε 中文测试 🚀🎉
"""

class UnicodeClass:
    """Class with unicode: Ωψφ"""
    
    def __init__(self):
        self.message = "Hello 世界! 🌍"
        self.greek = "αβγδε"
    
    def unicode_method(self, param="默认值"):
        """Method with unicode parameter"""
        return f"Processed: {param} ✨"

# Variables with unicode names
变量名 = "unicode variable name"
αβγ = 123
'''
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
        temp_file.write(unicode_code)
        temp_file.close()
        
        try:
            result = self.suggester.get_suggestion(temp_file.name, 10, 5)
            self.assertIn('suggestion', result)
            
            # Should handle unicode properly
            analyzer = self.suggester.analyze_file(temp_file.name)
            structure = analyzer.extract_structure()
            
            class_names = [cls['name'] for cls in structure['classes']]
            self.assertIn('UnicodeClass', class_names)
            
        finally:
            os.unlink(temp_file.name)


if __name__ == '__main__':
    # Set up test suite
    suite = unittest.TestSuite()
    
    # Add performance tests
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPerformance))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestStressConditions))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "="*50)
    print("PERFORMANCE TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)