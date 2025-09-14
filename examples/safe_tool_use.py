#!/usr/bin/env python3
"""
Demo: Safe Tool Use with RBAC
Shows role-based access control for database and system operations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from safety_sdk import safe_llm, SafetyConfig, SafetyException, RBACGuard

class DatabaseLLM:
    """Simulates LLM with database/system access"""
    
    def execute_query(self, query, **kwargs):
        if "delete" in query.lower():
            return {"content": f"Executed: {query} - 50 rows affected"}
        elif "select" in query.lower():
            return {"content": f"Query result: [{query}] - 10 rows returned"}
        else:
            return {"content": f"Unknown query: {query}"}

def demo_rbac_protection():
    print("=== Safe Tool Use with RBAC Demo ===\n")
    
    # Define role-based permissions
    role_permissions = {
        'admin': ['delete', 'drop', 'sudo', 'admin', 'execute'],
        'developer': ['select', 'insert', 'update'],
        'analyst': ['select'],
        'user': []  # No special permissions
    }
    
    guards = [
        RBACGuard({
            'role_permissions': role_permissions,
            'default_role': 'user'
        })
    ]
    
    llm = DatabaseLLM()
    
    # Test different user roles
    test_cases = [
        {
            'role': 'admin',
            'query': 'DELETE FROM users WHERE inactive = true',
            'should_pass': True
        },
        {
            'role': 'developer', 
            'query': 'SELECT * FROM users ORDER BY created_date',
            'should_pass': True
        },
        {
            'role': 'analyst',
            'query': 'DELETE FROM logs WHERE date < "2023-01-01"',
            'should_pass': False
        },
        {
            'role': 'user',
            'query': 'DROP TABLE sensitive_data',
            'should_pass': False
        }
    ]
    
    for case in test_cases:
        print(f"Testing: {case['role']} role")
        print(f"Query: {case['query']}")
        
        # Configure SDK for this role
        config = SafetyConfig(
            guards=guards,
            user_id=f"user_{case['role']}",
            role=case['role']
        )
        
        @safe_llm(config)
        def safe_db_query(query, **kwargs):
            return llm.execute_query(query, **kwargs)
        
        try:
            result = safe_db_query(case['query'])
            print(f"✓ Query allowed: {result['content']}")
            
            if not case['should_pass']:
                print("  ⚠️  WARNING: This should have been blocked!")
                
        except SafetyException as e:
            print(f"✗ Query blocked: {e.guard_responses[0].reason}")
            
            if case['should_pass']:
                print("  ⚠️  WARNING: This should have been allowed!")
            else:
                print("  ✓ Correctly enforced RBAC")
        
        print()

if __name__ == "__main__":
    demo_rbac_protection()
