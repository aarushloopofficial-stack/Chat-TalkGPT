"""
Chat&Talk GPT - Code Interpreter Sandbox
Secure code execution environment with proper error handling and syntax fixes
"""
import os
import asyncio
import logging
import uuid
import io
import sys
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger("CodeInterpreter")

# Security settings
ALLOWED_IMPORTS = [
    # Standard library
    "math", "random", "datetime", "time", "json", "re", "os", "sys",
    "collections", "itertools", "functools", "operator", "string",
    "urllib", "html", "base64", "hashlib", "secrets",
    "statistics", "decimal", "fractions", "array",
    # Data science
    "numpy", "pandas", "scipy", "matplotlib", "sklearn",
    # Utilities
    "typing", "pathlib", "copy", "io", "csv"
]

BLOCKED_PATTERNS = [
    r"import\s+os\s*;",
    r"import\s+sys\s*;",
    r"from\s+os\s+import",
    r"from\s+sys\s+import",
    r"subprocess",
    r"pty",
    r"socket",
    r"requests",
    r"urllib\.request",
    r"open\s*\(",
    r"file\s*=",
    r"write\(",
    r"rm\s+",
    r"del\s+",
    r"eval\(",
    r"exec\(",
    r"compile\(",
    r"__import__",
    r"exit\(",
    r"quit\(",
    r"sys\.exit",
    r"os\.system",
    r"os\.popen",
]


class CodeExecutionResult:
    """Result of code execution"""
    
    def __init__(
        self,
        success: bool,
        output: str = "",
        error: str = "",
        execution_time: float = 0,
        memory_used: int = 0
    ):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.memory_used = memory_used
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "timestamp": self.timestamp
        }


