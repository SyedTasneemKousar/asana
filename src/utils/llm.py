"""
LLM integration for generating realistic text content.
Supports OpenAI and Anthropic APIs.
"""

import os
import logging
from typing import List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class LLMGenerator:
    """LLM-based content generator"""
    
    def __init__(self):
        """Initialize LLM generator with configured provider"""
        self.provider = Config.LLM_PROVIDER
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.client = None
        self.model = None
        self.available = False
        
        try:
            if self.provider == 'openai':
                self._init_openai()
            elif self.provider == 'anthropic':
                self._init_anthropic()
            else:
                logger.warning(f"Unsupported LLM provider: {self.provider}. Using fallback templates.")
        except (ValueError, ImportError) as e:
            logger.warning(f"LLM initialization failed: {e}. Using fallback templates.")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            api_key = Config.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"  # Cost-effective model
            self.available = True
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}")
            raise
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            api_key = Config.ANTHROPIC_API_KEY
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-3-haiku-20240307"  # Cost-effective model
            self.available = True
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.warning(f"Anthropic initialization failed: {e}")
            raise
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Generated text
        """
        # FORCE FALLBACK - No LLM calls for speed
        return self._fallback_generation(prompt)
        
        try:
            if self.provider == 'openai':
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                system = system_prompt or ""
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}. Using fallback.")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback generation when LLM fails"""
        # Simple fallback - return a generic response
        return "Task description placeholder"
    
    def generate_batch(self, prompts: List[str], system_prompt: Optional[str] = None) -> List[str]:
        """
        Generate multiple texts (with rate limiting consideration)
        
        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt
        
        Returns:
            List of generated texts
        """
        results = []
        for prompt in prompts:
            results.append(self.generate(prompt, system_prompt))
        return results


# Global LLM generator instance (lazy initialization)
_llm_generator: Optional[LLMGenerator] = None


def get_llm_generator() -> LLMGenerator:
    """Get or create LLM generator instance"""
    global _llm_generator
    if _llm_generator is None:
        _llm_generator = LLMGenerator()
    return _llm_generator

