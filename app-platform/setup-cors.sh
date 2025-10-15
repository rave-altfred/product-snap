#!/bin/bash

# Configure CORS for DigitalOcean Spaces using AWS CLI
# This script sets up CORS to allow your frontend to access images

set -e

echo "🚀 Setting up CORS for DigitalOcean Spaces..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    echo -e "${YELLOW}Installing AWS CLI...${NC}"
    
    # Install AWS CLI using pip
    if command -v pip3 &> /dev/null; then
        pip3 install awscli
    elif command -v brew &> /dev/null; then
        brew install awscli
    else
        echo -e "${RED}❌ Please install AWS CLI manually:${NC}"
        echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
fi

echo -e "${GREEN}✓ AWS CLI is available${NC}"

# Get Spaces credentials from App Platform environment
echo -e "${BLUE}📋 Getting Spaces credentials from App Platform...${NC}"

APP_ID="07251f47-f75b-4ba6-87da-07ed5dcefb58"

# Extract S3 credentials from app spec
S3_ACCESS_KEY=$(doctl apps spec get $APP_ID --format yaml | grep -A 1 "key: S3_ACCESS_KEY" | grep "value:" | sed 's/.*value: //' | tr -d ' ')
S3_SECRET_KEY=$(doctl apps spec get $APP_ID --format yaml | grep -A 1 "key: S3_SECRET_KEY" | grep "value:" | sed 's/.*value: //' | tr -d ' ')
S3_ENDPOINT=$(doctl apps spec get $APP_ID --format yaml | grep -A 1 "key: S3_ENDPOINT" | grep "value:" | sed 's/.*value: //' | tr -d ' ')
S3_BUCKET="productsnap"

if [[ $S3_ACCESS_KEY == EV[* ]]; then
    echo -e "${RED}❌ Cannot extract encrypted credentials automatically${NC}"
    echo -e "${YELLOW}💡 Please set these environment variables manually:${NC}"
    echo "export AWS_ACCESS_KEY_ID=<your-spaces-access-key>"
    echo "export AWS_SECRET_ACCESS_KEY=<your-spaces-secret-key>"
    echo ""
    echo "You can find these keys in:"
    echo "DigitalOcean Console → Spaces → Settings → API Keys"
    echo ""
    echo -e "${YELLOW}Then run this script again.${NC}"
    
    # Check if they're already set
    if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
        exit 1
    else
        echo -e "${GREEN}✓ Found AWS credentials in environment${NC}"
    fi
else
    # Set AWS CLI environment variables
    export AWS_ACCESS_KEY_ID=$S3_ACCESS_KEY
    export AWS_SECRET_ACCESS_KEY=$S3_SECRET_KEY
fi

# Extract region from endpoint
REGION=$(echo $S3_ENDPOINT | sed 's/https:\/\///' | sed 's/\.digitaloceanspaces\.com//')

echo -e "${BLUE}📍 Configuration:${NC}"
echo "  Endpoint: $S3_ENDPOINT"
echo "  Bucket: $S3_BUCKET"
echo "  Region: $REGION"

# Configure AWS CLI for DigitalOcean Spaces
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID" --profile spaces
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY" --profile spaces
aws configure set region "$REGION" --profile spaces

echo -e "${YELLOW}🔧 Applying CORS configuration...${NC}"

# Apply CORS configuration
aws s3api put-bucket-cors \
    --bucket "$S3_BUCKET" \
    --cors-configuration file://cors-config.json \
    --endpoint-url "$S3_ENDPOINT" \
    --profile spaces

echo -e "${GREEN}✅ CORS configuration applied successfully!${NC}"

# Verify CORS configuration
echo -e "${BLUE}🔍 Verifying CORS configuration...${NC}"
aws s3api get-bucket-cors \
    --bucket "$S3_BUCKET" \
    --endpoint-url "$S3_ENDPOINT" \
    --profile spaces \
    --output json

echo -e "${GREEN}🎉 CORS setup complete!${NC}"
echo -e "${YELLOW}💡 Your frontend should now be able to load images from Spaces.${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Refresh your browser"
echo "2. Check the Library page"
echo "3. Images should now load properly!"