import re
from typing import Any, Dict, Optional
from .base import Guard, GuardResponse, GuardResult

class PIIDetectorGuard(Guard):
    PII_PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.action = self.config.get('action', 'warn')
    
    @property
    def name(self) -> str:
        return "pii_detector"
    
    def _detect_pii(self, text: str) -> Dict[str, list]:
        findings = {}
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                findings[pii_type] = matches
        return findings
    
    def check_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        findings = self._detect_pii(prompt)
        
        if not findings:
            return GuardResponse(result=GuardResult.ALLOW)
        
        if self.action == 'block':
            return GuardResponse(
                result=GuardResult.BLOCK,
                reason=f"PII detected: {list(findings.keys())}",
                confidence=0.9,
                metadata={"pii_types": list(findings.keys())}
            )
        else:
            return GuardResponse(
                result=GuardResult.WARN,
                reason=f"PII detected: {list(findings.keys())}",
                confidence=0.9,
                metadata={"pii_types": list(findings.keys())}
            )
    
    def check_output(self, response: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        return self.check_input(response, context)

class InjectionDetectorGuard(Guard):
    INJECTION_PATTERNS = [
        re.compile(r"(?i)\b(ignore|forget|disregard)\s+(previous|above|earlier|all)\s+(instructions?|prompts?|rules?)"),
        re.compile(r"(?i)\b(system|assistant)[:]\s*"),
        re.compile(r"(?i)\b(jailbreak|roleplay as|pretend to be)"),
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sensitivity = self.config.get('sensitivity', 'medium')
    
    @property  
    def name(self) -> str:
        return "injection_detector"
    
    def check_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        matches = []
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(prompt):
                matches.append(pattern.pattern[:50])
        
        if matches:
            return GuardResponse(
                result=GuardResult.BLOCK,
                reason=f"Potential prompt injection detected",
                confidence=0.8,
                metadata={"matched_patterns": matches}
            )
        
        return GuardResponse(result=GuardResult.ALLOW)
    
    def check_output(self, response: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        return GuardResponse(result=GuardResult.ALLOW)

class RBACGuard(Guard):
    """Role-Based Access Control for tool/API usage"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.role_permissions = self.config.get('role_permissions', {})
        self.default_role = self.config.get('default_role', 'user')
    
    @property
    def name(self) -> str:
        return "rbac_guard"
    
    def check_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        # Extract user role from context
        user_role = None
        if context and 'context' in context:
            user_role = context['context'].get('role', self.default_role)
        
        if not user_role:
            user_role = self.default_role
        
        # Check for tool/API usage patterns
        restricted_patterns = [
            r'delete\s+\w+',
            r'drop\s+table',
            r'sudo\s+',
            r'admin\s+',
            r'execute\s+',
        ]
        
        detected_actions = []
        for pattern in restricted_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                detected_actions.append(pattern)
        
        if detected_actions:
            allowed_actions = self.role_permissions.get(user_role, [])
            
            # Check if user has permission for detected actions
            for action in detected_actions:
                if not any(allowed in action for allowed in allowed_actions):
                    return GuardResponse(
                        result=GuardResult.BLOCK,
                        reason=f"Role '{user_role}' not authorized for action: {action}",
                        confidence=0.9,
                        metadata={"role": user_role, "blocked_action": action}
                    )
        
        return GuardResponse(result=GuardResult.ALLOW)
    
    def check_output(self, response: str, context: Optional[Dict[str, Any]] = None) -> GuardResponse:
        return GuardResponse(result=GuardResult.ALLOW)
