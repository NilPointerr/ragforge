import time
import logging
from typing import Optional
import groq
from groq import Groq

from ragforge.llm.base import BaseLLM
from ragforge.settings import settings
from ragforge.errors import ProviderError, ConfigurationError

logger = logging.getLogger(__name__)

class GroqLLM(BaseLLM):
    """
    Groq implementation of the LLM provider.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ConfigurationError(
                "GROQ_API_KEY environment variable is not set. "
                "Please set it to use Ragforge."
            )
        
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            raise ProviderError(f"Failed to initialize Groq client: {str(e)}")

    def generate_response(self, prompt: str, system_prompt: str) -> str:
        """
        Generates a response using Groq API with retries.
        """
        retries = 0
        last_error = None

        while retries < settings.LLM_MAX_RETRIES:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=settings.LLM_MODEL,
                    temperature=0.1, # Low temperature for factual grounding
                )
                
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
