#!/usr/bin/env python3
"""
Code Suggester - A Python code completion tool using AST analysis and LLM.

This module provides intelligent code suggestions by analyzing the code structure
using AST (Abstract Syntax Tree) and leveraging LLM for context-aware completions.
"""

import ast
import sys
import argparse
import json
import os
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CodeContext:
    """Represents the context around the cursor position."""
    file_path: str
    line_number: int
    column_number: int
    context_window: int
    code_structure: Dict[str, Any]
    context_before: str
    context_after: str
    current_line: str


class ASTAnalyzer:
    """Analyzes Python code using AST to extract structure information."""
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        try:
            self.tree = ast.parse(code)
        except SyntaxError as e:
            # Handle incomplete code by trying to parse what we can
            self.tree = None
            self.syntax_error = e
    
    def extract_structure(self) -> Dict[str, Any]:
        """Extract code structure information from AST."""
        if self.tree is None:
            return {"error": "Syntax error in code", "classes": [], "functions": [], "imports": []}
        
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": [],
            "decorators": []
        }
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "bases": [self._get_node_name(base) for base in node.bases]
                })
            
            elif isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [self._get_node_name(dec) for dec in node.decorator_list],
                    "returns": self._get_node_name(node.returns) if node.returns else None
                })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    structure["imports"].append({
                        "type": "import",
                        "name": alias.name,
                        "asname": alias.asname,
                        "lineno": node.lineno
                    })
            
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    structure["imports"].append({
                        "type": "from_import",
                        "module": node.module,
                        "name": alias.name,
                        "asname": alias.asname,
                        "lineno": node.lineno
                    })
            
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        structure["variables"].append({
                            "name": target.id,
                            "lineno": node.lineno
                        })
        
        return structure
    
    def _get_node_name(self, node) -> str:
        """Extract name from AST node."""
        if node is None:
            return ""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return str(type(node).__name__)
    
    def get_context_at_position(self, line_number: int, column_number: int, 
                              context_window: int) -> Tuple[str, str, str]:
        """Get context before and after the cursor position."""
        if line_number < 1 or line_number > len(self.lines):
            return "", "", ""
        
        current_line = self.lines[line_number - 1] if line_number <= len(self.lines) else ""
        
        # Calculate context boundaries
        start_line = max(0, line_number - context_window // 2)
        end_line = min(len(self.lines), line_number + context_window // 2)
        
        # Get context before cursor
        context_before_lines = self.lines[start_line:line_number-1]
        if line_number <= len(self.lines):
            context_before_lines.append(self.lines[line_number-1][:column_number])
        context_before = '\n'.join(context_before_lines)
        
        # Get context after cursor
        context_after_lines = []
        if line_number <= len(self.lines) and column_number < len(self.lines[line_number-1]):
            context_after_lines.append(self.lines[line_number-1][column_number:])
        context_after_lines.extend(self.lines[line_number:end_line])
        context_after = '\n'.join(context_after_lines)
        
        return context_before, context_after, current_line


class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def generate_completion(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate code completion using LLM."""
        raise NotImplementedError("Subclasses must implement generate_completion")


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and demonstration."""
    
    def generate_completion(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate a mock completion based on simple heuristics."""
        lines = prompt.split('\n')
        last_line = lines[-1] if lines else ""
        
        # Simple completion logic based on context
        if "def " in last_line and "(" in last_line and last_line.count("(") > last_line.count(")"):
            return "):\n    pass"
        elif "class " in last_line and ":" not in last_line:
            return ":\n    pass"
        elif "if " in last_line and ":" not in last_line:
            return ":\n    pass"
        elif "for " in last_line and ":" not in last_line:
            return ":\n    pass"
        elif "while " in last_line and ":" not in last_line:
            return ":\n    pass"
        elif last_line.strip().endswith("="):
            return " None"
        elif "import " in last_line and " as " not in last_line:
            return ""
        else:
            return "\n    # TODO: Implement this"


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for code completion."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key)
        self.model = model
        
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Set it via --api-key argument or OPENAI_API_KEY environment variable."
            )
        
        # Import OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai>=1.0.0"
            )
    
    def generate_completion(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate code completion using OpenAI API."""
        try:
            # Create a focused prompt for code completion
            completion_prompt = f"""You are a Python code completion assistant. Based on the code context below, provide ONLY the code that should complete the current line or add the next logical code.

Do not include explanations, comments, or full rewrites. Just provide the minimal completion.

Code context:
{prompt}

Completion:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": completion_prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more deterministic code
                timeout=10.0,  # 10 second timeout
                stop=["\n\n", "```"]  # Stop at double newlines or code blocks
            )
            
            completion = response.choices[0].message.content
            
            # Clean up the completion
            if completion:
                # Remove any markdown code blocks
                completion = completion.replace("```python", "").replace("```", "")
                # Strip leading/trailing whitespace but preserve internal formatting
                completion = completion.strip()
                
            return completion or "\n    # TODO: Implement this"
            
        except Exception as e:
            # More specific error handling
            import openai
            if isinstance(e, openai.AuthenticationError):
                return f"\n    # OpenAI Error: Invalid API key"
            elif isinstance(e, openai.RateLimitError):
                return f"\n    # OpenAI Error: Rate limit exceeded"
            elif isinstance(e, openai.APIConnectionError):
                return f"\n    # OpenAI Error: Network connection failed"
            elif "timeout" in str(e).lower():
                return f"\n    # OpenAI Error: Request timeout (>10s)"
            else:
                return f"\n    # OpenAI Error: {str(e)[:50]}..."


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider for code completion."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        super().__init__(api_key)
        self.model = model
        
        # Import Anthropic client
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Anthropic library not installed. Install with: pip install anthropic>=0.7.0"
            )
        
        if not api_key:
            raise ValueError(
                "Anthropic API key is required. Set it via --api-key argument or ANTHROPIC_API_KEY environment variable."
            )
    
    def generate_completion(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate code completion using Anthropic Claude API."""
        try:
            completion_prompt = f"""You are a Python code completion assistant. Based on the code context below, provide ONLY the code that should complete the current line or add the next logical code.

Do not include explanations, comments, or full rewrites. Just provide the minimal completion.

Code context:
{prompt}

Completion:"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": completion_prompt
                    }
                ]
            )
            
            completion = response.content[0].text if response.content else ""
            
            # Clean up the completion
            if completion:
                completion = completion.replace("```python", "").replace("```", "")
                completion = completion.strip()
                
            return completion or "\n    # TODO: Implement this"
            
        except Exception as e:
            return f"\n    # Error with Anthropic API: {str(e)[:50]}..."


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider for code completion."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-coder", base_url: str = "https://api.deepseek.com"):
        super().__init__(api_key)
        self.model = model
        self.base_url = base_url
        
        if not api_key:
            raise ValueError(
                "DeepSeek API key is required. Set it via --api-key argument or DEEPSEEK_API_KEY environment variable."
            )
        
        # Import OpenAI client (DeepSeek uses OpenAI-compatible API)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai>=1.0.0"
            )
    
    def generate_completion(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate code completion using DeepSeek API."""
        try:
            # Create a focused prompt for code completion
            completion_prompt = f"""You are a Python code completion assistant. Based on the code context below, provide ONLY the code that should complete the current line or add the next logical code.

Do not include explanations, comments, or full rewrites. Just provide the minimal completion.

Code context:
{prompt}

Completion:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": completion_prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more deterministic code
                timeout=10.0,  # 10 second timeout
                stop=["\n\n", "```"]  # Stop at double newlines or code blocks
            )
            
            completion = response.choices[0].message.content
            
            # Clean up the completion
            if completion:
                # Remove any markdown code blocks
                completion = completion.replace("```python", "").replace("```", "")
                # Strip leading/trailing whitespace but preserve internal formatting
                completion = completion.strip()
                
            return completion or "\n    # TODO: Implement this"
            
        except Exception as e:
            # More specific error handling
            import openai
            if isinstance(e, openai.AuthenticationError):
                return f"\n    # DeepSeek Error: Invalid API key"
            elif isinstance(e, openai.RateLimitError):
                return f"\n    # DeepSeek Error: Rate limit exceeded"
            elif isinstance(e, openai.APIConnectionError):
                return f"\n    # DeepSeek Error: Network connection failed"
            elif "timeout" in str(e).lower():
                return f"\n    # DeepSeek Error: Request timeout (>10s)"
            else:
                return f"\n    # DeepSeek Error: {str(e)[:50]}..."


class CodeSuggester:
    """Main class for providing code suggestions."""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None, context_window: int = 8096):
        self.llm_provider = llm_provider or MockLLMProvider()
        self.context_window = context_window
    
    def analyze_file(self, file_path: str) -> ASTAnalyzer:
        """Analyze a Python file and return AST analyzer."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")
        
        return ASTAnalyzer(code)
    
    def get_suggestion(self, file_path: str, line_number: int, column_number: int,
                      context_window: Optional[int] = None) -> Dict[str, Any]:
        """Get code suggestion at the specified cursor position."""
        if context_window is None:
            context_window = self.context_window
        
        # Analyze the file
        analyzer = self.analyze_file(file_path)
        
        # Extract code structure
        code_structure = analyzer.extract_structure()
        
        # Get context around cursor
        context_before, context_after, current_line = analyzer.get_context_at_position(
            line_number, column_number, context_window // 50  # Convert to line count
        )
        
        # Create context object
        context = CodeContext(
            file_path=file_path,
            line_number=line_number,
            column_number=column_number,
            context_window=context_window,
            code_structure=code_structure,
            context_before=context_before,
            context_after=context_after,
            current_line=current_line
        )
        
        # Prepare prompt for LLM
        prompt = self._create_prompt(context)
        
        # Check context length and truncate if necessary
        truncated = False
        if len(prompt) > context_window:
            prompt = prompt[:context_window]
            truncated = True
        
        # Generate suggestion
        try:
            suggestion = self.llm_provider.generate_completion(prompt)
        except Exception as e:
            suggestion = f"Error generating suggestion: {e}"
        
        result = {
            "suggestion": suggestion,
            "context": asdict(context),
            "truncated": truncated,
            "prompt_length": len(prompt),
            "context_window": context_window
        }
        
        if truncated:
            result["warning"] = "Context was truncated due to length limit. Consider continuing processing."
        
        return result
    
    def _create_prompt(self, context: CodeContext) -> str:
        """Create prompt for LLM based on code context."""
        structure_info = json.dumps(context.code_structure, indent=2)
        
        prompt = f"""
You are a Python code completion assistant. Based on the code structure and context, provide a relevant code completion.

Code Structure:
{structure_info}

Context before cursor:
```python
{context.context_before}
```

Context after cursor:
```python
{context.context_after}
```

Current line: {context.current_line}
Cursor position: Line {context.line_number}, Column {context.column_number}

Please provide a code completion that would be appropriate at this cursor position:
"""
        return prompt


def main():
    """Main entry point for the code suggester."""
    parser = argparse.ArgumentParser(description='Python Code Suggester')
    parser.add_argument('file_path', help='Path to the Python file')
    parser.add_argument('line_number', type=int, help='Line number (1-based)')
    parser.add_argument('column_number', type=int, help='Column number (0-based)')
    parser.add_argument('--context-window', type=int, default=8096, 
                       help='Context window length (default: 8096)')
    parser.add_argument('--api-key', help='API key for LLM provider')
    parser.add_argument('--provider', default='mock', 
                       choices=['mock', 'openai', 'anthropic', 'deepseek'],
                       help='LLM provider to use (default: mock)')
    parser.add_argument('--output-format', default='text', 
                       choices=['text', 'json'],
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    # Initialize LLM provider
    if args.provider == 'mock':
        llm_provider = MockLLMProvider()
    elif args.provider == 'openai':
        # Get API key from argument or environment variable
        api_key = args.api_key or os.getenv('OPENAI_API_KEY')
        try:
            llm_provider = OpenAIProvider(api_key=api_key)
        except (ImportError, ValueError) as e:
            print(f"Error initializing OpenAI provider: {e}")
            print("Falling back to mock provider")
            llm_provider = MockLLMProvider()
    elif args.provider == 'anthropic':
        # Get API key from argument or environment variable
        api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
        try:
            llm_provider = AnthropicProvider(api_key=api_key)
        except (ImportError, ValueError) as e:
            print(f"Error initializing Anthropic provider: {e}")
            print("Falling back to mock provider")
            llm_provider = MockLLMProvider()
    elif args.provider == 'deepseek':
        # Get API key from argument or environment variable
        api_key = args.api_key or os.getenv('DEEPSEEK_API_KEY')
        try:
            llm_provider = DeepSeekProvider(api_key=api_key)
        except (ImportError, ValueError) as e:
            print(f"Error initializing DeepSeek provider: {e}")
            print("Falling back to mock provider")
            llm_provider = MockLLMProvider()
    else:
        llm_provider = MockLLMProvider()
    
    # Create code suggester
    suggester = CodeSuggester(llm_provider, args.context_window)
    
    try:
        # Get suggestion
        result = suggester.get_suggestion(
            args.file_path, 
            args.line_number, 
            args.column_number,
            args.context_window
        )
        
        # Output result
        if args.output_format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"Suggestion: {result['suggestion']}")
            if result.get('warning'):
                print(f"Warning: {result['warning']}")
            print(f"Prompt length: {result['prompt_length']}/{result['context_window']}")
    
    except Exception as e:
        if args.output_format == 'json':
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()