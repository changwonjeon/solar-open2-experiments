#!/bin/bash
# Setup script for Solar Open2 development environment
# This script sets up the basic environment for working with Solar Open2

set -e

echo "Setting up Solar Open2 development environment..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}Detected macOS${NC}"
    PKG_MANAGER="brew"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${YELLOW}Detected Linux${NC}"
    if command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
    else
        echo -e "${RED}Unsupported package manager${NC}"
        exit 1
    fi
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    echo -e "${GREEN}Python $PYTHON_VERSION found${NC}"
else
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.10+${NC}"
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ]]; then
    echo -e "${RED}Python 3.10+ is required. Current version: $PYTHON_VERSION${NC}"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install common dependencies
echo "Installing common dependencies..."
pip install python-dotenv
pip install requests
pip install pyyaml

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Solar Open2 API Configuration
SOLAR_API_KEY=your-api-key-here

# Upstage API Endpoint
SOLAR_API_ENDPOINT=https://api.upstage.ai/v1

# Model Configuration
SOLAR_MODEL=solar-10.7b-chat
SOLAR_MAX_TOKENS=4096
SOLAR_TEMPERATURE=0.7

# Claude Code Configuration (optional)
# ANTHROPIC_API_KEY=your-anthropic-api-key

# Hermes Agent Configuration (optional)
# HERMES_CONFIG_PATH=~/.hermes/config.yaml
EOF
    echo -e "${GREEN}.env file created${NC}"
    echo -e "${YELLOW}Please edit .env with your actual API keys${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Create directories if they don't exist
echo "Creating directory structure..."
mkdir -p _private/credentials
mkdir -p _private/secrets
mkdir -p _private/notes
mkdir -p docs/notes/{people,papers,projects,note,writing}
mkdir -p data/{datasets,results,benchmarks}
mkdir -p src/{scripts,examples}

echo -e "${GREEN}Directory structure created${NC}"

# Set permissions on _private directory
echo "Setting directory permissions..."
chmod 700 _private
chmod 700 _private/credentials
chmod 700 _private/secrets
chmod 700 _private/notes

# Create a test script
echo "Creating test script..."
cat > src/scripts/test-setup.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify environment setup"""

import os
import sys

def test_environment():
    """Test basic environment setup"""
    print("Testing environment setup...")

    # Test Python version
    print(f"Python version: {sys.version}")

    # Test environment variables
    api_key = os.environ.get("SOLAR_API_KEY")
    if api_key and api_key != "your-api-key-here":
        print(f"✓ SOLAR_API_KEY is set (hidden)")
    else:
        print("⚠ SOLAR_API_KEY not set or using default")

    # Test imports
    try:
        import dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv not installed")

    try:
        import requests
        print("✓ requests installed")
    except ImportError:
        print("✗ requests not installed")

    try:
        import yaml
        print("✓ pyyaml installed")
    except ImportError:
        print("✗ pyyaml not installed")

    print("\nEnvironment setup test complete!")

if __name__ == "__main__":
    test_environment()
EOF

chmod +x src/scripts/test-setup.py

# Create a simple example script
echo "Creating example script..."
cat > src/examples/simple-query.py << 'EOF'
#!/usr/bin/env python3
"""
Simple example of querying Solar Open2 API
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def query_solar(prompt: str, max_tokens: int = 512, temperature: float = 0.7):
    """
    Send a query to Solar Open2 API

    Args:
        prompt: The prompt to send
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature

    Returns:
        The API response
    """
    # This is a placeholder - implement actual API call based on your setup
    api_key = os.getenv("SOLAR_API_KEY")
    endpoint = os.getenv("SOLAR_API_ENDPOINT", "https://api.upstage.ai/v1")

    if not api_key or api_key == "your-api-key-here":
        return "Error: SOLAR_API_KEY not configured. Please set it in .env file."

    # Example using OpenAI-compatible API
    # import requests
    # response = requests.post(
    #     f"{endpoint}/chat/completions",
    #     headers={
    #         "Authorization": f"Bearer {api_key}",
    #         "Content-Type": "application/json"
    #     },
    #     json={
    #         "model": os.getenv("SOLAR_MODEL", "solar-10.7b-chat"),
    #         "messages": [{"role": "user", "content": prompt}],
    #         "max_tokens": max_tokens,
    #         "temperature": temperature
    #     }
    # )
    # return response.json()

    return f"Ready to query Solar Open2 with prompt: {prompt[:50]}..."

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Hello! Can you help me with Solar Open2?"

    result = query_solar(prompt)
    print(result)
EOF

chmod +x src/examples/simple-query.py

echo ""
echo "================================================"
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: source .venv/bin/activate"
echo "3. Test with: python src/scripts/test-setup.py"
echo "4. Try an example: python src/examples/simple-query.py"
echo ""
echo -e "${YELLOW}Remember: Never commit .env or _private/ to git!${NC}"