class CodeInterpreter:
    """
    Secure code interpreter/sandbox for executing Python code
    Similar to ChatGPT's code interpreter
    """
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.max_execution_time = 30  # seconds
        self.max_output_size = 100000  # characters
        self.max_memory = 256 * 1024 * 1024  # 256MB
    
    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: int = 30,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dict with execution results
        """
        logger.info(f"Executing {language} code")
        
        if language.lower() != "python":
            return {
                "success": False,
                "error": f"Language '{language}' not supported. Only Python is available.",
                "output": ""
            }
        
        # Security check
        security_check = self._security_check(code)
        if not security_check["safe"]:
            return {
                "success": False,
                "error": f"Code blocked by security: {security_check['reason']}",
                "output": ""
            }
        
        # Execute code
        start_time = datetime.now()
        
        try:
            result = await self._execute_python(code, timeout, capture_output)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "output": result["output"],
                "error": result.get("error", ""),
                "execution_time": execution_time,
                "logs": result.get("logs", [])
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Execution timed out after {timeout} seconds",
                "output": "",
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "traceback": traceback.format_exc()
            }
    
    async def _execute_python(
        self,
        code: str,
        timeout: int,
        capture_output: bool
    ) -> Dict[str, Any]:
        """Execute Python code in sandbox"""
        
        # Create custom stdout/stderr capture
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        logs = []
        
        # Create a restricted globals dict with proper syntax
        restricted_globals = {
            "__builtins__": {
                # Allow only safe builtins
                "print": lambda *args, **kwargs: (
                    logs.append({"type": "print", "content": " ".join(map(str, args))}),
                    print(*args, file=stdout_capture, **kwargs)
                ),
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sum": sum,
                "min": min,
                "max": max,
                "sorted": sorted,
                "reversed": reversed,
                "abs": abs,
                "round": round,
                "pow": pow,
                "divmod": divmod,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "hasattr": hasattr,
                "getattr": getattr,
                "setattr": setattr,
                "delattr": delattr,
                "callable": callable,
                "type": type,
                "id": id,
                "hash": hash,
                "ascii": ascii,
                "bin": bin,
                "oct": oct,
                "hex": hex,
                "ord": ord,
                "chr": chr,
                "format": format,
                "slice": slice,
                "property": property,
                "classmethod": classmethod,
                "staticmethod": staticmethod,
                "super": super,
                "vars": vars,
                "dir": dir,
                "help": help,
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "KeyError": KeyError,
                "IndexError": IndexError,
                "AttributeError": AttributeError,
                "RuntimeError": RuntimeError,
                "ZeroDivisionError": ZeroDivisionError,
                "None": None,
                "True": True,
                "False": False,
            }
        }
        
        # Pre-import safe modules (with error handling)
        try:
            restricted_globals["math"] = __import__("math")
            restricted_globals["random"] = __import__("random")
            restricted_globals["datetime"] = __import__("datetime")
            restricted_globals["time"] = __import__("time")
            restricted_globals["json"] = __import__("json")
            restricted_globals["re"] = __import__("re")
            restricted_globals["collections"] = __import__("collections")
            restricted_globals["itertools"] = __import__("itertools")
            restricted_globals["functools"] = __import__("functools")
            restricted_globals["operator"] = __import__("operator")
            restricted_globals["string"] = __import__("string")
            restricted_globals["statistics"] = __import__("statistics")
            restricted_globals["decimal"] = __import__("decimal")
            restricted_globals["fractions"] = __import__("fractions")
            restricted_globals["typing"] = __import__("typing")
            restricted_globals["pathlib"] = __import__("pathlib")
        except ImportError as e:
            logger.warning(f"Failed to import standard library: {e}")
        
        # Try to import data science libraries (optional)
        try:
            restricted_globals["numpy"] = __import__("numpy")
            restricted_globals["np"] = restricted_globals["numpy"]
        except ImportError:
            logger.info("NumPy not available")
        
        try:
            restricted_globals["pandas"] = __import__("pandas")
            restricted_globals["pd"] = restricted_globals["pandas"]
        except ImportError:
            logger.info("Pandas not available")
        
        try:
            restricted_globals["matplotlib"] = __import__("matplotlib")
        except ImportError:
            logger.info("Matplotlib not available")
        
        try:
            restricted_globals["sklearn"] = __import__("sklearn")
        except ImportError:
            logger.info("Scikit-learn not available")
        
        restricted_locals = {}
        
        # Redirect stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            if capture_output:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
            
            # Execute code with timeout
            async def run_code():
                try:
                    exec(code, restricted_globals, restricted_locals)
                except Exception as e:
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    stderr_capture.write(error_msg + "\n")
                    stderr_capture.write(traceback.format_exc())
                    raise e
            
            # Run with timeout
            await asyncio.wait_for(run_code(), timeout=timeout)
            
            # Get captured output
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            
            return {
                "output": stdout[:self.max_output_size],
                "error": stderr[:self.max_output_size] if stderr else "",
                "logs": logs
            }
            
        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _security_check(self, code: str) -> Dict[str, Any]:
        """Check code for security issues"""
        
        code_lower = code.lower()
        
        # Check for blocked patterns
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return {
                    "safe": False,
                    "reason": f"Blocked pattern detected: {pattern}"
                }
        
        # Check for dangerous operations
        dangerous_keywords = [
            "subprocess", "pty", "socket", "threading", "multiprocessing",
            "pickle", "marshal", "rmtree", "remove", "unlink", "mkfifo", "mknod"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in code_lower:
                return {
                    "safe": False,
                    "reason": f"Dangerous operation detected: {keyword}"
                }
        
        # Allow limited sys and os usage for safe operations
        # but block dangerous ones
        if "sys.exit" in code_lower or "os.system" in code_lower or "os.popen" in code_lower:
            return {
                "safe": False,
                "reason": "Dangerous system operation not allowed"
            }
        
        return {"safe": True}
    
    async def execute_with_ai(
        self,
        task: str,
        ai_client = None,
        explanation: bool = True
    ) -> Dict[str, Any]:
        """
        Execute code based on natural language task
        
        Args:
            task: Task description in natural language
            ai_client: AI client for generating code
            explanation: Whether to include code explanation
            
        Returns:
            Dict with execution results and explanation
        """
        if not ai_client:
            return {
                "success": False,
                "error": "AI client not provided"
            }
        
        # Generate code from task
        prompt = f"""Write Python code to accomplish the following task:
{task}

Requirements:
- Use only safe, non-blocking operations
- Use numpy and pandas for data operations if needed
- Include error handling
- Return the result as a print statement

Code:"""
        
        try:
            # Try to import AI aggregator
            from ai_aggregator import get_ai_aggregator
            aggregator = get_ai_aggregator()
            
            code = await aggregator.generate_response(
                prompt=prompt,
                provider="groq",
                model="llama-3.1-70b-versatile"
            )
            
            # Extract just the code (remove explanation)
            code = self._extract_code(code)
            
            # Execute the code
            result = await self.execute(code)
            
            if explanation:
                explanation_prompt = f"""Explain this Python code in simple terms:
{code}

