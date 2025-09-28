# 🔧 OpenAI Connection Troubleshooting Guide

## 🚨 Problem: Connection Error with OpenAI API

You're seeing: `# Error with OpenAI API: Connection error....`

This indicates network connectivity issues or API problems. Here are solutions:

## 🔍 **Diagnosis Steps**

### 1. **Check API Key Status**
```bash
# Verify API key is set
echo "API Key length: ${#OPENAI_API_KEY}"

# Test API key format (should start with 'sk-')
echo $OPENAI_API_KEY | grep -q "^sk-" && echo "✅ Valid format" || echo "❌ Invalid format"
```

### 2. **Test Network Connectivity**
```bash
# Test basic internet connectivity
curl -I https://api.openai.com

# Test with verbose output
curl -v https://api.openai.com/v1/models
```

### 3. **Verify OpenAI Service Status**
- Check [OpenAI Status Page](https://status.openai.com/)
- Look for API outages or maintenance

## 🛠️ **Solutions**

### **Solution 1: Use Mock Provider (Immediate)**
```bash
# Switch back to mock provider (always works)
python code_suggester.py sample_files/simple_example.py 20 10 --provider mock

# This will give you basic completions without API calls
```

### **Solution 2: Test with Timeout Bypass**
```bash
# Try with JSON output for better error visibility
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai --output-format json
```

### **Solution 3: Validate API Key**
```bash
# Test API key directly with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | head -20
```

### **Solution 4: Network Proxy/Firewall**
If you're behind a corporate firewall:
```bash
# Set proxy if needed
export HTTPS_PROXY=your-proxy-server:port
export HTTP_PROXY=your-proxy-server:port

# Then retry
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai
```

### **Solution 5: Alternative API Endpoint**
Some networks block certain endpoints. Test:
```bash
# Check if you can reach OpenAI at all
ping api.openai.com

# Test different endpoint
nslookup api.openai.com
```

## 🔄 **Quick Workarounds**

### **Option A: Use Offline Mode**
```bash
# Use mock provider for development
python code_suggester.py sample_files/simple_example.py 20 10 --provider mock
```

### **Option B: Test with Different Position**
```bash
# Try a simpler context (might need less processing)
python code_suggester.py sample_files/simple_example.py 10 0 --provider openai
```

### **Option C: Reduce Context Window**
```bash
# Smaller context = faster API calls
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai --context-window 1000
```

## 🔧 **Advanced Debugging**

### **Enable Verbose OpenAI Logging**
```python
# Create debug_openai.py
import openai
import os
import logging

logging.basicConfig(level=logging.DEBUG)

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5,
        timeout=5
    )
    print("✅ Success:", response.choices[0].message.content)
except Exception as e:
    print("❌ Error:", e)
```

### **Check API Credits/Billing**
- Log into [OpenAI Platform](https://platform.openai.com/usage)
- Verify you have available credits
- Check if your API key has usage limits

## 📊 **Common Error Types**

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Connection error` | Network/firewall issue | Check internet, proxy settings |
| `Invalid API key` | Wrong/expired key | Get new key from OpenAI dashboard |
| `Rate limit exceeded` | Too many requests | Wait or upgrade plan |
| `Request timeout` | Slow network | Use smaller context window |
| `Authentication error` | API key format wrong | Check key starts with 'sk-' |

## ✅ **Working Alternatives**

While troubleshooting OpenAI, you can still use the code suggester:

### **1. Mock Provider (Always Available)**
```bash
python code_suggester.py sample_files/simple_example.py 20 10 --provider mock
# Output: Basic rule-based suggestions
```

### **2. Test with Different Sample Files**
```bash
# Try simpler context
python code_suggester.py sample_files/simple_example.py 10 5 --provider openai

# Try complex context  
python code_suggester.py sample_files/complex_example.py 50 10 --provider openai
```

### **3. JSON Output for Debugging**
```bash
python code_suggester.py sample_files/simple_example.py 20 10 --provider openai --output-format json | jq '.'
```

## 🎯 **Next Steps**

1. **Immediate**: Use mock provider for testing
2. **Short-term**: Debug network connectivity
3. **Long-term**: Set up proper OpenAI account with credits

## 📞 **Getting Help**

If issues persist:
1. Check [OpenAI Community Forum](https://community.openai.com/)
2. Verify your OpenAI account status
3. Test with a fresh API key
4. Contact OpenAI support if billing/account issues

---

**🔄 Quick Test Command:**
```bash
# This should always work (mock provider)
python code_suggester.py sample_files/simple_example.py 20 10 --provider mock
```