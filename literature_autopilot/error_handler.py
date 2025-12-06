import json
import time
import random
from typing import Dict, Any, Callable, Optional

class RobustErrorHandler:
    """Centralized error handling with recovery strategies."""
    
    @staticmethod
    def handle_json_error(response_text: str) -> Dict[str, Any]:
        """Try to repair malformed JSON."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Strategy 1: Extract JSON from markdown code blocks
            if "```json" in response_text:
                try:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except Exception:
                    pass
            
            # Strategy 2: Find first { and last }
            try:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except Exception:
                pass
            
            # Strategy 3: Common LLM mistakes (trailing commas)
            # This is harder to fix safely without regex, but we can try simple things
            # For now, just log and return empty or raise
            print(f"Failed to parse JSON from response: {response_text[:100]}...")
            return {}

    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3, initial_delay: float = 1.0, 
                          exceptions_to_catch: tuple = (Exception,)) -> Any:
        """Retry a function with exponential backoff."""
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func()
            except exceptions_to_catch as e:
                last_exception = e
                if attempt == max_retries - 1:
                    break
                
                # Add jitter
                sleep_time = delay * (1 + random.random() * 0.1)
                print(f"    Attempt {attempt + 1} failed ({str(e)}). Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
                delay *= 2
        
        print(f"    All {max_retries} attempts failed.")
        raise last_exception
