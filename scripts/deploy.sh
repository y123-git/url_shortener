#!/bin/bash
# Deployment script for different environments

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying URL Shortener${NC}"
echo -e "${GREEN}========================================${NC}"

# Check environment
ENV=${1:-development}
echo -e "${BLUE}Environment: $ENV${NC}"

# Validate environment
if [[ "$ENV" != "development" && "$ENV" != "staging" && "$ENV" != "production" ]]; then
    echo -e "${RED}Invalid environment: $ENV${NC}"
    echo "Usage: ./scripts/deploy.sh [development|staging|production]"
    exit 1
fi

# Load environment variables
if [ -f ".env.${ENV}" ]; then
    echo -e "${YELLOW}Loading .env.${ENV}...${NC}"
    export $(cat .env.${ENV} | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo -e "${YELLOW}Loading .env...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Deployment strategies
case $ENV in
    development)
        echo -e "${YELLOW}🐳 Starting development environment...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose/docker-compose.dev.yml up -d
        
        echo -e "${YELLOW}Waiting for services to be ready...${NC}"
        sleep 5
        
        echo -e "${GREEN}✓ Development environment started${NC}"
        echo -e "Access: http://localhost:8000"
        echo -e "Docs: http://localhost:8000/docs"
        echo -e "Adminer: http://localhost:8080"
        
        # Show logs
        echo -e "${YELLOW}Showing logs (Ctrl+C to exit)...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose/docker-compose.dev.yml logs -f
        ;;
        
    staging)
        echo -e "${YELLOW}🚀 Deploying to staging...${NC}"
        
        # Build and push images
        export REGISTRY=${REGISTRY:-staging-registry.example.com}
        ./scripts/build.sh
        
        # Apply Kubernetes manifests
        echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"
        kubectl config use-context staging
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/deployment.yaml
        kubectl apply -f k8s/service.yaml
        kubectl apply -f k8s/ingress.yaml
        
        # Wait for rollout
        echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
        kubectl rollout status deployment/url-shortener -n staging
        
        # Run smoke tests
        echo -e "${YELLOW}Running smoke tests...${NC}"
        ./scripts/healthcheck.sh
        
        echo -e "${GREEN}✓ Staging deployment complete${NC}"
        echo -e "Access: https://staging.urlshortener.example.com"
        ;;
        
    production)
        echo -e "${RED}⚠️  PRODUCTION DEPLOYMENT${NC}"
        echo -e "${RED}Are you sure you want to deploy to production? (yes/no)${NC}"
        read -r confirmation
        
        if [[ "$confirmation" != "yes" ]]; then
            echo -e "${YELLOW}Deployment cancelled${NC}"
            exit 0
        fi
        
        echo -e "${YELLOW}🚀 Deploying to production...${NC}"
        
        # Build and push images
        export REGISTRY=${REGISTRY:-prod-registry.example.com}
        export VERSION=$(git rev-parse --short HEAD)
        ./scripts/build.sh
        
        # Backup current deployment
        echo -e "${YELLOW}Creating backup of current deployment...${NC}"
        kubectl get deployment url-shortener -n production -o yaml > backup_$(date +%Y%m%d_%H%M%S).yaml
        
        # Apply Kubernetes manifests with production config
        echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"
        kubectl config use-context production
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/deployment.yaml
        kubectl apply -f k8s/service.yaml
        kubectl apply -f k8s/ingress.yaml
        kubectl apply -f k8s/hpa.yaml
        
        # Wait for rollout
        echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
        kubectl rollout status deployment/url-shortener -n production
        
        # Run comprehensive tests
        echo -e "${YELLOW}Running comprehensive tests...${NC}"
        ./scripts/healthcheck.sh
        
        # Verify metrics
        echo -e "${YELLOW}Checking metrics...${NC}"
        kubectl top pods -n production
        
        echo -e "${GREEN}✓ Production deployment complete${NC}"
        echo -e "Access: https://urlshortener.example.com"
        echo -e "Monitor: https://grafana.urlshortener.example.com"
        echo -e "Version: ${VERSION}"
        ;;
esac

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"