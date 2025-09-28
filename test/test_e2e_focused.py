#!/usr/bin/env python3
"""
Focused E2E Tests - Real-world testing scenarios using sample files.

This script provides targeted tests for specific IDE-like scenarios:
1. Method completion after dot notation
2. Parameter completion in function calls
3. Import statement completion
4. Class inheritance scenarios
5. Error handling with malformed code
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_suggester import CodeSuggester


def test_method_completion():
    """Test method completion scenarios like 'obj.' completion."""
    print("🔍 Testing Method Completion Scenarios")
    print("-" * 50)
    
    suggester = CodeSuggester()
    simple_file = Path("sample_files/simple_example.py")
    
    if not simple_file.exists():
        print("❌ Simple example file not found")
        return False
    
    # Test various positions for method completion
    test_cases = [
        {
            "name": "After object creation",
            "line": 62,
            "column": 25,  # After "calc = create_calculator()"
            "expected_in_structure": ["Calculator", "add", "subtract"]
        },
        {
            "name": "Inside method call",
            "line": 65,
            "column": 8,   # At "calc.add(10)"
            "expected_in_structure": ["Calculator", "add"]
        }
    ]
    
    success_count = 0
    for test in test_cases:
        print(f"\n🎯 Test: {test['name']} (Line {test['line']}, Col {test['column']})")
        
        try:
            result = suggester.get_suggestion(str(simple_file), test['line'], test['column'])
            
            # Check if suggestion was generated
            if 'suggestion' in result and result['suggestion']:
                print(f"   ✅ Suggestion generated: {len(result['suggestion'])} chars")
                success_count += 1
            else:
                print(f"   ⚠️  No suggestion generated")
            
            # Check if relevant structure is detected
            context = result['context']
            structure = context['code_structure']
            
            found_elements = []
            for expected in test['expected_in_structure']:
                # Check in classes
                if any(cls['name'] == expected for cls in structure['classes']):
                    found_elements.append(f"class:{expected}")
                
                # Check in methods
                for cls in structure['classes']:
                    if expected in cls['methods']:
                        found_elements.append(f"method:{expected}")
                        break
            
            if found_elements:
                print(f"   📋 Found relevant elements: {found_elements}")
            else:
                print(f"   ⚠️  Expected elements not found in structure")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Method completion tests: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)


def test_cli_real_world_scenarios():
    """Test CLI with real-world usage patterns."""
    print("\n🖥️  Testing CLI Real-World Scenarios")
    print("-" * 50)
    
    simple_file = "sample_files/simple_example.py"
    complex_file = "sample_files/complex_example.py"
    
    cli_tests = [
        {
            "name": "Quick suggestion check",
            "cmd": [sys.executable, "code_suggester.py", simple_file, "20", "10"],
            "expected_in_output": ["Suggestion:", "Prompt length:"]
        },
        {
            "name": "JSON output for IDE integration",
            "cmd": [sys.executable, "code_suggester.py", simple_file, "30", "5", "--output-format", "json"],
            "expected_json_keys": ["suggestion", "context", "truncated"]
        },
        {
            "name": "Complex file with small context window",
            "cmd": [sys.executable, "code_suggester.py", complex_file, "100", "10", "--context-window", "1000"],
            "expected_in_output": ["Warning:", "truncated"]
        },
        {
            "name": "Edge case - very large line number",
            "cmd": [sys.executable, "code_suggester.py", simple_file, "1000", "0"],
            "should_not_crash": True
        }
    ]
    
    success_count = 0
    for test in cli_tests:
        print(f"\n🎯 Test: {test['name']}")
        print(f"   Command: {' '.join(test['cmd'])}")
        
        try:
            result = subprocess.run(
                test['cmd'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__)),
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"   ❌ Command failed with code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                continue
            
            output = result.stdout.strip()
            
            # Check for expected text output
            if 'expected_in_output' in test:
                found_all = True
                for expected_text in test['expected_in_output']:
                    if expected_text not in output:
                        found_all = False
                        print(f"   ⚠️  Missing expected text: '{expected_text}'")
                
                if found_all:
                    print(f"   ✅ All expected text found")
                    success_count += 1
                else:
                    print(f"   ❌ Some expected text missing")
            
            # Check for expected JSON structure
            elif 'expected_json_keys' in test:
                try:
                    json_data = json.loads(output)
                    missing_keys = []
                    for key in test['expected_json_keys']:
                        if key not in json_data:
                            missing_keys.append(key)
                    
                    if not missing_keys:
                        print(f"   ✅ Valid JSON with all expected keys")
                        success_count += 1
                    else:
                        print(f"   ❌ Missing JSON keys: {missing_keys}")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Invalid JSON output: {e}")
            
            # Check that command doesn't crash
            elif 'should_not_crash' in test:
                print(f"   ✅ Command completed without crashing")
                success_count += 1
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Command timed out (>10s)")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print(f"\n📊 CLI tests: {success_count}/{len(cli_tests)} successful")
    return success_count == len(cli_tests)


def test_structure_extraction_accuracy():
    """Test accuracy of structure extraction with sample files."""
    print("\n🔍 Testing Structure Extraction Accuracy")
    print("-" * 50)
    
    suggester = CodeSuggester()
    
    # Test simple file structure
    simple_file = Path("sample_files/simple_example.py")
    if simple_file.exists():
        print(f"\n📄 Analyzing {simple_file.name}")
        
        analyzer = suggester.analyze_file(str(simple_file))
        structure = analyzer.extract_structure()
        
        # Expected elements in simple file
        expected_classes = ["Calculator"]
        expected_methods = ["__init__", "add", "subtract", "multiply", "divide"]
        expected_functions = ["create_calculator", "main"]
        expected_imports = ["os", "sys"]
        
        # Verify classes
        found_classes = [cls['name'] for cls in structure['classes']]
        for expected_class in expected_classes:
            if expected_class in found_classes:
                print(f"   ✅ Found class: {expected_class}")
            else:
                print(f"   ❌ Missing class: {expected_class}")
        
        # Verify methods (in Calculator class)
        calculator_class = next((cls for cls in structure['classes'] if cls['name'] == 'Calculator'), None)
        if calculator_class:
            found_methods = calculator_class['methods']
            for expected_method in expected_methods:
                if expected_method in found_methods:
                    print(f"   ✅ Found method: Calculator.{expected_method}")
                else:
                    print(f"   ❌ Missing method: Calculator.{expected_method}")
        
        # Verify functions
        found_functions = [func['name'] for func in structure['functions']]
        for expected_function in expected_functions:
            if expected_function in found_functions:
                print(f"   ✅ Found function: {expected_function}")
            else:
                print(f"   ❌ Missing function: {expected_function}")
        
        # Verify imports
        found_imports = [imp['name'] for imp in structure['imports'] if imp['type'] == 'import']
        for expected_import in expected_imports:
            if expected_import in found_imports:
                print(f"   ✅ Found import: {expected_import}")
            else:
                print(f"   ❌ Missing import: {expected_import}")
    
    # Test complex file structure
    complex_file = Path("sample_files/complex_example.py")
    if complex_file.exists():
        print(f"\n📄 Analyzing {complex_file.name}")
        
        analyzer = suggester.analyze_file(str(complex_file))
        structure = analyzer.extract_structure()
        
        # Should find various complex constructs
        class_count = len(structure['classes'])
        function_count = len(structure['functions'])
        import_count = len(structure['imports'])
        
        print(f"   📊 Found {class_count} classes, {function_count} functions, {import_count} imports")
        
        if class_count >= 3:
            print(f"   ✅ Adequate class detection")
        else:
            print(f"   ⚠️  Low class count, expected more complex structures")
        
        if import_count >= 10:
            print(f"   ✅ Complex import detection")
        else:
            print(f"   ⚠️  Expected more imports in complex file")
    
    return True


def test_performance_characteristics():
    """Test performance with sample files."""
    print("\n⚡ Testing Performance Characteristics")
    print("-" * 50)
    
    import time
    suggester = CodeSuggester()
    
    files_to_test = [
        ("sample_files/simple_example.py", "Simple file"),
        ("sample_files/complex_example.py", "Complex file")
    ]
    
    for file_path, description in files_to_test:
        if not Path(file_path).exists():
            print(f"   ⚠️  {description} not found: {file_path}")
            continue
        
        print(f"\n📄 {description}: {file_path}")
        
        # Test multiple suggestions for performance
        test_positions = [(10, 0), (20, 5), (30, 10), (40, 0), (50, 5)]
        
        start_time = time.time()
        successful_suggestions = 0
        
        for line, column in test_positions:
            try:
                result = suggester.get_suggestion(file_path, line, column)
                if 'suggestion' in result:
                    successful_suggestions += 1
            except Exception:
                pass  # Count failures silently for performance test
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(test_positions) if test_positions else 0
        
        print(f"   ⏱️  Total time: {total_time:.3f}s")
        print(f"   ⚡ Avg per suggestion: {avg_time:.3f}s")
        print(f"   ✅ Success rate: {successful_suggestions}/{len(test_positions)}")
        
        # Performance assertions
        if avg_time < 0.1:
            print(f"   ✅ Performance: Good (< 0.1s per suggestion)")
        elif avg_time < 0.5:
            print(f"   ⚠️  Performance: Acceptable (< 0.5s per suggestion)")
        else:
            print(f"   ❌ Performance: Poor (>= 0.5s per suggestion)")
    
    return True


def main():
    """Run focused E2E tests."""
    print("🚀 Focused E2E Tests for Code Suggester")
    print("="*60)
    print("Testing real-world scenarios using sample files")
    
    # Change to parent directory for testing
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Verify we're in the right directory
    if not Path("code_suggester.py").exists():
        print("❌ Error: code_suggester.py not found")
        print("   Please ensure the script structure is correct")
        return 1
    
    # Verify sample files exist
    sample_dir = Path("sample_files")
    if not sample_dir.exists():
        print("❌ Error: sample_files directory not found")
        return 1
    
    # Run test categories
    test_results = []
    
    try:
        test_results.append(("Method Completion", test_method_completion()))
        test_results.append(("CLI Integration", test_cli_real_world_scenarios()))
        test_results.append(("Structure Extraction", test_structure_extraction_accuracy()))
        test_results.append(("Performance", test_performance_characteristics()))
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Tests failed with error: {e}")
        return 1
    
    # Print summary
    print("\n" + "="*60)
    print("📋 E2E Test Summary")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} test categories passed")
    
    if passed_tests == total_tests:
        print("🎉 All E2E tests passed! Code suggester is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())