import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict

from .guards.base import GuardChain, GuardResult, GuardResponse

@dataclass
class SafetyConfig:
    """Configuration for safety-wrapped LLM calls"""
    guards: List[Any]  # List of Guard instances
    audit_enabled: bool = True
    fail_open: bool = False  # If true, allow calls when guards fail
    user_id: Optional[str] = None
    role: Optional[str] = None

@dataclass
class CallContext:
    """Context information for LLM calls"""
    call_id: str
    user_id: Optional[str] = None
    role: Optional[str] = None
    timestamp: float = None
    model: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class SafetyException(Exception):
    """Exception raised when safety guards block a request"""
    def __init__(self, message: str, guard_responses: List[GuardResponse]):
        super().__init__(message)
        self.guard_responses = guard_responses

def safe_llm(config: SafetyConfig):
    """Decorator to wrap LLM calls with safety guards"""
    
    def decorator(llm_function: Callable) -> Callable:
        guard_chain = GuardChain(config.guards)
        
        @wraps(llm_function)
        def wrapper(*args, **kwargs):
            call_id = str(uuid.uuid4())
            context = CallContext(
                call_id=call_id,
                user_id=config.user_id,
                role=config.role,
                model=kwargs.get('model', 'unknown')
            )
            
            # Extract prompt from common parameter names
            prompt = _extract_prompt(args, kwargs)
            
            # Pre-call guard checks
            input_responses = guard_chain.check_input(prompt, {"context": asdict(context)})
            blocked_inputs = [r for r in input_responses if r.result == GuardResult.BLOCK]
            
            if blocked_inputs and not config.fail_open:
                raise SafetyException(
                    f"Request blocked by guards: {[r.reason for r in blocked_inputs]}", 
                    input_responses
                )
            
            # Make the actual LLM call
            try:
                start_time = time.time()
                response = llm_function(*args, **kwargs)
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Extract response text
                response_text = _extract_response_text(response)
                
                # Post-call guard checks
                output_responses = guard_chain.check_output(response_text, {"context": asdict(context)})
                blocked_outputs = [r for r in output_responses if r.result == GuardResult.BLOCK]
                
                if blocked_outputs and not config.fail_open:
                    raise SafetyException(
                        f"Response blocked by guards: {[r.reason for r in blocked_outputs]}", 
                        output_responses
                    )
                
                # Simple logging to console for now
                if config.audit_enabled:
                    print(f"[AUDIT] {call_id[:8]} - {config.user_id} - success - {latency_ms}ms")
                
                return response
                
            except SafetyException:
                raise  # Re-raise safety exceptions
            except Exception as e:
                if config.fail_open:
                    return llm_function(*args, **kwargs)  # Retry without guards
                else:
                    raise e
        
        return wrapper
    return decorator

def _extract_prompt(args: tuple, kwargs: dict) -> str:
    """Extract prompt from various call patterns"""
    # OpenAI-style: messages=[{"role": "user", "content": "..."}]
    if 'messages' in kwargs:
        messages = kwargs['messages']
        if isinstance(messages, list) and messages:
            last_message = messages[-1]
            if isinstance(last_message, dict) and 'content' in last_message:
                return last_message['content']
    
    # Simple string prompt
    if 'prompt' in kwargs:
        return kwargs['prompt']
    
    # First positional argument
    if args:
        return str(args[0])
    
    return ""

def _extract_response_text(response: Any) -> str:
    """Extract text from various response formats"""
    # Simple dict with content
    if isinstance(response, dict) and 'content' in response:
        return response['content']
    
    # Simple string response
    if isinstance(response, str):
        return response
    
    return str(response)
