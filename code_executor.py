"""
Chat&Talk GPT - Code Executor Module
Provides code execution functionality using the Piston API with local fallback
"""
import requests
import logging
import json
import subprocess
import tempfile
import os
import shutil
from typing import Dict, List, Optional, Any

logger = logging.getLogger("CodeExecutor")

# Piston API endpoints
PISTON_API_BASE = "https://emkc.org/api/v2/piston"
PISTON_EXECUTE_URL = f"{PISTON_API_BASE}/execute"
PISTON_RUNTIMES_URL = f"{PISTON_API_BASE}/runtimes"

# Language mapping for Piston API
LANGUAGE_MAP = {
    "python": "python",
    "python3": "python",
    "javascript": "javascript",
    "js": "javascript",
    "node": "javascript",
    "java": "java",
    "c": "c",
    "cpp": "c++",
    "c++": "c++",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "ruby": "ruby",
    "php": "php",
    "typescript": "typescript",
    "ts": "typescript",
    "csharp": "csharp",
    "c#": "csharp",
    "swift": "swift",
    "kotlin": "kotlin",
}

# File extensions for local execution
LANGUAGE_EXTENSIONS = {
    "python": ".py",
    "javascript": ".js",
    "java": ".java",
    "c": ".c",
    "c++": ".cpp",
    "go": ".go",
    "rust": ".rs",
    "ruby": ".rb",
    "php": ".php",
    "typescript": ".ts",
    "csharp": ".cs",
    "swift": ".swift",
    "kotlin": ".kt",
}

# Default timeout for code execution (in seconds)
DEFAULT_TIMEOUT = 10


