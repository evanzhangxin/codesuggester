#!/usr/bin/env python3
"""
Demo script showing DeepSeek integration with the Code Suggester.

This script demonstrates how to use DeepSeek provider programmatically
and shows the differences between providers.
"""

import os
import sys

# Add the parent directory to the path to import code_suggester
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_suggester import CodeSuggester, MockLLMProvider, DeepSeekProvider

def demo_providers():
    """Demonstrate different LLM providers."""
    print("🚀 DeepSeek Integration Demo")
    print("=" * 50)
    
    # Sample code for testing (relative to project root)
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_file = os.path.join(script_dir, "sample_files", "simple_example.py")
    line_number = 25
    column_number = 10
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file {sample_file} not found")
        return
    
    print(f"📄 Testing with file: {sample_file}")
    print(f"📍 Position: Line {line_number}, Column {column_number}")
    print()
    
    # Test 1: Mock Provider
    print("🎭 Testing Mock Provider")
    print("-" * 30)
    mock_suggester = CodeSuggester(MockLLMProvider())
    result = mock_suggester.get_suggestion(sample_file, line_number, column_number)
    print(f"✅ Mock suggestion: {result['suggestion'][:50]}...")
    print(f"📊 Prompt length: {result['prompt_length']} chars")
    print()
    
    # Test 2: DeepSeek Provider (if API key available)
    print("🤖 Testing DeepSeek Provider")
    print("-" * 30)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("⚠️  DEEPSEEK_API_KEY not set in environment")
        print("💡 Set your API key: export DEEPSEEK_API_KEY='your_key_here'")
        print("🔄 Simulating DeepSeek provider initialization...")
        
        try:
            # This will fail without API key, showing error handling
            deepseek_provider = DeepSeekProvider()
        except ValueError as e:
            print(f"✅ Expected error: {e}")
            print("🔄 Falling back to mock provider (as designed)")
            deepseek_suggester = CodeSuggester(MockLLMProvider())
            result = deepseek_suggester.get_suggestion(sample_file, line_number, column_number)
            print(f"✅ Fallback suggestion: {result['suggestion'][:50]}...")
    else:
        print(f"🔑 Found API key: {api_key[:10]}...")
        try:
            deepseek_provider = DeepSeekProvider(api_key=api_key)
            deepseek_suggester = CodeSuggester(deepseek_provider)
            print("🚀 DeepSeek provider initialized successfully")
            
            result = deepseek_suggester.get_suggestion(sample_file, line_number, column_number)
            print(f"✅ DeepSeek suggestion: {result['suggestion'][:50]}...")
            print(f"📊 Prompt length: {result['prompt_length']} chars")
            
            if "DeepSeek Error:" in result['suggestion']:
                print("⚠️  API call failed (expected with test key)")
            else:
                print("🎉 Real DeepSeek completion generated!")
                
        except Exception as e:
            print(f"❌ DeepSeek provider error: {e}")
            print("🔄 This demonstrates robust error handling")
    
    print()
    
    # Test 3: Show code structure analysis
    print("🔍 Code Structure Analysis")
    print("-" * 30)
    
    suggester = CodeSuggester()
    analyzer = suggester.analyze_file(sample_file)
    structure = analyzer.extract_structure()
    
    print(f"📦 Classes found: {len(structure['classes'])}")
    for cls in structure['classes']:
        print(f"   🏗️  {cls['name']} (line {cls['lineno']})")
        for method in cls['methods'][:3]:  # Show first 3 methods
            print(f"      🔧 {method}")
    
    print(f"🔧 Functions found: {len(structure['functions'])}")
    for func in structure['functions'][:3]:  # Show first 3 functions
        print(f"   ⚙️  {func['name']} (line {func['lineno']})")
    
    print(f"📥 Imports found: {len(structure['imports'])}")
    for imp in structure['imports'][:3]:  # Show first 3 imports
        print(f"   📦 {imp['name']}")
    
    print()
    print("✅ Demo completed successfully!")
    print("💡 Try setting DEEPSEEK_API_KEY for real API integration")

def show_cli_examples():
    """Show CLI usage examples."""
    print("\n🖥️  CLI Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "desc": "Basic DeepSeek usage",
            "cmd": "python code_suggester.py sample_files/simple_example.py 25 10 --provider deepseek"
        },
        {
            "desc": "DeepSeek with custom API key",
            "cmd": "python code_suggester.py sample_files/simple_example.py 25 10 --provider deepseek --api-key 'your_key'"
        },
        {
            "desc": "DeepSeek with JSON output",
            "cmd": "python code_suggester.py sample_files/simple_example.py 25 10 --provider deepseek --output-format json"
        },
        {
            "desc": "DeepSeek with custom context window",
            "cmd": "python code_suggester.py sample_files/complex_example.py 50 15 --provider deepseek --context-window 4096"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['desc']}")
        print(f"   $ {example['cmd']}")
        print()
    
    print("🔧 Environment Setup:")
    print("   $ export DEEPSEEK_API_KEY='your_api_key_here'")
    print()
    print("📚 For more details, see: DEEPSEEK_SETUP_GUIDE.md")

if __name__ == "__main__":
    demo_providers()
    show_cli_examples()