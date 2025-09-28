#!/usr/bin/env python3
"""
Test script for OpenAI integration with the code suggester.

This script tests the OpenAI provider implementation and provides examples
of how to use it with real API keys.
"""

import os
import sys
import json

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code_suggester import CodeSuggester, OpenAIProvider, MockLLMProvider


def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    print("🔧 Testing OpenAI Provider Initialization")
    print("-" * 50)
    
    # Test without API key
    try:
        provider = OpenAIProvider()
        print("❌ Should have failed without API key")
    except ValueError as e:
        print(f"✅ Correctly rejected empty API key: {e}")
    except ImportError as e:
        print(f"❌ Import error (OpenAI not installed): {e}")
        return False
    
    # Test with dummy API key
    try:
        provider = OpenAIProvider(api_key="dummy-key-for-testing")
        print("✅ Provider initialized with dummy key")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize with dummy key: {e}")
        return False


def test_openai_provider_with_real_key():
    """Test OpenAI provider with real API key."""
    print("\n🌐 Testing OpenAI Provider with Real API Key")
    print("-" * 50)
    
    # Get API key from environment or user input
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found in environment")
        print("   Set OPENAI_API_KEY environment variable to test with real API")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return False
    
    try:
        # Initialize provider
        provider = OpenAIProvider(api_key=api_key)
        print("✅ OpenAI provider initialized successfully")
        
        # Test simple completion
        test_prompt = """
def calculate_factorial(n):
    if n <= 1:
        return 1
    else:
        return n * calculate_factorial(n - 1)

# Test the function
result = calculate_factorial(5)
print(f"Factorial of 5 is: {result}")

# Now let's create a function to calculate fibonacci sequence
def fibonacci("""
        
        print("🧠 Generating completion with OpenAI...")
        completion = provider.generate_completion(test_prompt, max_tokens=100)
        print(f"✅ Completion generated: {repr(completion[:100])}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with OpenAI API: {e}")
        return False


def test_cli_integration_with_openai():
    """Test CLI integration with OpenAI provider."""
    print("\n🖥️  Testing CLI Integration with OpenAI")
    print("-" * 50)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Skipping CLI test - no OPENAI_API_KEY")
        return False
    
    import subprocess
    
    # Test CLI with OpenAI provider
    cmd = [
        sys.executable, "code_suggester.py",
        "sample_files/simple_example.py", "20", "10",
        "--provider", "openai",
        "--api-key", api_key,
        "--output-format", "json"
    ]
    
    try:
        print(f"🔍 Running: {' '.join(cmd[:7])} [API_KEY] ...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            try:
                json_result = json.loads(result.stdout)
                print("✅ CLI integration successful")
                print(f"   Suggestion: {repr(json_result.get('suggestion', '')[:50])}...")
                print(f"   Prompt length: {json_result.get('prompt_length', 'N/A')}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON output: {result.stdout[:100]}...")
                return False
        else:
            print(f"❌ CLI failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ CLI test timed out (>30s)")
        return False
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False


def test_comparison_mock_vs_openai():
    """Compare mock provider vs OpenAI provider outputs."""
    print("\n⚖️  Comparing Mock vs OpenAI Providers")
    print("-" * 50)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Skipping comparison - no OPENAI_API_KEY")
        return
    
    test_prompt = """
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
    
    def multiply(self, value):
        self.result *= value
        return self.result
    
    def """
    
    try:
        # Test with mock provider
        mock_provider = MockLLMProvider()
        mock_completion = mock_provider.generate_completion(test_prompt)
        print(f"🎭 Mock Provider: {repr(mock_completion)}")
        
        # Test with OpenAI provider
        openai_provider = OpenAIProvider(api_key=api_key)
        openai_completion = openai_provider.generate_completion(test_prompt, max_tokens=50)
        print(f"🧠 OpenAI Provider: {repr(openai_completion)}")
        
        print("✅ Comparison completed")
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")


def demonstrate_usage():
    """Demonstrate usage examples."""
    print("\n📖 Usage Examples")
    print("-" * 50)
    
    print("1. Using OpenAI with environment variable:")
    print("   export OPENAI_API_KEY='your-api-key'")
    print("   python code_suggester.py sample_files/simple_example.py 20 10 --provider openai")
    
    print("\n2. Using OpenAI with command line API key:")
    print("   python code_suggester.py sample_files/simple_example.py 20 10 --provider openai --api-key 'your-key'")
    
    print("\n3. JSON output for programmatic use:")
    print("   python code_suggester.py sample_files/complex_example.py 50 5 --provider openai --output-format json")
    
    print("\n4. Testing different models (modify code_suggester.py):")
    print("   # In OpenAIProvider.__init__, change model parameter")
    print("   # Available models: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview")


def main():
    """Run all OpenAI integration tests."""
    print("🚀 OpenAI Integration Testing for Code Suggester")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Provider initialization
    result1 = test_openai_provider_initialization()
    test_results.append(("Provider Initialization", result1))
    
    # Test 2: Real API key testing
    result2 = test_openai_provider_with_real_key()
    test_results.append(("Real API Testing", result2))
    
    # Test 3: CLI integration
    result3 = test_cli_integration_with_openai()
    test_results.append(("CLI Integration", result3))
    
    # Test 4: Comparison (demonstration only)
    test_comparison_mock_vs_openai()
    
    # Test 5: Usage demonstration
    demonstrate_usage()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 OpenAI Integration Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All OpenAI integration tests passed!")
    else:
        print("⚠️  Some tests failed - check API key and network connection")
    
    # Next steps
    print(f"\n🎯 Next Steps:")
    print("• Set OPENAI_API_KEY environment variable to enable full testing")
    print("• Run: python code_suggester.py sample_files/simple_example.py 20 10 --provider openai")
    print("• Test with different sample files and positions")
    print("• Compare outputs with mock provider")


if __name__ == "__main__":
    main()