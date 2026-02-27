"""
Chat&Talk GPT - Model Manager
Manages AI model interactions and configurations
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio

logger = logging.getLogger("ModelManager")

class ModelManager:
    """
    Manages AI model configurations and interactions
    Supports multiple providers: Groq, OpenAI, Anthropic, Google, etc.
    """
    
    def __init__(self):
        self.models = {
            "groq": {
                "models": [
                    "llama-3.1-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768",
                    "gemma-7b-it"
                ],
                "default": "llama-3.1-70b-versatile",
                "api_key": os.getenv("GROQ_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1"
            },
            "openai": {
                "models": [
                    "gpt-4-turbo-preview",
                    "gpt-4",
                    "gpt-3.5-turbo",
                    "gpt-3.5-turbo-16k"
                ],
                "default": "gpt-4-turbo-preview",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1"
            },
            "anthropic": {
                "models": [
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                "default": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": "https://api.anthropic.com"
            },
            "google": {
                "models": [
                    "gemini-pro",
                    "gemini-pro-vision"
                ],
                "default": "gemini-pro",
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "base_url": "https://generativelanguage.googleapis.com/v1beta"
            }
        }
        
        self.current_provider = "groq"
        self.current_model = self.models["groq"]["default"]
        self.model_settings = {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        # Load saved settings
        self._load_settings()
    
    def _load_settings(self):
        """Load model settings from file"""
        try:
            settings_file = "model_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.current_provider = saved_settings.get("provider", "groq")
                    self.current_model = saved_settings.get("model", self.models["groq"]["default"])
                    self.model_settings.update(saved_settings.get("settings", {}))
        except Exception as e:
            logger.warning(f"Could not load model settings: {e}")
    
    def _save_settings(self):
        """Save model settings to file"""
        try:
            settings_file = "model_settings.json"
            settings_data = {
                "provider": self.current_provider,
                "model": self.current_model,
                "settings": self.model_settings,
                "updated_at": datetime.now().isoformat()
            }
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save model settings: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return list(self.models.keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        if provider in self.models:
            return self.models[provider]["models"]
        return []
    
    def set_provider(self, provider: str) -> bool:
        """Set the current AI provider"""
        if provider in self.models and self.models[provider]["api_key"]:
            self.current_provider = provider
            self.current_model = self.models[provider]["default"]
            self._save_settings()
            return True
        return False
    
    def set_model(self, model: str) -> bool:
        """Set the current model"""
        if model in self.models[self.current_provider]["models"]:
            self.current_model = model
            self._save_settings()
            return True
        return False
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update model settings"""
        try:
            self.model_settings.update(settings)
            self._save_settings()
            return True
        except Exception as e:
            logger.error(f"Error updating model settings: {e}")
            return False
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current model configuration"""
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "settings": self.model_settings,
            "api_key_configured": bool(self.models[self.current_provider]["api_key"])
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to current provider"""
        try:
            # This would be implemented with actual API calls
            # For now, return a mock response
            return {
                "success": True,
                "provider": self.current_provider,
                "model": self.current_model,
                "message": "Connection test successful"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": self.current_provider
            }
    
    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if provider not in self.models:
            return {"error": "Provider not found"}
        
        provider_info = self.models[provider]
        if model not in provider_info["models"]:
            return {"error": "Model not found"}
        
        # Model information based on provider and model
        model_info = {
            "provider": provider,
            "model": model,
            "available": bool(provider_info["api_key"]),
            "is_default": model == provider_info["default"]
        }
        
        # Add model-specific details
        if provider == "groq":
            if "70b" in model:
                model_info.update({
                    "context_length": 131072,
                    "description": "High-performance large language model",
                    "cost_per_1k_tokens": "0.59"
                })
            elif "8b" in model:
                model_info.update({
                    "context_length": 131072,
                    "description": "Fast and efficient model",
                    "cost_per_1k_tokens": "0.05"
                })
        elif provider == "openai":
            if "gpt-4" in model:
                model_info.update({
                    "context_length": 128000 if "turbo" in model else 8192,
                    "description": "Advanced reasoning model",
                    "cost_per_1k_tokens": "0.03" if "turbo" in model else "0.06"
                })
            elif "gpt-3.5" in model:
                model_info.update({
                    "context_length": 16385 if "16k" in model else 4096,
                    "description": "Fast and capable model",
                    "cost_per_1k_tokens": "0.002" if "16k" in model else "0.0015"
                })
        elif provider == "anthropic":
            model_info.update({
                "context_length": 200000,
                "description": "Constitutional AI model",
                "cost_per_1k_tokens": "0.015" if "opus" in model else "0.003" if "sonnet" in model else "0.00025"
            })
        elif provider == "google":
            model_info.update({
                "context_length": 32768,
                "description": "Google's generative AI model",
                "cost_per_1k_tokens": "0.00025"
            })
        
        return model_info
    
    def get_all_models_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get information about all available models"""
        all_models = {}
        for provider in self.models:
            all_models[provider] = []
            for model in self.models[provider]["models"]:
                model_info = self.get_model_info(provider, model)
                all_models[provider].append(model_info)
        return all_models
    
    def optimize_settings_for_task(self, task_type: str) -> Dict[str, Any]:
        """Get optimized settings for different task types"""
        task_settings = {
            "creative": {
                "temperature": 0.9,
                "top_p": 0.95,
                "max_tokens": 2048
            },
            "analytical": {
                "temperature": 0.1,
                "top_p": 0.5,
                "max_tokens": 4096
            },
            "coding": {
                "temperature": 0.2,
                "top_p": 0.7,
                "max_tokens": 4096
            },
            "conversation": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024
            },
            "summarization": {
                "temperature": 0.3,
                "top_p": 0.6,
                "max_tokens": 512
            }
        }
        
        return task_settings.get(task_type, self.model_settings)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get model usage statistics"""
        # This would track actual usage in a real implementation
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "provider_usage": {
                provider: 0 for provider in self.models.keys()
            },
            "model_usage": {},
            "last_reset": datetime.now().isoformat()
        }

# Singleton instance
_model_manager: Optional[ModelManager] = None

def get_model_manager() -> ModelManager:
    """Get or create model manager singleton"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager

# Convenience functions
def get_current_model_config() -> Dict[str, Any]:
    """Get current model configuration"""
    return get_model_manager().get_current_config()

def set_ai_provider(provider: str) -> bool:
    """Set AI provider"""
    return get_model_manager().set_provider(provider)

def set_ai_model(model: str) -> bool:
    """Set AI model"""
    return get_model_manager().set_model(model)
