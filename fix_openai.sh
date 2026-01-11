#!/bin/bash
# Script to fix OpenAI SDK compatibility issue

echo "Fixing OpenAI SDK compatibility issue..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "Upgrading OpenAI SDK to fix 'proxies' error..."
pip install --upgrade "openai>=1.55.3"

echo ""
echo "Checking installed version..."
python3 -c "import openai; print(f'OpenAI version: {openai.__version__}')" 2>/dev/null || echo "OpenAI not installed"

echo ""
echo "Done! Try running test_credentials.py again."

