# 🧪 E2E Testing Guide for Code Suggester

This guide provides comprehensive instructions for testing the code suggester functionality using the sample files.

## 🚀 Quick Start E2E Testing

### 1. **Run All Tests**
```bash
# Unit tests (18 tests)
python test_code_suggester.py

# Focused E2E tests (4 categories)
python test_e2e_focused.py

# Interactive demo
python demo_e2e.py

# Full E2E test suite (13 tests)
python test_e2e.py
```

### 2. **Manual CLI Testing**

#### Basic Suggestions
```bash
# Simple file - empty line
python code_suggester.py sample_files/simple_example.py 10 0

# Simple file - inside method
python code_suggester.py sample_files/simple_example.py 20 15

# Complex file - inside class
python code_suggester.py sample_files/complex_example.py 50 10
```

#### JSON Output (for IDE integration)
```bash
# Get JSON response
python code_suggester.py sample_files/simple_example.py 25 10 --output-format json

# Pretty print JSON
python code_suggester.py sample_files/simple_example.py 25 10 --output-format json | python -m json.tool
```

#### Context Window Testing
```bash
# Small context window (will truncate)
python code_suggester.py sample_files/complex_example.py 100 10 --context-window 500

# Large context window
python code_suggester.py sample_files/simple_example.py 20 5 --context-window 4000
```

## 🎯 Specific E2E Test Scenarios

### **Method Completion Testing**
Test positions that simulate IDE autocomplete scenarios:

```bash
# After object creation (like "calc.|" cursor)
python code_suggester.py sample_files/simple_example.py 62 25

# Inside method call (like "calc.add(|" cursor)  
python code_suggester.py sample_files/simple_example.py 65 12

# Class method definition
python code_suggester.py sample_files/simple_example.py 19 20
```

### **Complex Code Structure Testing**
```bash
# Inside dataclass
python code_suggester.py sample_files/complex_example.py 51 15

# Decorator area
python code_suggester.py sample_files/complex_example.py 102 10

# Async function body
python code_suggester.py sample_files/complex_example.py 135 20

# Generic class
python code_suggester.py sample_files/complex_example.py 75 25
```

### **Error Handling Testing**
```bash
# Line out of range (should not crash)
python code_suggester.py sample_files/simple_example.py 1000 0

# Negative line (should handle gracefully)
python code_suggester.py sample_files/simple_example.py -1 0

# Very large column
python code_suggester.py sample_files/simple_example.py 10 10000

# Non-existent file (should show error)
python code_suggester.py non_existent.py 10 0
```

## 📊 Expected Results

### **Structure Extraction (simple_example.py)**
- ✅ 1 Class: `Calculator`
- ✅ 7+ Methods: `__init__`, `add`, `subtract`, `multiply`, `divide`, `clear`, `get_history`
- ✅ 2+ Functions: `create_calculator`, `main`
- ✅ 4 Imports: `os`, `sys`, `List`, `Dict`

### **Structure Extraction (complex_example.py)**
- ✅ 6+ Classes: `Serializable`, `Status`, `Task`, `BaseProcessor`, `TaskProcessor`
- ✅ 15+ Functions: Various async/sync functions
- ✅ 20+ Imports: `asyncio`, `contextlib`, `typing`, etc.

### **Performance Expectations**
- ⚡ Simple file: < 0.01s per suggestion
- ⚡ Complex file: < 0.05s per suggestion
- 📏 Prompt generation: < 0.001s
- 🔍 Structure extraction: < 0.01s

### **CLI Output Formats**

#### Text Output Example:
```
Suggestion: 
    # TODO: Implement this
Prompt length: 4484/8096
```

#### JSON Output Example:
```json
{
  "suggestion": "\n    # TODO: Implement this",
  "context": {
    "file_path": "sample_files/simple_example.py",
    "line_number": 20,
    "column_number": 10,
    "code_structure": { ... }
  },
  "truncated": false,
  "prompt_length": 4534,
  "context_window": 8096
}
```

## 🔧 Advanced Testing Scenarios

### **Performance Stress Testing**
```bash
# Test with multiple rapid requests
for i in {10..50..10}; do 
  echo "Testing line $i"
  time python code_suggester.py sample_files/complex_example.py $i 10
done
```

### **Context Window Stress Testing**  
```bash
# Test different window sizes
for size in 500 1000 2000 4000 8000; do
  echo "Testing window size $size"
  python code_suggester.py sample_files/complex_example.py 100 10 --context-window $size | grep "Prompt length"
done
```

### **Integration Testing with Real IDE Workflows**
```bash
# Simulate IDE usage patterns
positions=(
  "15 0"    # Import area
  "25 10"   # Class definition
  "35 15"   # Method body
  "45 5"    # Function call
  "55 20"   # Parameter area
)

for pos in "${positions[@]}"; do
  echo "Testing position: $pos"
  python code_suggester.py sample_files/simple_example.py $pos --output-format json | jq '.suggestion'
done
```

## 🎮 Interactive Testing

### **Python REPL Testing**
```python
# Start Python REPL
python3

# Test programmatically
import sys, os
sys.path.append('.')
from code_suggester import CodeSuggester

suggester = CodeSuggester()

# Test simple suggestion
result = suggester.get_suggestion('sample_files/simple_example.py', 20, 10)
print(f"Suggestion: {result['suggestion']}")
print(f"Classes found: {len(result['context']['code_structure']['classes'])}")

# Test structure extraction
analyzer = suggester.analyze_file('sample_files/complex_example.py')
structure = analyzer.extract_structure()
print(f"Complex file has {len(structure['classes'])} classes")
```

## ✅ Success Criteria

### **E2E Tests Should Pass If:**
1. 🎯 **All unit tests pass** (18/18)
2. 🎯 **All focused E2E tests pass** (4/4 categories)
3. 🎯 **CLI responds within 0.1s** for simple files
4. 🎯 **JSON output is valid** and contains required keys
5. 🎯 **Structure extraction is accurate** for both sample files
6. 🎯 **Error handling is graceful** (no crashes)
7. 🎯 **Context truncation works** with warnings
8. 🎯 **Multiple calls are consistent** (same results)

## 🚨 Common Issues & Solutions

### **"File not found" errors**
```bash
# Ensure you're in the autocomplete directory
cd /path/to/autocomplete
pwd  # Should show .../autocomplete
ls sample_files/  # Should show .py files
```

### **"No module named 'code_suggester'" errors**
```bash
# Ensure Python path is set correctly
export PYTHONPATH=$PWD:$PYTHONPATH
python -c "import code_suggester; print('OK')"
```

### **Slow performance**
```bash
# Check system resources
python -c "import time; start=time.time(); import ast; print(f'AST import: {time.time()-start:.3f}s')"
```

## 📋 Test Checklist

- [ ] Unit tests: `python test_code_suggester.py`
- [ ] E2E focused tests: `python test_e2e_focused.py`  
- [ ] Demo run: `python demo_e2e.py`
- [ ] Manual CLI testing with both sample files
- [ ] JSON output validation
- [ ] Context window testing (500, 1000, 2000, 4000, 8000)
- [ ] Error handling with invalid inputs
- [ ] Performance verification (< 0.1s per suggestion)
- [ ] Structure extraction accuracy verification

## 🎉 Ready for Production!

When all tests pass, the code suggester is ready for:
- ✅ IDE plugin integration
- ✅ API service deployment  
- ✅ Real LLM provider integration
- ✅ Production usage