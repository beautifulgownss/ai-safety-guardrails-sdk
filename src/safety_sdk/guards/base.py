from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

class GuardResult(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"

@dataclass
class GuardResponse:
    result: GuardResult
    reason: Optional[str] = None
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

class Guard(ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
    
    @abstractmethod
    def check_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        pass
    
    @abstractmethod
    def check_output(self, response: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

class GuardChain:
    def __init__(self, guards: List[Guard]):
        self.guards = [g for g in guards if g.enabled]
    
    def check_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[GuardResponse]:
        responses = []
        for guard in self.guards:
            try:
                response = guard.check_input(prompt, context)
                responses.append(response)
                if response.result == GuardResult.BLOCK:
                    break
            except Exception as e:
                responses.append(GuardResponse(
                    result=GuardResult.WARN,
                    reason=f"Guard {guard.name} failed: {str(e)}",
                    confidence=0.0
                ))
        return responses
    
    def check_output(self, response: str, context: Optional[Dict[str, Any]] = None) -> List[GuardResponse]:
        guard_responses = []
        for guard in self.guards:
            try:
                guard_response = guard.check_output(response, context)
                guard_responses.append(guard_response)
                if guard_response.result == GuardResult.BLOCK:
                    break
            except Exception as e:
                guard_responses.append(GuardResponse(
                    result=GuardResult.WARN,
                    reason=f"Guard {guard.name} failed: {str(e)}",
                    confidence=0.0
                ))
        return guard_responses
