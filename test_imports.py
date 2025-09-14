import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from safety_sdk.guards.base import GuardResult, GuardResponse
    print("✓ Base guard imports work")
    
    from safety_sdk.guards.validators import PIIDetectorGuard
    print("✓ Validator imports work")
    
    from safety_sdk.wrapper import SafetyConfig
    print("✓ Wrapper imports work")
    
    print("All core imports successful!")
    
except ImportError as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
