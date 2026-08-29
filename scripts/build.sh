#!/bin/bash
# Build script for container images

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building URL Shortener Docker Images${NC}"
echo -e "${GREEN}========================================${NC}"

# Get version from environment or use latest
VERSION=${VERSION:-latest}
REGISTRY=${REGISTRY:-}

# Build production image
echo -e "${YELLOW}Building production image...${NC}"
docker build -f docker/Dockerfile -t url-shortener:${VERSION} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Production image built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build production image${NC}"
    exit 1
fi

# Build development image
echo -e "${YELLOW}Building development image...${NC}"
docker build -f docker/Dockerfile.dev -t url-shortener:dev .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Development image built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build development image${NC}"
    exit 1
fi

# Tag for registry if specified
if [ -n "$REGISTRY" ]; then
    echo -e "${YELLOW}Tagging for registry: $REGISTRY${NC}"
    docker tag url-shortener:${VERSION} $REGISTRY/url-shortener:${VERSION}
    docker tag url-shortener:dev $REGISTRY/url-shortener:dev
    docker tag url-shortener:${VERSION} $REGISTRY/url-shortener:latest
    
    echo -e "${YELLOW}Pushing to registry...${NC}"
    docker push $REGISTRY/url-shortener:${VERSION}
    docker push $REGISTRY/url-shortener:dev
    docker push $REGISTRY/url-shortener:latest
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Images pushed to registry${NC}"
    else
        echo -e "${RED}✗ Failed to push images${NC}"
        exit 1
    fi
fi

# Show image info
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Images created:"
docker images | grep url-shortener

echo -e "\n${GREEN}To run:${NC}"
echo "  docker-compose up -d"
echo "  docker run -p 8000:8000 url-shortener:${VERSION}"