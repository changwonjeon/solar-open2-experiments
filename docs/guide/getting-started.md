---
type: Guide
title: Getting Started with Solar Open2
description: Initial setup and configuration for working with Solar Open2
tags: [guide, setup, beginner]
timestamp: 2026-07-17T00:00:00Z
---

# Getting Started with Solar Open 2

This guide walks you through setting up your environment to work with Solar Open 2 using Claude Code and Hermes Agent.

## Prerequisites

- Python 3.10+ installed
- Git installed
- Access to Claude Code CLI
- Access to Hermes Agent (if using)

## Setup Steps

### 1. Clone This Repository

```bash
git clone <repository-url>
cd _Upstage
```

### 2. Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt  # If requirements.txt exists
```

### 4. Configure Environment Variables

Create a `.env` file (not tracked by git):

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 5. Verify Installation

```bash
# Test basic functionality
python -c "import solar_open2; print('OK')"
```

## First Experiment

1. Navigate to `docs/experiments/`
2. Create a new experiment file using the template
3. Follow the experiment workflow

## Next Steps

- Read the [Model Reference](../reference/solar-open2.md)
- Review the [Experiment Templates](../templates/template-experiment.md)
- Check out example experiments in `docs/experiments/`

## Troubleshooting

### Common Issues

**Issue: Import errors**
- Ensure your virtual environment is activated
- Check that all dependencies are installed

**Issue: API key errors**
- Verify your API keys are set in `.env`
- Ensure the `.env` file is in the correct location

For more help, see the [Troubleshooting Guide](troubleshooting.md).
