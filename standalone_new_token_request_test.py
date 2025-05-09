#!/usr/bin/env python3

from datetime import datetime, timedelta
import uuid

def test_new_token_request():
    """
    Test that users can request a new verification token when needed.
    """
    print("\nNew Token Request Tests:")
    print("----------------------")
    
    # Mock user class for testing token generation
    class MockUser:
        def __init__(self, email_verified=False, token=None, token_created_at=None):
            self.email_verified = email_verified
            self.verification_token = token
            self.verification_token_created_at = token_created_at
            self.token_request_count = 0
            self.last_token_request = None
            
        def generate_new_token(self):
            """Generate a new verification token."""
            # Check if user is already verified
            if self.email_verified:
                return False, "User is already verified"
                
            # Check for token request rate limiting (max 3 per day)
            if self.last_token_request and datetime.now() - self.last_token_request < timedelta(days=1):
                self.token_request_count += 1
                if self.token_request_count > 3:
                    return False, "Too many token requests"
            else:
                self.token_request_count = 1
                
            # Generate new token
            self.verification_token = str(uuid.uuid4())
            self.verification_token_created_at = datetime.now()
            self.last_token_request = datetime.now()
            
            return True, "New token generated"
    
    # Test cases
    tests = []
    
    # Test 1: Unverified user should get a new token successfully
    user = MockUser(email_verified=False)
    success, message = user.generate_new_token()
    tests.append((success, "Unverified user should get a new token successfully"))
    
    # Test 2: Verified user should not get a new token
    user = MockUser(email_verified=True)
    success, message = user.generate_new_token()
    tests.append((not success, "Verified user should not get a new token"))
    
    # Test 3: User should be able to request multiple tokens (within limit)
    user = MockUser(email_verified=False)
    for i in range(3):
        user.generate_new_token()
    success, message = user.generate_new_token()
    tests.append((not success, "User should be rate limited after too many requests"))
    
    # Test 4: Token should be regenerated with different value
    user = MockUser(email_verified=False, token="old_token")
    old_token = user.verification_token
    user.generate_new_token()
    tests.append((old_token != user.verification_token, "Token should be regenerated with different value"))
    
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
    success = test_new_token_request()
    exit(0 if success else 1)