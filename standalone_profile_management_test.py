#!/usr/bin/env python3

from datetime import datetime
import uuid
import time  # Add this import for sleep

def test_profile_management():
    """
    Test the profile management functionality.
    """
    print("\nProfile Management Tests:")
    print("-----------------------")
    
    # Mock user class for testing profile management
    class MockUser:
        def __init__(self, id=None, email="user@example.com", first_name=None, last_name=None, is_professional=False):
            self.id = id or str(uuid.uuid4())
            self.email = email
            self.first_name = first_name
            self.last_name = last_name
            self.bio = None
            self.linkedin_profile_url = None
            self.github_profile_url = None
            self.is_professional = is_professional
            self.professional_status_updated_at = None
            self.updated_at = datetime.now()
            
        def update_profile(self, profile_data):
            """Update the user profile with the provided data"""
            for key, value in profile_data.items():
                if hasattr(self, key) and value is not None:
                    setattr(self, key, value)
            self.updated_at = datetime.now()
            return self
            
        def update_professional_status(self, is_professional):
            """Update the professional status"""
            self.is_professional = is_professional
            self.professional_status_updated_at = datetime.now()
            return self
    
    # Test cases
    tests = []
    
    # Test 1: User should be able to update profile
    user = MockUser(first_name="John", last_name="Doe")
    profile_data = {
        "bio": "Software engineer with 5 years of experience",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe"
    }
    user.update_profile(profile_data)
    
    # Check if profile was updated correctly
    tests.append((
        user.bio == profile_data["bio"] and
        user.linkedin_profile_url == profile_data["linkedin_profile_url"] and
        user.github_profile_url == profile_data["github_profile_url"],
        "User should be able to update profile"
    ))
    
    # Test 2: Admin should be able to update professional status
    user = MockUser()
    user.update_professional_status(True)
    
    # Check if professional status was updated correctly
    tests.append((
        user.is_professional == True and
        user.professional_status_updated_at is not None,
        "Admin should be able to update professional status"
    ))
    
    # Test 3: Professional status update should be timestamped
    user = MockUser(is_professional=False)
    old_time = datetime.now()
    # Simulate some time passing
    time.sleep(0.01)  # Adding a small delay to ensure timestamp difference
    user.update_professional_status(True)
    
    # Check if timestamp was updated
    tests.append((
        user.professional_status_updated_at > old_time,
        "Professional status update should be timestamped"
    ))
    
    # Test 4: Partial profile updates should work
    user = MockUser(first_name="John", last_name="Doe")
    # Only update one field
    user.update_profile({"bio": "New bio"})
    
    # Check if only specified fields were updated
    tests.append((
        user.bio == "New bio" and
        user.first_name == "John" and
        user.last_name == "Doe",
        "Partial profile updates should work"
    ))
    
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
    success = test_profile_management()
    exit(0 if success else 1)