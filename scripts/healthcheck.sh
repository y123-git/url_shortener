#!/bin/bash
# Health check script for URL Shortener

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Running Health Checks${NC}"
echo -e "${GREEN}========================================${NC}"

BASE_URL=${BASE_URL:-http://localhost:8000}
MAX_RETRIES=${MAX_RETRIES:-5}
RETRY_DELAY=${RETRY_DELAY:-3}

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local expected_status=${2:-200}
    local description=${3:-$endpoint}
    
    echo -e "${YELLOW}Checking $description...${NC}"
    
    for i in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL$endpoint)
        
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✓ $description is healthy (status: $response)${NC}"
            return 0
        else
            echo -e "${YELLOW}  Attempt $i/$MAX_RETRIES: Got status $response, expected $expected_status${NC}"
            sleep $RETRY_DELAY
        fi
    done
    
    echo -e "${RED}✗ $description failed after $MAX_RETRIES attempts${NC}"
    return 1
}

# 1. Health endpoint
check_endpoint "/health" 200 "Health endpoint"

# 2. Root endpoint
check_endpoint "/" 200 "Root endpoint"

# 3. Test URL shortening
echo -e "${YELLOW}Testing URL shortening...${NC}"
short_response=$(curl -s -X POST $BASE_URL/shorten \
    -H "Content-Type: application/json" \
    -d '{"original_url":"https://example.com/healthtest"}' 2>/dev/null)

if [ $? -eq 0 ]; then
    short_code=$(echo $short_response | grep -o '"short_code":"[^"]*' | cut -d'"' -f4)
    short_url=$(echo $short_response | grep -o '"short_url":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$short_code" ]; then
        echo -e "${GREEN}✓ URL shortening works${NC}"
        echo -e "  Short Code: $short_code"
        echo -e "  Short URL: $short_url"
    else
        echo -e "${RED}✗ URL shortening failed${NC}"
        echo -e "  Response: $short_response"
        exit 1
    fi
else
    echo -e "${RED}✗ URL shortening request failed${NC}"
    exit 1
fi

# 4. Test redirect
echo -e "${YELLOW}Testing redirect...${NC}"
if [ -n "$short_code" ]; then
    redirect_response=$(curl -s -o /dev/null -w "%{http_code}" -L $BASE_URL/$short_code)
    
    if [ "$redirect_response" = "200" ]; then
        echo -e "${GREEN}✓ Redirect works (status: $redirect_response)${NC}"
    else
        echo -e "${RED}✗ Redirect failed (status: $redirect_response)${NC}"
        exit 1
    fi
fi

# 5. Test analytics
echo -e "${YELLOW}Testing analytics...${NC}"
if [ -n "$short_code" ]; then
    analytics_response=$(curl -s $BASE_URL/analytics/$short_code)
    
    if [ $? -eq 0 ]; then
        click_count=$(echo $analytics_response | grep -o '"click_count":[0-9]*' | cut -d':' -f2)
        if [ -n "$click_count" ]; then
            echo -e "${GREEN}✓ Analytics works (clicks: $click_count)${NC}"
        else
            echo -e "${RED}✗ Analytics response invalid${NC}"
            echo -e "  Response: $analytics_response"
            exit 1
        fi
    else
        echo -e "${RED}✗ Analytics request failed${NC}"
        exit 1
    fi
fi

# 6. Test Redis cache
echo -e "${YELLOW}Testing Redis cache...${NC}"
if [ -n "$short_code" ]; then
    # First request (cache miss)
    time1=$(curl -s -o /dev/null -w "%{time_total}" $BASE_URL/$short_code)
    sleep 1
    # Second request (cache hit)
    time2=$(curl -s -o /dev/null -w "%{time_total}" $BASE_URL/$short_code)
    
    if (( $(echo "$time2 < $time1" | bc -l) )); then
        echo -e "${GREEN}✓ Redis cache is working (${time1}s → ${time2}s)${NC}"
    else
        echo -e "${YELLOW}⚠️  Cache performance not detected (${time1}s → ${time2}s)${NC}"
    fi
fi

# 7. Test database connection
echo -e "${YELLOW}Testing database connection...${NC}"
db_response=$(curl -s $BASE_URL/health)
db_status=$(echo $db_response | grep -o '"database":"[^"]*' | cut -d'"' -f4)

if [ "$db_status" = "connected" ]; then
    echo -e "${GREEN}✓ Database is connected${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    exit 1
fi

# 8. Performance test (simple)
echo -e "${YELLOW}Running performance test...${NC}"
if [ -n "$short_code" ]; then
    total_time=0
    for i in {1..10}; do
        time=$(curl -s -o /dev/null -w "%{time_total}" $BASE_URL/$short_code)
        total_time=$(echo "$total_time + $time" | bc -l)
    done
    avg_time=$(echo "scale=3; $total_time / 10" | bc -l)
    
    echo -e "${GREEN}✓ Average response time: ${avg_time}s${NC}"
    
    if (( $(echo "$avg_time < 0.05" | bc -l) )); then
        echo -e "${GREEN}✓ Performance is excellent (< 50ms)${NC}"
    elif (( $(echo "$avg_time < 0.1" | bc -l) )); then
        echo -e "${GREEN}✓ Performance is good (< 100ms)${NC}"
    elif (( $(echo "$avg_time < 0.5" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Performance could be better (${avg_time}s)${NC}"
    else
        echo -e "${RED}✗ Performance is slow (${avg_time}s)${NC}"
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All health checks passed!${NC}"
echo -e "${GREEN}========================================${NC}"

# Summary
echo -e "\n${BLUE}Summary:${NC}"
echo -e "  Service: ${BASE_URL}"
echo -e "  Status: Healthy"
echo -e "  Test URL: ${BASE_URL}/${short_code}"
echo -e "  Analytics: ${BASE_URL}/analytics/${short_code}"
echo -e "  API Docs: ${BASE_URL}/docs"