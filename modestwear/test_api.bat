@echo off
REM API Endpoint Test Script for ModestWear (Windows)

set BASE_URL=https://modestwear.onrender.com
echo Testing ModestWear API at %BASE_URL%
echo ======================================

echo.
echo 1. Health Check
curl -s %BASE_URL%/health/

echo.
echo.
echo 2. Get Categories
curl -s %BASE_URL%/catalog/items/categories/

echo.
echo.
echo 3. Get Products
curl -s %BASE_URL%/catalog/items/products/

echo.
echo.
echo 4. Register User
curl -s -X POST %BASE_URL%/api/auth/register/ -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"username\":\"testuser\",\"password\":\"SecurePass123!\",\"first_name\":\"Test\",\"last_name\":\"User\"}"

echo.
echo.
echo ======================================
echo API Tests Complete!
pause
