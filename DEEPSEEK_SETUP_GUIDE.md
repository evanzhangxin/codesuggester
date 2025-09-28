# DeepSeek Integration Setup Guide

This guide explains how to set up and use the DeepSeek provider with the Python Code Suggester.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# DeepSeek provider uses OpenAI-compatible API
pip install openai>=1.0.0
```

### 2. Get DeepSeek API Key
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key

### 3. Set Up API Key

#### Option A: Environment Variable (Recommended)
```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

#### Option B: Command Line Argument
```bash
python code_suggester.py file.py 10 5 --provider deepseek --api-key "your_api_key_here"
```

## 🛠️ Usage Examples

### Basic Usage
```bash
# Set API key in environment
export DEEPSEEK_API_KEY="sk-..."

# Use DeepSeek for code completion
python code_suggester.py sample_files/simple_example.py 25 10 --provider deepseek
```

### JSON Output for IDE Integration
```bash
python code_suggester.py sample_files/complex_example.py 50 15 \
  --provider deepseek \
  --output-format json \
  --context-window 4096
```

### Using Different Models
DeepSeek provider supports multiple models:
- `deepseek-coder` (default) - Optimized for code completion
- `deepseek-chat` - General conversational model

The provider automatically uses the OpenAI-compatible API endpoint: `https://api.deepseek.com`

## 🔧 Configuration Options

### Model Selection
Currently, the model is set to `deepseek-coder` by default, which is specifically designed for code completion tasks.

### API Endpoint
The DeepSeek provider uses the official API endpoint: `https://api.deepseek.com`

### Error Handling
The provider includes comprehensive error handling for:
- Invalid API keys
- Rate limiting
- Network connection issues
- Timeout errors
- General API errors

## 🧪 Testing the Integration

### 1. Test Basic Functionality
```bash
# Test with mock provider first
python code_suggester.py sample_files/simple_example.py 10 0 --provider mock

# Test DeepSeek provider (should show error without API key)
python code_suggester.py sample_files/simple_example.py 10 0 --provider deepseek

# Test with API key
python code_suggester.py sample_files/simple_example.py 10 0 --provider deepseek --api-key "your_key"
```

### 2. Run Unit Tests
```bash
# Run all tests including DeepSeek provider tests
python test/test_code_suggester.py

# Run focused E2E tests
python test/test_e2e_focused.py
```

## 📊 Features

### ✅ What Works
- **OpenAI-Compatible API**: Uses standard OpenAI client library
- **Code-Optimized Model**: `deepseek-coder` model specialized for programming
- **Robust Error Handling**: Graceful fallback to mock provider on errors
- **Context-Aware**: Leverages AST analysis for intelligent completions
- **Configurable**: Supports custom timeouts, temperature, and context windows
- **Fallback Support**: Automatically falls back to mock provider if DeepSeek fails

### 🎯 Use Cases
- **IDE Integration**: JSON output perfect for IDE plugins
- **Code Review**: Automated suggestion generation
- **Development Workflow**: Quick completions during coding
- **Learning**: Educational tool for understanding code structure

## 🔍 Troubleshooting

### Common Issues

#### "DeepSeek API key is required"
**Solution**: Set the API key using environment variable or command line argument
```bash
export DEEPSEEK_API_KEY="your_key_here"
```

#### "Invalid API key"
**Solution**: Verify your API key is correct and has proper permissions

#### "Network connection failed"
**Solution**: Check your internet connection and firewall settings

#### "Rate limit exceeded"
**Solution**: Wait before making additional requests or upgrade your API plan

### Fallback Behavior
If DeepSeek provider fails for any reason, the system automatically falls back to the mock provider, ensuring the tool continues to function.

## 💡 Tips for Best Results

1. **Use Descriptive Context**: Ensure good code structure around the cursor position
2. **Appropriate Context Window**: Use 2048-8096 tokens for best balance of context and speed
3. **JSON Output**: Use JSON format for programmatic integration
4. **Error Monitoring**: Monitor error messages for API issues

## 🔗 Related Documentation

- [Main README](README.md) - Complete project documentation
- [Testing Guide](test/E2E_TESTING_GUIDE.md) - Comprehensive testing information
- [Performance Testing](TESTING_SUMMARY.md) - Performance metrics and benchmarks

---

**Note**: DeepSeek integration is designed to be drop-in compatible with existing workflows while providing enhanced code completion capabilities through specialized AI models.