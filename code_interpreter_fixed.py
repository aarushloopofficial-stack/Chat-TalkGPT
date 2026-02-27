"""
Chat&Talk GPT - Code Interpreter Sandbox
Secure code execution environment
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
    "statistics", "decimal", "fractions", "complex", "array",
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
        
        # Create a restricted globals dict
        restricted_globals = {
            "__builtins__": {
                # Allow only safe builtins
                "print": lambda *args, **kwargs: (
                    logs.append({"type": "print", "content": " ".join(map(str, args))}),
                    print(*args, **kwargs)
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
                "input": lambda *args, **kwargs: logs.append({"type": "input", "content": "Input not allowed in sandbox"}),
                "open": lambda *args, **kwargs: logs.append({"type": "error", "content": "File operations not allowed"}),
                "__import__": lambda *args, **kwargs: logs.append({"type": "error", "content": "Dynamic imports not allowed"}),
            },
            # Pre-import some safe modules
            "math": __import__("math"),
            "random": __import__("random"),
            "datetime": __import__("datetime"),
            "time": __import__("time"),
            "json": __import__("json"),
            "re": __import__("re"),
            "collections": __import__("collections"),
            "itertools": __import__("itertools"),
            "functools": __import__("functools"),
            "operator": __import__("operator"),
            "string": __import__("string"),
            "statistics": __import__("statistics"),
            "decimal": __import__("decimal"),
            "fractions": __import__("fractions"),
            "typing": __import__("typing"),
            "pathlib": __import__("pathlib"),
            "numpy": __import__("numpy"),
            "pandas": __import__("pandas"),
            # Include data visualization with limited functionality
            "matplotlib": __import__("matplotlib"),
            "sklearn": __import__("sklearn"),
        }
        
        restricted_locals = {}
        
        # Redirect stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            if capture_output:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
            
            # Execute code
            loop = asyncio.get_event_loop()
            
            async def run_code():
                try:
                    exec(code, restricted_globals, restricted_locals)
                except Exception as e:
                    raise e
            
            await asyncio.wait_for(run_code(), timeout=timeout)
            
            # Get captured output
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            
            return {
                "output": stdout[:self.max_output_size],
                "error": stderr[:self.max_output_size],
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
            "pickle", "marshal", "exec", "eval", "compile",
            "rmtree", "remove", "unlink", "mkfifo", "mknod"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in code_lower:
                return {
                    "safe": False,
                    "reason": f"Dangerous operation detected: {keyword}"
                }
        
        # Check for attempts to access system
        if "sys." in code_lower or "os." in code_lower:
            return {
                "safe": False,
                "reason": "System module access not allowed"
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
- Use numpy and pandas for data operations
- Include error handling
- Return the result as a print statement

Code:"""
        
        try:
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
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_code(self, text: str) -> str:
        """Extract Python code from AI response"""
        # Try to find code block
        code_match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try to find any code block
        code_match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
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
- Use matplotlib and pandas
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
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
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
    explanation: bool = True
) -> Dict[str, Any]:
    """Convenience function for running code from natural language"""
    interpreter = get_code_interpreter()
    return await interpreter.execute_with_ai(task, explanation=explanation)
