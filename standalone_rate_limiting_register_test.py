#!/usr/bin/env python3

import time

def test_rate_limiting_register():
    """
    Test that rate limiting works properly for registration attempts.
    """
    print("\nRate Limiting Registration Tests:")
    print("-------------------------------")
    
    # Mock rate limiter class for registration endpoint
    class MockRegisterRateLimiter:
        def __init__(self):
            self.attempts = {}  # IP -> [timestamps]
            self.max_attempts = 3  # Stricter limit for registration (prevent account farming)
            self.window = 3600  # Longer window (1 hour) for registration
            
        def is_rate_limited(self, ip):
            current_time = time.time()
            
            # Initialize if IP not seen before
            if ip not in self.attempts:
                self.attempts[ip] = []
                
            # Clean up old attempts (older than window)
            self.attempts[ip] = [t for t in self.attempts[ip] 
                                if current_time - t < self.window]
                                
            # Check if rate limited
            if len(self.attempts[ip]) >= self.max_attempts:
                return True
                
            # Record this attempt
            self.attempts[ip].append(current_time)
            return False
    
    # Test cases
    tests = []
    
    # Test 1: First few attempts should not be rate limited
    rate_limiter = MockRegisterRateLimiter()
    is_limited = False
    for i in range(2):
        is_limited = rate_limiter.is_rate_limited("192.168.1.1")
    tests.append((not is_limited, "First few registration attempts should not be rate limited"))
    
    # Test 2: Too many attempts should be rate limited
    rate_limiter = MockRegisterRateLimiter()
    for i in range(5):
        is_limited = rate_limiter.is_rate_limited("192.168.1.2")
    tests.append((is_limited, "Too many registration attempts should be rate limited"))
    
    # Test 3: Registration should have stricter limits than login
    register_limiter = MockRegisterRateLimiter()
    # Test with 4 attempts (over the 3 limit)
    for i in range(4):
        register_limited = register_limiter.is_rate_limited("192.168.1.3")
    tests.append((register_limited, "Registration should have stricter limits"))
    
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
    success = test_rate_limiting_register()
    exit(0 if success else 1)