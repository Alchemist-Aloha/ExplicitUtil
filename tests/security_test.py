
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path so we can import ExplicitUtil
sys.path.append(os.path.abspath("src"))

from ExplicitUtil.recursive_namer import run_namer_command

def test_security_injection():
    # Attempting injection via namer_config
    # In a vulnerable version with shell=True and string formatting,
    # this would execute the touch command.
    # With shell=False, this will be passed as a single argument to the python command.
    malicious_config = '"; touch /tmp/pwned_test; "'
    test_dir = Path(".")

    print(f"Testing with malicious config: {malicious_config}")

    # We mock subprocess.run to avoid actually trying to run 'python -m namer'
    # which might not be installed or might fail for other reasons.
    # But we want to see what it WOULD have run if it weren't mocked,
    # or just rely on the fact that with shell=False, injection is impossible.
    # Actually, to be sure, let's NOT mock it if we want to prove the fix,
    # but we don't want to rely on 'python' and 'namer' being there.

    # Better approach: verify that /tmp/pwned_test is NOT created.
    if os.path.exists("/tmp/pwned_test"):
        os.remove("/tmp/pwned_test")

    try:
        run_namer_command(test_dir, malicious_config)
    except Exception as e:
        print(f"Expected exception or error due to missing 'namer' module: {e}")

    if os.path.exists("/tmp/pwned_test"):
        print("VULNERABILITY STILL PRESENT!")
        os.remove("/tmp/pwned_test")
        return False
    else:
        print("Security test PASSED: No command injection detected.")
        return True

if __name__ == "__main__":
    if test_security_injection():
        sys.exit(0)
    else:
        sys.exit(1)
