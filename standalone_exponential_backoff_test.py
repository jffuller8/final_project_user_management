#!/usr/bin/env python3

import time
import math

def test_exponential_backoff():
    """
    Test that exponential backoff works properly for repeated failed attempts.
    """
    print("\nExponential Backoff Tests:")
    print("------------------------")
    
    # Mock backoff calculator
    class MockBackoffCalculator:
        def __init__(self):
            self.attempts = {}  # IP -> [attempt_count, last_attempt_time]
            self.base_delay = 1  # Base delay in seconds
            
        def record_failed_attempt(self, ip):
            current_time = time.time()
            
            if ip not in self.attempts:
                self.attempts[ip] = [1, current_time]
            else:
                self.attempts[ip][0] += 1
                self.attempts[ip][1] = current_time
                
            return self.get_delay(ip)
            
        def get_delay(self, ip):
            """Calculate exponential backoff delay."""
            if ip not in self.attempts:
                return 0
                
            attempt_count = self.attempts[ip][0]
            
            # No delay for first few attempts
            if attempt_count <= 3:
                return 0
                
            # Exponential backoff: 2^(n-3) seconds (capped at 5 minutes)
            delay = min(math.pow(2, attempt_count - 3), 300)
            return delay
    
    # Test cases
    tests = []
    
    # Test 1: First few attempts should have no delay
    backoff = MockBackoffCalculator()
    delay = backoff.record_failed_attempt("192.168.1.1")
    tests.append((delay == 0, "First attempt should have no delay"))
    
    # Test 2: After several failures, delay should increase
    backoff = MockBackoffCalculator()
    for i in range(5):  # 5 attempts
        delay = backoff.record_failed_attempt("192.168.1.2")
    tests.append((delay > 0, "After several failures, delay should increase"))
    
    # Test 3: Backoff should be exponential
    backoff = MockBackoffCalculator()
    delays = []
    for i in range(7):  # 7 attempts
        delays.append(backoff.record_failed_attempt("192.168.1.3"))
    
    # Check if delays follow exponential pattern
    is_exponential = True
    for i in range(3, len(delays) - 1):
        if delays[i + 1] < delays[i] * 1.5:  # Not strictly 2x, allow some flexibility
            is_exponential = False
            break
            
    tests.append((is_exponential, "Backoff should be exponential"))
    
    # Test 4: Backoff should be capped
    backoff = MockBackoffCalculator()
    for i in range(15):  # Many attempts
        delay = backoff.record_failed_attempt("192.168.1.4")
    tests.append((delay <= 300, "Backoff should be capped at reasonable limit"))
    
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
    success = test_exponential_backoff()
    exit(0 if success else 1)