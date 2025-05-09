#!/usr/bin/env python3

# Direct import of the function to test
from app.utils.security import validate_password_strength

def test_valid_password_acceptance():
    """Test that various valid passwords are accepted."""
    results = []
    
    # Test cases of valid passwords (all should pass)
    valid_passwords = [
        "StrongP@ss123", 
        "C0mpl3x!P@ssw0rd",
        "Sup3r$3cur3",
        "P@$$w0rd2023",
        "MyP@55w0rd!",
        "Abcd1234!@#$"
    ]
    
    # Run tests
    for password in valid_passwords:
        actual = validate_password_strength(password)
        success = actual == True
        results.append((success, f"Password '{password}' should be accepted", password, True, actual))
        
    # Print results
    passed = 0
    failed = 0
    
    print("\nValid Password Acceptance Tests:")
    print("-------------------------------")
    
    for success, message, password, expected, actual in results:
        if success:
            result = "PASS"
            passed += 1
        else:
            result = "FAIL"
            failed += 1
            
        print(f"{result}: {message}")
        print(f"  Expected: True, Actual: {actual}\n")
    
    # Summary
    total = passed + failed
    print(f"Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    # Run the test
    success = test_valid_password_acceptance()
    exit(0 if success else 1)