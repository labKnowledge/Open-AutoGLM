#!/bin/bash
# Quick start script to fetch and analyze Slack conversations

set -e

echo "========================================="
echo "Slack Channel Analysis Tool"
echo "========================================="
echo ""

# Check if SLACK_BOT_TOKEN is set
if [ -z "$SLACK_BOT_TOKEN" ]; then
    echo "❌ Error: SLACK_BOT_TOKEN environment variable is not set"
    echo ""
    echo "Please set your Slack Bot Token in one of the following ways:"
    echo "1. Add it to Cursor Dashboard (Cloud Agents > Secrets)"
    echo "2. Export it in your shell: export SLACK_BOT_TOKEN='xoxb-your-token'"
    echo ""
    echo "See slack_analysis/README.md for detailed setup instructions."
    exit 1
fi

echo "✓ SLACK_BOT_TOKEN found"
echo ""

# Check if requests is installed
echo "Checking dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "Installing requests package..."
    pip install requests
}
echo "✓ Dependencies ready"
echo ""

# Fetch data
echo "========================================="
echo "Step 1: Fetching Slack conversations..."
echo "========================================="
python3 slack_analysis/fetch_slack_data.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to fetch Slack data"
    exit 1
fi

echo ""
echo "✓ Data fetched successfully"
echo ""

# Analyze data
echo "========================================="
echo "Step 2: Analyzing conversations..."
echo "========================================="
python3 slack_analysis/analyze_conversations.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to analyze data"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ Analysis Complete!"
echo "========================================="
echo ""
echo "Generated files:"
echo "  📄 slack_analysis/conversations_data.json - Raw conversation data"
echo "  📊 slack_analysis/analysis_report.txt - Human-readable report"
echo "  📈 slack_analysis/analysis_data.json - Structured analysis data"
echo ""
echo "View the report:"
echo "  cat slack_analysis/analysis_report.txt"
echo ""
