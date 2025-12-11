#!/bin/bash
# Activate virtual environment for AI Job Source Agent

cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "📦 Installed packages:"
pip list | grep -E "(requests|beautifulsoup4|python-dotenv|lxml)"
echo ""
echo "🚀 Ready to run the agent!"
echo "   Run: python job_source_agent.py"
echo "   Or: python example_usage.py"

