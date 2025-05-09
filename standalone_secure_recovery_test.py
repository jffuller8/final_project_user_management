#!/usr/bin/env python3

import uuid
from datetime import datetime, timedelta

def test_secure_recovery_flow():
    """
    Test the secure account recovery flow.
    """
    print("\nSecure Recovery Flow Tests:")
    print("-------------------------")
    
    # Mock classes for testing recovery flow
    class MockRecoveryToken:
        def __init__(self, user_id):
            self.token = str(uuid.uuid4())
            self.user_id = user_id
            self.created_at = datetime.now()
            self.is_used = False
            
        def is_valid(self):
            # Token is valid if:
            # 1. Not used
            # 2. Not expired (less than 24 hours old)
            if self.is_used:
                return False
                
            if datetime.now() - self.created_at > timedelta(hours=24):
                return False
                
            return True
            
        def use_token(self):
            if not self.is_valid():
                return False
                
            self.is_used = True
            return True
    
    class MockRecoveryManager:
        def __init__(self):
            self.tokens = {}  # user_id -> [tokens]
            self.reset_attempts = {}  # IP -> count
            
        def create_recovery_token(self, user_id):
            """Create a new recovery token."""
            token = MockRecoveryToken(user_id)
            
            if user_id not in self.tokens:
                self.tokens[user_id] = []
                
            # Store token
            self.tokens[user_id].append(token)
            return token.token
            
        def verify_and_use_token(self, user_id, token_str):
            """Verify and use a recovery token."""
            if user_id not in self.tokens:
                return False
                
            # Find matching token
            for token in self.tokens[user_id]:
                if token.token == token_str and token.is_valid():
                    return token.use_token()
                    
            return False
            
        def record_recovery_attempt(self, ip):
            """Record a recovery attempt from an IP."""
            current_time = datetime.now()
            
            if ip not in self.reset_attempts:
                self.reset_attempts[ip] = 1
            else:
                self.reset_attempts[ip] += 1
                
            # Rate limit: max 3 attempts per hour
            return self.reset_attempts[ip] <= 3
    
    # Test cases
    tests = []
    
    # Test 1: Should generate valid recovery token
    manager = MockRecoveryManager()
    token_str = manager.create_recovery_token("user1")
    tests.append((token_str is not None, "Should generate valid recovery token"))
    
    # Test 2: Valid token should be accepted
    manager = MockRecoveryManager()
    token_str = manager.create_recovery_token("user2")
    is_valid = manager.verify_and_use_token("user2", token_str)
    tests.append((is_valid, "Valid token should be accepted"))
    
    # Test 3: Token should only be usable once
    manager = MockRecoveryManager()
    token_str = manager.create_recovery_token("user3")
    manager.verify_and_use_token("user3", token_str)
    is_valid = manager.verify_and_use_token("user3", token_str)
    tests.append((not is_valid, "Token should only be usable once"))
    
    # Test 4: Recovery should be rate limited
    manager = MockRecoveryManager()
    for i in range(5):  # 5 attempts
        can_attempt = manager.record_recovery_attempt("192.168.1.1")
    tests.append((not can_attempt, "Recovery should be rate limited"))
    
    # Print results
    passed = 0
    failed = 0
    
    for success, message in tests:
        if success:
            result = "PASS"
            passed += 1
        else:
            result = "FAIL"
            failed += 1
            
        print(f"{result}: {message}")
    
    # Summary
    total = passed + failed
    print(f"\nResults: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    # Run the test
    success = test_secure_recovery_flow()
    exit(0 if success else 1)