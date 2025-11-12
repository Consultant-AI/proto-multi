#!/bin/bash
# Quick deployment status check

echo "Checking deployment status..."
echo ""

if [ -f /tmp/deployment_monitor.log ]; then
    echo "Latest monitoring output:"
    tail -5 /tmp/deployment_monitor.log
    echo ""

    if grep -q "DEPLOYMENT COMPLETE" /tmp/deployment_monitor.log; then
        echo "✅ DEPLOYMENT IS READY!"
        echo ""
        echo "Access at: http://46.224.25.170/"
        echo "Login: admin / anthropic2024"
        echo ""
        echo "Next step: Create snapshot for fast restores!"
    else
        echo "⏳ Still deploying... Docker is building from local files"
        echo "   This takes ~10-12 minutes for first deployment"
        echo ""
        echo "   Run this script again in a few minutes"
    fi
else
    echo "❌ Monitoring log not found"
fi
