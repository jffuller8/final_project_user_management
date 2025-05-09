#!/usr/bin/env python3

from datetime import datetime, timedelta

def test_account_auto_unlock():
    """
    Test that locked accounts automatically unlock after the specified period.
    """
    print("\nAccount Auto-Unlock Tests:")
    print("-------------------------")
    
    # Mock user class for testing auto-unlock functionality
    class MockUser:
        def __init__(self, is_locked=False, locked_at=None):
            self.is_locked = is_locked
            self.locked_at = locked_at
            self.unlock_after_hours = 1
            
        def should_auto_unlock(self):
            if not self.is_locked or not self.locked_at:
                return False
                
            # Check if enough time has passed
            unlock_time = self.locked_at + timedelta(hours=self.unlock_after_hours)
            return datetime.now() > unlock_time
            
        def check_and_unlock(self):
            if self.should_auto_unlock():
                self.is_locked = False
                self.locked_at = None
                return True
            return False
    
    # Test cases
    tests = []
    
    # Test 1: Recently locked account should not auto-unlock
    recent_time = datetime.now() - timedelta(minutes=30)  # 30 minutes ago
    user = MockUser(is_locked=True, locked_at=recent_time)
    unlocked = user.check_and_unlock()
    tests.append((not unlocked, "Recently locked account should not auto-unlock"))
    
    # Test 2: Account locked more than 1 hour ago should auto-unlock
    old_time = datetime.now() - timedelta(hours=2)  # 2 hours ago
    user = MockUser(is_locked=True, locked_at=old_time)
    unlocked = user.check_and_unlock()
    tests.append((unlocked, "Account locked more than 1 hour ago should auto-unlock"))
    
    # Test 3: Account should be unlocked after auto-unlock
    old_time = datetime.now() - timedelta(hours=2)
    user = MockUser(is_locked=True, locked_at=old_time)
    user.check_and_unlock()
    tests.append((not user.is_locked, "Account should be unlocked after auto-unlock"))
    
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
    success = test_account_auto_unlock()
    exit(0 if success else 1)