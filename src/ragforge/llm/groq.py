import time
import logging
from typing import Optional
import groq
from groq import Groq

from ragforge.core.base import BaseLLM
from ragforge.settings import settings
from ragforge.errors import ProviderError, ConfigurationError

logger = logging.getLogger(__name__)

class GroqLLM(BaseLLM):
    """
    Groq implementation of the LLM provider.
    """

    def __init__(self):
        """Initialize the Groq LLM client."""
        if not settings.groq_api_key:
            raise ConfigurationError(
                "GROQ_API_KEY environment variable is not set. "
                "Please set it to use Ragforge."
            )
        
        try:
            self.client = Groq(api_key=settings.groq_api_key)
        except Exception as e:
            raise ProviderError(f"Failed to initialize Groq client: {str(e)}")

    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.1,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generates a response using Groq API with retries.
        """
        retries = 0
        last_error = None

        while retries < settings.llm_max_retries:
            try:
                # Build request parameters
                request_params = {
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "model": settings.llm_model,
                    "temperature": temperature,
                    "top_p": top_p,
                }
                
                # Add max_tokens if provided
                if max_tokens is not None:
                    request_params["max_tokens"] = max_tokens
                
                # Add any additional kwargs
                request_params.update(kwargs)
                
                chat_completion = self.client.chat.completions.create(**request_params)
                
                content = chat_completion.choices[0].message.content
                if content is None:
                    raise ProviderError("Received empty response from Groq.")
                    
                return content

            except (groq.APIConnectionError, groq.RateLimitError, groq.APIStatusError) as e:
                logger.warning(f"Groq API error (attempt {retries + 1}): {e}")
                last_error = e
                retries += 1
                time.sleep(1 * retries) # Exponential backoff-ish
            except Exception as e:
                # Non-retryable error
                raise ProviderError(f"Unexpected error during Groq generation: {str(e)}")

        raise ProviderError(f"Max retries exceeded for Groq API. Last error: {str(last_error)}")
