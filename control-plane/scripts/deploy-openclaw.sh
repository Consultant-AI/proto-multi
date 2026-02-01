#!/bin/bash
set -e

# Deploy OpenClaw tarball to S3
# New EC2 instances will download and install this version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLOUDBOT_DIR="$REPO_ROOT/cloudbot"
S3_BUCKET="s3://cloudbot-moltbot-assets"

echo "=== OpenClaw Deploy Script ==="
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo "ERROR: AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

# Build cloudbot
echo "1. Building cloudbot..."
cd "$CLOUDBOT_DIR"
npm run build

# Create tarball
echo ""
echo "2. Creating tarball..."
npm pack

# Find the created tarball
TARBALL=$(ls -t openclaw-*.tgz 2>/dev/null | head -1)
if [ -z "$TARBALL" ]; then
    echo "ERROR: No tarball found after npm pack"
    exit 1
fi

echo "   Created: $TARBALL"

# Upload to S3
echo ""
echo "3. Uploading to S3..."
aws s3 cp "$TARBALL" "$S3_BUCKET/openclaw.tgz"

echo ""
echo "=== Deploy Complete ==="
echo ""
echo "New EC2 instances will now use this version."
echo "Create a new instance from the dashboard to test."
