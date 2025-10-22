#!/bin/bash
# Test script to verify all environment variables are properly set

echo "=================================="
echo "PERSEPTOR Environment Variables Test"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check environment variable
check_env_var() {
    local var_name=$1
    local expected_default=$2
    local actual_value=$(docker-compose exec -T backend printenv $var_name 2>/dev/null || echo "NOT_SET")
    
    echo -n "Checking $var_name... "
    if [ "$actual_value" != "NOT_SET" ]; then
        echo -e "${GREEN}✓${NC} Value: $actual_value"
        return 0
    else
        echo -e "${RED}✗${NC} Not set (expected: $expected_default)"
        return 1
    fi
}

echo "=== Backend Container Environment Variables ==="
check_env_var "BACKEND_HOST" "0.0.0.0"
check_env_var "BACKEND_PORT" "5000"
check_env_var "FLASK_ENV" "development"
check_env_var "TESSERACT_CMD" "/usr/bin/tesseract"
check_env_var "CHROME_BIN" "/usr/bin/chromium"
check_env_var "CHROMEDRIVER_PATH" "/usr/bin/chromedriver"
check_env_var "SIGMAHQ_BASE_URL" "https://github.com/SigmaHQ/sigma/blob/master"

echo ""
echo "=== Frontend Container Environment Variables ==="
NGINX_PORT=$(docker-compose exec -T frontend printenv NGINX_PORT 2>/dev/null || echo "NOT_SET")
BACKEND_SERVICE=$(docker-compose exec -T frontend printenv BACKEND_SERVICE 2>/dev/null || echo "NOT_SET")
FRONTEND_BACKEND_PORT=$(docker-compose exec -T frontend printenv BACKEND_PORT 2>/dev/null || echo "NOT_SET")

echo -n "Checking NGINX_PORT... "
if [ "$NGINX_PORT" != "NOT_SET" ]; then
    echo -e "${GREEN}✓${NC} Value: $NGINX_PORT"
else
    echo -e "${RED}✗${NC} Not set"
fi

echo -n "Checking BACKEND_SERVICE... "
if [ "$BACKEND_SERVICE" != "NOT_SET" ]; then
    echo -e "${GREEN}✓${NC} Value: $BACKEND_SERVICE"
else
    echo -e "${RED}✗${NC} Not set"
fi

echo -n "Checking BACKEND_PORT (frontend)... "
if [ "$FRONTEND_BACKEND_PORT" != "NOT_SET" ]; then
    echo -e "${GREEN}✓${NC} Value: $FRONTEND_BACKEND_PORT"
else
    echo -e "${RED}✗${NC} Not set"
fi

echo ""
echo "=== Nginx Configuration Test ==="
echo "Generated nginx config:"
docker-compose exec -T frontend cat /etc/nginx/conf.d/default.conf | grep -E "listen|proxy_pass" | head -5

echo ""
echo "=== Backend Configuration Test ==="
echo "Testing if backend is using environment variables..."
docker-compose exec -T backend python -c "import os; print(f'BACKEND_HOST: {os.environ.get(\"BACKEND_HOST\")}'); print(f'BACKEND_PORT: {os.environ.get(\"BACKEND_PORT\")}'); print(f'TESSERACT_CMD: {os.environ.get(\"TESSERACT_CMD\")}')"

echo ""
echo "=== Docker Network Test ==="
echo "Testing backend connectivity from frontend..."
docker-compose exec -T frontend ping -c 1 backend > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Backend is reachable from frontend via Docker network"
else
    echo -e "${RED}✗${NC} Cannot reach backend from frontend"
fi

echo ""
echo "=== Port Exposure Test ==="
echo -n "Checking if backend port is exposed externally... "
if docker-compose ps | grep backend | grep -q "0.0.0.0:5000"; then
    echo -e "${RED}✗${NC} Backend is exposed externally (SECURITY RISK!)"
else
    echo -e "${GREEN}✓${NC} Backend is NOT exposed externally (correct)"
fi

echo -n "Checking if frontend port is exposed... "
if docker-compose ps | grep frontend | grep -q "0.0.0.0:"; then
    echo -e "${GREEN}✓${NC} Frontend is exposed externally"
else
    echo -e "${RED}✗${NC} Frontend is NOT exposed"
fi

echo ""
echo "=================================="
echo "Test Complete!"
echo "=================================="

