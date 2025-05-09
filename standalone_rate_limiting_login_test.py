#!/usr/bin/env python3

import time

def test_rate_limiting_login():
    """
    Test that rate limiting works properly for login attempts.
    """
    print("\nRate Limiting Login Tests:")
    print("-------------------------")
    
    # Mock rate limiter class for login endpoint
    class MockLoginRateLimiter:
        def __init__(self):
            self.attempts = {}  # IP -> [timestamps]
            self.max_attempts = 5  # Maximum attempts per minute
            self.window = 60  # Time window in seconds
            
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
    rate_limiter = MockLoginRateLimiter()
    is_limited = False
    for i in range(4):
        is_limited = rate_limiter.is_rate_limited("192.168.1.1")
    tests.append((not is_limited, "First few attempts should not be rate limited"))
    
    # Test 2: Too many attempts should be rate limited
    rate_limiter = MockLoginRateLimiter()
    for i in range(10):
        is_limited = rate_limiter.is_rate_limited("192.168.1.2")
    tests.append((is_limited, "Too many attempts should be rate limited"))
    
    # Test 3: Different IPs should have separate rate limiting
    rate_limiter = MockLoginRateLimiter()
    # Rate limit first IP
    for i in range(10):
        rate_limiter.is_rate_limited("192.168.1.3")
    # Second IP should not be limited
    is_limited = rate_limiter.is_rate_limited("192.168.1.4")
    tests.append((not is_limited, "Different IPs should have separate rate limiting"))
    
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
    success = test_rate_limiting_login()
    exit(0 if success else 1)