#!/bin/bash
# Setup script for Solar Open 2 development environment with uv
# This script sets up the basic environment for working with Solar Open 2 using uv

set -e

echo "Setting up Solar Open 2 development environment with uv..."
echo "=========================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}uv is not installed. Please install uv first:${NC}"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}uv $(uv --version) found${NC}"

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

# Create uv virtual environment
echo "Creating uv virtual environment..."
if [ ! -d ".venv" ]; then
    uv venv
    echo -e "${GREEN}uv virtual environment created${NC}"
else
    echo -e "${YELLOW}uv virtual environment already exists${NC}"
fi

# Install dependencies using uv
echo "Installing dependencies with uv..."
uv pip install python-dotenv requests pyyaml

# Create pyproject.toml if it doesn't exist (for uv project management)
if [ ! -f "pyproject.toml" ]; then
    echo "Creating pyproject.toml..."
    uv init --name upstage-solar-test --quiet
    echo -e "${GREEN}pyproject.toml created${NC}"
else
    echo -e "${YELLOW}pyproject.toml already exists${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Solar Open 2 API Configuration
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
mkdir -p docs/notes/{people,papers,projects,notes,writing}
mkdir -p data/{datasets,results,benchmarks}
mkdir -p src/{scripts,examples}
mkdir -p assets

echo -e "${GREEN}Directory structure created${NC}"

# Set permissions on _private directory
echo "Setting directory permissions..."
chmod 700 _private
chmod 700 _private/credentials
chmod 700 _private/secrets
chmod 700 _private/notes

# Activate the virtual environment for this session
echo ""
echo -e "${GREEN}Environment setup complete!${NC}"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run Python scripts:"
echo "  uv run python src/scripts/test-setup.py"
echo "  uv run python src/examples/simple-query.py"
echo ""
echo "To install additional packages:"
echo "  uv pip install <package-name>"
echo ""
echo "To add packages to pyproject.toml:"
echo "  uv add <package-name>"
echo ""
echo -e "${YELLOW}Remember: Never commit .env or _private/ to git!${NC}"
