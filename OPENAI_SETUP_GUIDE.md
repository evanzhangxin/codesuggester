# 🔑 OpenAI Integration Setup Guide

## ✅ OpenAI Provider Implementation Complete

The code suggester now includes full OpenAI API integration! Here's how to use it:

### 🚀 Quick Start

#### 1. **Get OpenAI API Key**
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Create an API key in your dashboard
- Note: This requires a paid OpenAI account with credits

#### 2. **Set Environment Variable**
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-actual-api-key-here"

# Windows
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 3. **Test OpenAI Integration**
```bash
# Basic usage with OpenAI
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai

# JSON output for programmatic use
python code_suggester.py sample_files/simple_example.py 25 15 --provider openai --output-format json

# Use API key directly (not recommended for production)
python code_suggester.py sample_files/complex_example.py 50 5 --provider openai --api-key "your-key"
```

## 🔧 Implementation Details

### **Supported Providers**
- ✅ **`mock`** - Local mock provider (default, no API key needed)
- ✅ **`openai`** - OpenAI GPT models (requires API key)
- ✅ **`anthropic`** - Anthropic Claude models (requires API key, package not installed)

### **OpenAI Configuration**
- **Default Model**: `gpt-3.5-turbo` (fast and cost-effective)
- **Temperature**: `0.3` (balanced creativity/determinism)
- **Max Tokens**: `150` (configurable)
- **Stop Sequences**: `["\\n\\n", "\`\`\`"]` (prevents overgeneration)

### **Error Handling**
- Graceful fallback to mock provider on API errors
- Proper error messages for missing API keys
- Network timeout handling
- Cost-conscious token limits

## 📊 Performance Comparison

| Provider | Speed | Quality | Cost | Use Case |
|----------|-------|---------|------|----------|
| **Mock** | ⚡ Instant | 📝 Basic | 💰 Free | Development, Testing |
| **OpenAI** | 🔄 ~1-3s | 🧠 High | 💳 Paid | Production, Real Code |
| **Anthropic** | 🔄 ~1-3s | 🧠 High | 💳 Paid | Alternative LLM |

## 🧪 Testing Examples

### **Example 1: Method Completion**
```bash
# Input: Calculator class with incomplete method
python code_suggester.py sample_files/simple_example.py 25 20 --provider openai

# Expected: Intelligent method completion based on class context
```

### **Example 2: Complex Code Context**
```bash
# Input: Complex async/decorator context
python code_suggester.py sample_files/complex_example.py 100 15 --provider openai --output-format json

# Expected: Context-aware async function completion
```

### **Example 3: Error Handling**
```bash
# Test with invalid API key
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai --api-key "invalid"

# Expected: Graceful fallback to mock provider with error message
```

## 🔐 Security Best Practices

### **API Key Management**
- ✅ Use environment variables (`OPENAI_API_KEY`)
- ✅ Never commit API keys to version control
- ✅ Use different keys for development/production
- ✅ Monitor API usage and set spending limits

### **Production Deployment**
```bash
# Recommended production usage
export OPENAI_API_KEY="your-production-key"
python code_suggester.py $FILE $LINE $COL --provider openai --output-format json
```

## 💰 Cost Considerations

### **OpenAI Pricing (as of 2024)**
- **GPT-3.5-turbo**: ~$0.001-0.002 per 1K tokens
- **GPT-4**: ~$0.03-0.06 per 1K tokens
- **Average suggestion**: ~500-1000 tokens (prompt + completion)

### **Cost Optimization Tips**
- Use `gpt-3.5-turbo` for most suggestions (cheaper)
- Implement caching for repeated queries
- Set appropriate token limits
- Monitor usage with OpenAI dashboard

## 🚀 Advanced Usage

### **Custom Model Configuration**
```python
# Modify code_suggester.py to use different models
provider = OpenAIProvider(api_key=api_key, model="gpt-4")
```

### **Batch Processing**
```bash
# Process multiple files efficiently
for file in *.py; do
    python code_suggester.py "$file" 20 10 --provider openai --output-format json
done
```

### **IDE Integration Example**
```python
# Example IDE plugin code
from code_suggester import CodeSuggester, OpenAIProvider

api_key = os.getenv('OPENAI_API_KEY')
provider = OpenAIProvider(api_key=api_key)
suggester = CodeSuggester(provider)

# Get suggestion at cursor position
result = suggester.get_suggestion(file_path, line, column)
suggestion = result['suggestion']
```

## 🐛 Troubleshooting

### **Common Issues**

#### "OpenAI library not installed"
```bash
pip install openai>=1.0.0
```

#### "API key is required"
```bash
# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Or use command line
python code_suggester.py file.py 20 10 --provider openai --api-key "your-key"
```

#### "API call failed" / Network errors
- Check internet connection
- Verify API key is valid and has credits
- Check OpenAI service status
- Falls back to mock provider automatically

#### Slow response times
- Normal for first request (model loading)
- Consider using `gpt-3.5-turbo` instead of `gpt-4`
- Check network latency to OpenAI servers

### **Debug Mode**
```bash
# Enable verbose output for debugging
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai --output-format json | jq '.'
```

## 📈 Next Steps

### **Ready for Production Use**
- ✅ Full OpenAI integration implemented
- ✅ Error handling and fallbacks
- ✅ CLI and programmatic interfaces
- ✅ JSON output for IDE integration
- ✅ Comprehensive testing framework

### **Future Enhancements**
- Response caching for performance
- Multiple model support (GPT-4, etc.)
- Custom prompt templates
- Batch processing optimization
- Usage analytics and monitoring

---

## 🎉 **OpenAI Integration Complete!**

The code suggester now supports real AI-powered code completion with OpenAI's models. Set your API key and start getting intelligent code suggestions!

**Test it now:**
```bash
export OPENAI_API_KEY="your-key-here"
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai
```