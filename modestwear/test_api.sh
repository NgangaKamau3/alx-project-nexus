#!/bin/bash
# API Endpoint Test Script for ModestWear

BASE_URL="http://localhost:8000"
echo "Testing ModestWear API at $BASE_URL"
echo "======================================"

# Test 1: Health Check
echo -e "\n1. Health Check"
curl -s $BASE_URL/health/ | python -m json.tool

# Test 2: Get Categories
echo -e "\n\n2. Get Categories"
curl -s $BASE_URL/catalog/items/categories/ | python -m json.tool

# Test 3: Get Products
echo -e "\n\n3. Get Products"
curl -s $BASE_URL/catalog/items/products/ | python -m json.tool

# Test 4: Register User
echo -e "\n\n4. Register User"
curl -s -X POST $BASE_URL/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }' | python -m json.tool

echo -e "\n\n======================================"
echo "API Tests Complete!"