class CodeExecutor:
    """
    Code execution class using the Piston API with local fallback.
    Supports multiple programming languages including Python, JavaScript, Java, C/C++, etc.
    """
    
    def __init__(self, user_agent: str = "ChatAndTalkGPT/1.0 (Code Executor)"):
        """
        Initialize the CodeExecutor with user agent and load supported languages.
        
        Args:
            user_agent: User agent string for API requests
        """
        self.user_agent = user_agent
        self._supported_languages: List[Dict[str, Any]] = []
        self._timeout = DEFAULT_TIMEOUT
        self._piston_available = False
        self._local_available = True
        self._load_supported_languages()
        self._check_local_runtimes()
        
    def _load_supported_languages(self) -> None:
        """Load supported languages from Piston API."""
        try:
            response = requests.get(
                PISTON_RUNTIMES_URL,
                headers={"User-Agent": self.user_agent},
                timeout=10
            )
            if response.status_code == 200:
                self._supported_languages = response.json()
                self._piston_available = True
                logger.info(f"Loaded {len(self._supported_languages)} supported languages from Piston API")
            else:
                logger.warning(f"Failed to load languages from Piston API: {response.status_code}")
                self._set_default_languages()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error loading supported languages: {e}")
            self._piston_available = False
            self._set_default_languages()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Piston API response: {e}")
            self._piston_available = False
            self._set_default_languages()
    
    def _check_local_runtimes(self) -> None:
        """Check which local runtimes are available."""
        self._local_runtimes = {}
        
        # Check for Python
        if self._check_command("python") or self._check_command("python3"):
            self._local_runtimes["python"] = self._get_command_version("python") or "3.x"
            
        # Check for Node.js
        if self._check_command("node"):
            self._local_runtimes["javascript"] = self._get_command_version("node") or "18.x"
            
        # Check for Java
        if self._check_command("java"):
            self._local_runtimes["java"] = self._get_command_version("java") or "11+"
            
        # Check for Go
        if self._check_command("go"):
            self._local_runtimes["go"] = self._get_command_version("go") or "1.x"
            
        # Check for Rust
        if self._check_command("rustc"):
            self._local_runtimes["rust"] = self._get_command_version("rustc") or "1.x"
            
        # Check for Ruby
        if self._check_command("ruby"):
            self._local_runtimes["ruby"] = self._get_command_version("ruby") or "3.x"
            
        # Check for PHP
        if self._check_command("php"):
            self._local_runtimes["php"] = self._get_command_version("php") or "8.x"
            
        logger.info(f"Available local runtimes: {self._local_runtimes}")
        
    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
            
    def _get_command_version(self, command: str) -> Optional[str]:
        """Get the version of a command."""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                version_output = result.stdout or result.stderr
                # Extract version number
                import re
                match = re.search(r'(\d+\.\d+\.\d+)', version_output)
                if match:
                    return match.group(1)
                return version_output.strip()[:20]
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None
            
    def _set_default_languages(self) -> None:
        """Set default supported languages if API is unavailable."""
        self._supported_languages = [
            {"language": "python", "version": "3.10.0"},
            {"language": "javascript", "version": "18.15.0"},
            {"language": "java", "version": "15.0.2"},
            {"language": "c", "version": "10.2.0"},
            {"language": "c++", "version": "10.2.0"},
            {"language": "go", "version": "1.16.2"},
            {"language": "rust", "version": "1.68.2"},
            {"language": "ruby", "version": "3.0.1"},
            {"language": "php", "version": "8.1.0"},
            {"language": "typescript", "version": "5.0.3"},
            {"language": "csharp", "version": "6.12.0"},
            {"language": "swift", "version": "5.8.0"},
            {"language": "kotlin", "version": "1.8.20"},
        ]
        logger.info("Using default supported languages")
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of supported languages with their versions.
        
        Returns:
            List of dictionaries containing language name and version
        """
        # Return Piston languages if available
        if self._piston_available:
            return [
                {"language": lang.get("language", ""), "version": lang.get("version", ""), "source": "piston"}
                for lang in self._supported_languages
            ]
        
        # Otherwise return local runtimes
        return [
            {"language": lang, "version": ver, "source": "local"}
            for lang, ver in self._local_runtimes.items()
        ]
    
    def _normalize_language(self, language: str) -> Optional[str]:
        """
        Normalize the language name to Piston API format.
        
        Args:
            language: Language name or alias
            
        Returns:
            Normalized language name or None if not supported
        """
        lang_lower = language.lower().strip()
        return LANGUAGE_MAP.get(lang_lower)
    
    def _is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Language name to check
            
        Returns:
            True if language is supported, False otherwise
        """
        normalized = self._normalize_language(language)
        if not normalized:
            return False
        
        # Check Piston API
        if self._piston_available:
            for lang in self._supported_languages:
                if lang.get("language", "").lower() == normalized.lower():
                    return True
        
        # Check local runtimes
        if normalized in self._local_runtimes:
            return True
            
        return False
    
    def _get_language_version(self, language: str) -> Optional[str]:
        """
        Get the default version for a language.
        
        Args:
            language: Language name
            
        Returns:
            Version string or None if not found
        """
        normalized = self._normalize_language(language)
        if not normalized:
            return None
            
        # Check Piston API
        if self._piston_available:
            for lang in self._supported_languages:
                if lang.get("language", "").lower() == normalized.lower():
                    return lang.get("version")
        
        # Check local runtimes
        if normalized in self._local_runtimes:
            return self._local_runtimes[normalized]
            
        return None
    
    def _execute_local(self, code: str, language: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute code locally using subprocess.
        
        Args:
            code: Source code to execute
            language: Programming language
            args: Optional command-line arguments
            
        Returns:
            Dictionary with execution results
        """
        normalized = self._normalize_language(language)
        
        # Get the file extension
        ext = LANGUAGE_EXTENSIONS.get(normalized, ".txt")
        
        # Create a temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = f"main{ext}"
            filepath = os.path.join(tmpdir, filename)
            
            try:
                # Write code to file
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)
                
                # Determine the command to run
                cmd = self._get_local_command(normalized, filepath, args)
                if not cmd:
                    return {
                        "success": False,
                        "language": normalized,
                        "version": self._local_runtimes.get(normalized, ""),
                        "output": "",
                        "stderr": "",
                        "code": code,
                        "error": f"No local runtime available for {normalized}"
                    }
                
                # Execute the code
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    cwd=tmpdir,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                return {
                    "success": result.returncode == 0,
                    "language": normalized,
                    "version": self._local_runtimes.get(normalized, ""),
                    "output": result.stdout,
                    "stderr": result.stderr,
                    "code": code,
                    "error": None if result.returncode == 0 else result.stderr
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "language": normalized,
                    "version": self._local_runtimes.get(normalized, ""),
                    "output": "",
                    "stderr": "",
                    "code": code,
                    "error": f"Execution timed out after {self._timeout} seconds"
                }
            except Exception as e:
                return {
                    "success": False,
                    "language": normalized,
                    "version": self._local_runtimes.get(normalized, ""),
                    "output": "",
                    "stderr": "",
                    "code": code,
                    "error": f"Execution error: {str(e)}"
                }
    
    def _get_local_command(self, language: str, filepath: str, args: List[str] = None) -> Optional[List[str]]:
        """Get the command to execute the code locally."""
        cmd_args = args or []
        
        commands = {
            "python": ["python", filepath] + cmd_args,
            "javascript": ["node", filepath] + cmd_args,
            "java": ["java", filepath] + cmd_args,  # Note: For java, filepath should be the class name without extension
            "go": ["go", "run", filepath] + cmd_args,
            "rust": ["rustc", filepath, "-o", filepath.replace(".rs", ".exe")],
            "ruby": ["ruby", filepath] + cmd_args,
            "php": ["php", filepath] + cmd_args,
        }
        
        return commands.get(language)
    
    def execute(self, code: str, language: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute code in the specified language using Piston API or local fallback.
        
        Args:
            code: Source code to execute
            language: Programming language (python, javascript, java, etc.)
            args: Optional command-line arguments
            
        Returns:
            Dictionary with execution results:
                - success: bool - Whether execution was successful
                - language: str - Language used
                - version: str - Language version
                - output: str - Standard output
                - stderr: str - Standard error
                - code: str - The executed code
                - error: str - Error message if any
        """
        # Validate language
        normalized_language = self._normalize_language(language)
        if not normalized_language:
            return {
                "success": False,
                "language": language,
                "version": "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": f"Language '{language}' is not supported"
            }
        
        if not self._is_language_supported(language):
            return {
                "success": False,
                "language": normalized_language,
                "version": "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": f"Language '{normalized_language}' is not available"
            }
        
        # Try Piston API first if available
        if self._piston_available:
            result = self._execute_piston(code, normalized_language, args)
            # If Piston works, return the result
            if result.get("success") or "API" not in result.get("error", ""):
                return result
            # If Piston fails (like auth issues), fall back to local execution
            logger.warning(f"Piston API failed, falling back to local execution: {result.get('error')}")
        
        # Fall back to local execution
        return self._execute_local(code, language, args)
    
    def _execute_piston(self, code: str, language: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute code using Piston API."""
        version = self._get_language_version(language)
        
        # Prepare the request payload
        payload = {
            "language": language,
            "version": version,
            "files": [
                {
                    "name": self._get_filename(language),
                    "content": code
                }
            ]
        }
        
        # Add arguments if provided
        if args:
            payload["args"] = args
        
        try:
            response = requests.post(
                PISTON_EXECUTE_URL,
                json=payload,
                headers={
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/json"
                },
                timeout=self._timeout
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "language": language,
                    "version": version or "",
                    "output": "",
                    "stderr": "",
                    "code": code,
                    "error": f"API returned status code {response.status_code}"
                }
            
            result = response.json()
            
            # Parse the response
            run = result.get("run", {})
            compile_result = result.get("compile", {})
            
            output = run.get("stdout", "")
            stderr = run.get("stderr", "")
            
            # Check for compilation errors
            if compile_result and compile_result.get("stderr"):
                compile_stderr = compile_result.get("stderr", "")
                return {
                    "success": False,
                    "language": language,
                    "version": version or "",
                    "output": output,
                    "stderr": stderr,
                    "code": code,
                    "error": f"Compilation error: {compile_stderr}"
                }
            
            # Check if there was a runtime error
            if stderr and "error" in stderr.lower():
                return {
                    "success": False,
                    "language": language,
                    "version": version or "",
                    "output": output,
                    "stderr": stderr,
                    "code": code,
                    "error": f"Runtime error: {stderr}"
                }
            
            return {
                "success": True,
                "language": language,
                "version": version or "",
                "output": output,
                "stderr": stderr,
                "code": code,
                "error": None
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Code execution timed out after {self._timeout} seconds")
            return {
                "success": False,
                "language": language,
                "version": version or "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": f"Execution timed out after {self._timeout} seconds"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Code execution request error: {e}")
            return {
                "success": False,
                "language": language,
                "version": version or "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": f"Request error: {str(e)}"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Piston API response: {e}")
            return {
                "success": False,
                "language": language,
                "version": version or "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": "Error parsing API response"
            }
        except Exception as e:
            logger.error(f"Unexpected error during code execution: {e}")
            return {
                "success": False,
                "language": language,
                "version": version or "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _get_filename(self, language: str) -> str:
        """
        Get the appropriate filename for a language.
        
        Args:
            language: Normalized language name
            
        Returns:
            Filename with appropriate extension
        """
        extensions = {
            "python": "main.py",
            "javascript": "main.js",
            "java": "Main.java",
            "c": "main.c",
            "c++": "main.cpp",
            "go": "main.go",
            "rust": "main.rs",
            "ruby": "main.rb",
            "php": "main.php",
            "typescript": "main.ts",
            "csharp": "Main.cs",
            "swift": "main.swift",
            "kotlin": "Main.kt",
        }
        return extensions.get(language, "main.txt")
    
    def run_python(self, code: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Convenience method to execute Python code.
        
        Args:
            code: Python source code
            args: Optional command-line arguments
            
        Returns:
            Dictionary with execution results
        """
        return self.execute(code, "python", args)
    
    def run_javascript(self, code: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Convenience method to execute JavaScript/Node.js code.
        
        Args:
            code: JavaScript source code
            args: Optional command-line arguments
            
        Returns:
            Dictionary with execution results
        """
        return self.execute(code, "javascript", args)
    
    def run_java(self, code: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Convenience method to execute Java code.
        
        Args:
            code: Java source code
            args: Optional command-line arguments
            
        Returns:
            Dictionary with execution results
        """
        return self.execute(code, "java", args)


# Create a global instance for easy import
code_executor = CodeExecutor()
