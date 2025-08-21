#!/usr/bin/env python3
"""
Simple API test script for the AI Document Organizer backend
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_stats():
    """Test stats endpoint"""
    print("Testing stats endpoint...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_categories():
    """Test categories endpoint"""
    print("Testing categories endpoint...")
    response = requests.get(f"{BASE_URL}/categories")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_documents():
    """Test documents endpoint"""
    print("Testing documents endpoint...")
    response = requests.get(f"{BASE_URL}/documents")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_analytics():
    """Test analytics endpoint"""
    print("Testing analytics endpoint...")
    response = requests.get(f"{BASE_URL}/analytics")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_search():
    """Test search endpoint"""
    print("Testing search endpoint...")
    response = requests.get(f"{BASE_URL}/search/recent?limit=5")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_upload():
    """Test upload endpoint"""
    print("Testing upload endpoint...")
    # Create a simple text file for testing
    test_file_path = Path("test_upload.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test document for upload testing.")
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"files": ("test_upload.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Clean up test file
        test_file_path.unlink()
        
    except Exception as e:
        print(f"Upload test failed: {e}")
        # Clean up test file if it exists
        if test_file_path.exists():
            test_file_path.unlink()

def main():
    """Run all tests"""
    print("=== AI Document Organizer API Tests ===\n")
    
    try:
        test_health()
        test_stats()
        test_categories()
        test_documents()
        test_analytics()
        test_search()
        test_upload()
        
        print("✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
