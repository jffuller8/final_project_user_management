#!/usr/bin/env python3

# Direct import of the function to test
from app.utils.security import validate_password_strength

def test_password_strength_validation():
    """Test that password strength validation works correctly."""
    results = []
    
    # Test cases
    test_cases = [
        ("StrongP@ss123", True, "Good password should pass"),
        ("Short1!", False, "Too short should fail"),
        ("password123!", False, "No uppercase should fail"),
        ("PASSWORD123!", False, "No lowercase should fail"),
        ("Password!", False, "No digits should fail"),
        ("Password123", False, "No special characters should fail")
    ]
    
    # Run tests
    for password, expected, message in test_cases:
        actual = validate_password_strength(password)
        success = actual == expected
        results.append((success, message, password, expected, actual))
        
    # Print results
    passed = 0
    failed = 0
    
    print("\nPassword Validation Tests:")
    print("-------------------------")
    
    for success, message, password, expected, actual in results:
        if success:
            result = "PASS"
            passed += 1
        else:
            result = "FAIL"
            failed += 1
            
        print(f"{result}: {message}")
        print(f"  Password: '{password}'")
        print(f"  Expected: {expected}, Actual: {actual}\n")
    
    # Summary
    total = passed + failed
    print(f"Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    # Run the test
    success = test_password_strength_validation()
    exit(0 if success else 1)