Explanation:"""
                
                explanation_text = await aggregator.generate_response(
                    prompt=explanation_prompt,
                    provider="groq",
                    model="llama-3.1-70b-versatile"
                )
                
                return {
                    "success": result["success"],
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "execution_time": result.get("execution_time", 0),
                    "code": code,
                    "explanation": explanation_text
                }
            
            return result
            
        except ImportError:
            return {
                "success": False,
                "error": "AI aggregator module not found. Cannot generate code from natural language."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error in AI code generation: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def _extract_code(self, text: str) -> str:
        """Extract Python code from AI response"""
        # Try to find python code block
        code_match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try to find any code block
        code_match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try without newline after backticks
        code_match = re.search(r"```(.*?)```", text, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            # Remove language identifier if present
            if code.startswith("python\n"):
                code = code[7:]
            return code
        
        # Return as-is if no code block found
        return text.strip()
    
    async def visualize_data(
        self,
        data_description: str,
        chart_type: str = "auto",
        ai_client = None
    ) -> Dict[str, Any]:
        """
        Create data visualizations
        
        Args:
            data_description: Description of data/chart to create
            chart_type: Type of chart (bar, line, pie, scatter, auto)
            ai_client: AI client for generating code
            
        Returns:
            Dict with visualization code and result
        """
        if not ai_client:
            return {
                "success": False,
                "error": "AI client not provided"
            }
        
        prompt = f"""Create Python code using matplotlib to visualize data.
Data/Chart description: {data_description}
Chart type: {chart_type}

Requirements:
- Use matplotlib and pandas if needed
- Create a complete, runnable script
- Include sample data if not provided
- Save plot to 'output.png'

Code:"""
        
        try:
            from ai_aggregator import get_ai_aggregator
            aggregator = get_ai_aggregator()
            
            code = await aggregator.generate_response(
                prompt=prompt,
                provider="groq",
                model="llama-3.1-70b-versatile"
            )
            
            code = self._extract_code(code)
            
            # Execute
            result = await self.execute(code)
            
            return {
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "code": code,
                "chart_type": chart_type
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "AI aggregator module not found"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error in visualization: {str(e)}",
                "traceback": traceback.format_exc()
            }


# Singleton instance
_code_interpreter: Optional[CodeInterpreter] = None


def get_code_interpreter() -> CodeInterpreter:
    """Get or create code interpreter singleton"""
    global _code_interpreter
    if _code_interpreter is None:
        _code_interpreter = CodeInterpreter()
    return _code_interpreter


async def execute_code(
    code: str,
    language: str = "python",
    timeout: int = 30
) -> Dict[str, Any]:
    """Convenience function for code execution"""
    interpreter = get_code_interpreter()
    return await interpreter.execute(code, language, timeout)


async def run_code_task(
    task: str,
    explanation: bool = True,
    ai_client = None
) -> Dict[str, Any]:
    """Convenience function for running code from natural language"""
    interpreter = get_code_interpreter()
    return await interpreter.execute_with_ai(task, ai_client=ai_client, explanation=explanation)


# Example usage and testing
if __name__ == "__main__":
    async def test_interpreter():
        """Test the code interpreter"""
        print("Testing Code Interpreter...")
        print("-" * 50)
        
        interpreter = get_code_interpreter()
        
        # Test 1: Simple calculation
        print("\nTest 1: Simple calculation")
        result = await interpreter.execute("""
import math
result = math.sqrt(16) + math.pi
print(f"Result: {result}")
""")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        
        # Test 2: List operations
        print("\nTest 2: List operations")
        result = await interpreter.execute("""
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"Original: {numbers}")
print(f"Squared: {squared}")
print(f"Sum of squares: {sum(squared)}")
""")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        
        # Test 3: Error handling
        print("\nTest 3: Error handling")
        result = await interpreter.execute("""
try:
    x = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
""")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        
        # Test 4: Security check (should fail)
        print("\nTest 4: Security check")
        result = await interpreter.execute("""
import subprocess
subprocess.run(['ls'])
""")
        print(f"Success: {result['success']}")
        print(f"Error: {result['error']}")
        
        print("\n" + "-" * 50)
        print("Testing complete!")
    
    # Run tests
    asyncio.run(test_interpreter())