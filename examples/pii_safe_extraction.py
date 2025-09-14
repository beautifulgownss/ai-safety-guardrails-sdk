#!/usr/bin/env python3
"""
Demo: PII-Safe Data Extraction
Shows how to safely extract structured data while protecting sensitive information.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from safety_sdk import safe_llm, SafetyConfig, SafetyException, PIIDetectorGuard

# Mock LLM that might leak PII in responses
class DataExtractionLLM:
    def extract_contact_info(self, text, **kwargs):
        # Simulate extraction that might include PII
        if "john@company.com" in text.lower():
            return {
                "content": '{"name": "John Smith", "email": "john@company.com", "phone": "555-123-4567", "role": "engineer"}'
            }
        else:
            return {"content": '{"name": "Unknown", "email": "not_found", "role": "unknown"}'}

def demo_pii_safe_extraction():
    print("=== PII-Safe Data Extraction Demo ===\n")
    
    # Configure strict PII protection
    guards = [
        PIIDetectorGuard({
            'action': 'block',  # Block any response containing PII
        })
    ]
    
    config = SafetyConfig(
        guards=guards,
        user_id="data_analyst_001",
        role="analyst",
        fail_open=False  # Strict mode - block if unsafe
    )
    
    llm = DataExtractionLLM()
    
    @safe_llm(config)
    def safe_extract_contacts(text, **kwargs):
        return llm.extract_contact_info(text, **kwargs)
    
    # Test cases
    test_cases = [
        {
            "name": "Clean business card",
            "input": "John Smith, Senior Engineer, TechCorp Inc.",
            "should_pass": True
        },
        {
            "name": "Business card with PII",
            "input": "Contact John Smith at john@company.com or call 555-123-4567",
            "should_pass": False
        }
    ]
    
    for case in test_cases:
        print(f"Testing: {case['name']}")
        print(f"Input: {case['input']}")
        
        try:
            result = safe_extract_contacts(case['input'])
            print(f"✓ Extraction successful: {result['content'][:100]}...")
            
            if not case['should_pass']:
                print("  ⚠️  WARNING: This should have been blocked!")
                
        except SafetyException as e:
            print(f"✗ Extraction blocked: {e.guard_responses[0].reason}")
            
            if case['should_pass']:
                print("  ⚠️  WARNING: This should have passed!")
            else:
                print("  ✓ Correctly protected PII")
        
        print()

if __name__ == "__main__":
    demo_pii_safe_extraction()
