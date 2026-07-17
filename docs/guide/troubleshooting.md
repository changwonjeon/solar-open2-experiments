---
type: Guide
title: Troubleshooting Guide
description: Common issues and solutions for working with Solar Open2 and related tools
tags: [guide, troubleshooting, help]
timestamp: 2026-07-17T00:00:00Z
---

# Troubleshooting Guide

This guide covers common issues encountered when working with Solar Open2, Claude Code, Hermes Agent, and the OKF knowledge base.

## Table of Contents

- [API and Connection Issues](#api-and-connection-issues)
- [Model Performance Issues](#model-performance-issues)
- [Claude Code Issues](#claude-code-issues)
- [Hermes Agent Issues](#hermes-agent-issues)
- [OKF Format Issues](#okf-format-issues)
- [Git and Version Control Issues](#git-and-version-control-issues)

## API and Connection Issues

### Connection Timeout

**Symptoms:**
```
Error: Connection timeout after 30 seconds
```

**Causes and Solutions:**

1. **Network connectivity issues**
   ```bash
   # Check internet connectivity
   ping api.upstage.ai
   
   # Check DNS resolution
   nslookup api.upstage.ai
   ```

2. **Firewall blocking**
   - Ensure outbound HTTPS (443) is allowed
   - Check corporate firewall settings
   - Try using a VPN if on restricted network

3. **API endpoint incorrect**
   ```bash
   # Verify endpoint URL
   curl -I https://api.upstage.ai/v1
   ```

### Authentication Errors

**Symptoms:**
```
Error: Invalid API key
Error: Authentication failed
```

**Solutions:**

1. **Verify API key format**
   ```bash
   # Check if key is set correctly
   echo $SOLAR_API_KEY
   
   # Key should look like: sk-xxxxxxxxxxxxxxxxxxxxxxxx
   # Not: ${SOLAR_API_KEY} or $SOLAR_API_KEY
   ```

2. **Check environment file**
   ```bash
   # Ensure .env file exists and is readable
   cat .env
   # Should contain: SOLAR_API_KEY=your-actual-key
   ```

3. **Regenerate API key** (if compromised or invalid)
   - Log into Upstage dashboard
   - Navigate to API Keys section
   - Generate new key
   - Update environment variables

### Rate Limiting

**Symptoms:**
```
Error: Rate limit exceeded
Error: 429 Too Many Requests
```

**Solutions:**

1. **Implement exponential backoff**
   ```python
   import time
   import random
   
   def api_call_with_retry(func, max_retries=5):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               wait_time = (2 ** attempt) + random.uniform(0, 1)
               time.sleep(wait_time)
       raise Exception("Max retries exceeded")
   ```

2. **Reduce request frequency**
   - Add delays between requests
   - Batch requests where possible
   - Cache responses

3. **Upgrade API plan** (if available)
   - Contact Upstage support
   - Consider enterprise plan for higher limits

### Model Not Found

**Symptoms:**
```
Error: Model 'solar-10.7b-chat' not found
```

**Solutions:**

1. **Verify model name**
   - Check Upstage documentation for correct model names
   - Ensure no typos (e.g., `solar-10.7b` vs `solar-10.7B`)

2. **Check model availability**
   ```bash
   # List available models
   curl -H "Authorization: Bearer $SOLAR_API_KEY" \
        https://api.upstage.ai/v1/models
   ```

3. **Update configuration**
   - Ensure config points to correct model
   - Check for deprecated model names

## Model Performance Issues

### Poor Quality Output

**Symptoms:**
- Nonsensical or irrelevant responses
- Frequent hallucinations
- Incoherent text generation

**Solutions:**

1. **Adjust temperature**
   ```python
   # Lower temperature for more focused output
   response = client.chat.completions.create(
       model="solar-10.7b-chat",
       messages=messages,
       temperature=0.3  # Lower for factual tasks
   )
   ```

2. **Improve prompts**
   - Be more specific about requirements
   - Provide examples (few-shot prompting)
   - Use clear structure and formatting

3. **Add system message**
   ```python
   messages = [
       {"role": "system", "content": "You are a helpful AI assistant. Provide concise, accurate answers."},
       {"role": "user", "content": "Your question here"}
   ]
   ```

4. **Check for context overflow**
   - Ensure input fits within context window
   - Summarize long inputs
   - Remove irrelevant information

### Repeated Responses

**Symptoms:**
- Model gets stuck in loops
- Repeats same phrases

**Solutions:**

1. **Adjust parameters**
   ```python
   response = client.chat.completions.create(
       model="solar-10.7b-chat",
       messages=messages,
       temperature=0.7,
       presence_penalty=0.5,  # Reduce repetition
       frequency_penalty=0.5  # Reduce word repetition
   )
   ```

2. **Set stop sequences**
   ```python
   response = client.chat.completions.create(
       model="solar-10.7b-chat",
       messages=messages,
       stop=["\n\n", " repetition", " loop"]
   )
   ```

3. **Limit response length**
   ```python
   response = client.chat.completions.create(
       model="solar-10.7b-chat",
       messages=messages,
       max_tokens=512  # Limit output length
   )
   ```

### Context Window Exceeded

**Symptoms:**
```
Error: Context length exceeded
Error: Input too long
```

**Solutions:**

1. **Summarize input**
   ```python
   # Create summary of long content
   summary_response = client.chat.completions.create(
       model="solar-10.7b-chat",
       messages=[{"role": "user", "content": f"Summarize this in 500 words: {long_text}"}]
   )
   ```

2. **Chunk large inputs**
   ```python
   def process_in_chunks(text, chunk_size=4000):
       chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
       results = []
       for chunk in chunks:
           result = client.chat.completions.create(
               model="solar-10.7b-chat",
               messages=[{"role": "user", "content": chunk}]
           )
           results.append(result.choices[0].message.content)
       return " ".join(results)
   ```

3. **Use streaming for long responses**
   ```python
   streaming_response = client.chat.completions.create(
       model="solar-10.7b-chat",
       messages=messages,
       stream=True
   )
   for chunk in streaming_response:
       print(chunk.choices[0].delta.content, end="")
   ```

## Claude Code Issues

### Command Not Found

**Symptoms:**
```
zsh: command not found: claude
```

**Solutions:**

1. **Install Claude Code**
   ```bash
   npm install -g @anthropic-ai/claude-code
   # Or
   pip install claude-code
   ```

2. **Check PATH**
   ```bash
   # Verify installation path is in PATH
   which claude
   echo $PATH
   
   # Add to PATH if needed
   export PATH="$HOME/.local/bin:$PATH"  # Add to ~/.bashrc
   ```

3. **Verify installation**
   ```bash
   claude --version
   ```

### Configuration Not Loading

**Symptoms:**
- Custom settings not applied
- Default model used instead of Solar Open2

**Solutions:**

1. **Check config file location**
   ```bash
   # Default locations
   ~/.claude/settings.json
   ~/.claude/settings.local.json
   .claude/settings.json  # Project-level
   ```

2. **Verify config syntax**
   ```bash
   # Check JSON validity
   python -m json.tool ~/.claude/settings.json
   ```

3. **Check file permissions**
   ```bash
   chmod 644 ~/.claude/settings.json
   ```

### Plugin/Extension Issues

**Symptoms:**
- Plugins not loading
- Custom commands not working

**Solutions:**

1. **Check plugin directory**
   ```bash
   ls -la ~/.claude/plugins/
   ```

2. **Verify plugin syntax**
   - Check plugin files for syntax errors
   - Ensure proper export statements

3. **Clear plugin cache**
   ```bash
   rm -rf ~/.claude/cache/
   ```

## Hermes Agent Issues

### Agent Not Responding

**Symptoms:**
- No response after query
- Hangs indefinitely

**Solutions:**

1. **Check Hermes status**
   ```bash
   hermes status
   ```

2. **Restart Hermes**
   ```bash
   hermes stop
   hermes start
   ```

3. **Check logs**
   ```bash
   hermes logs --tail 50
   ```

### Tool Execution Failures

**Symptoms:**
```
Error: Tool execution failed
```

**Solutions:**

1. **Verify tool configuration**
   - Check tool definitions in config
   - Ensure command paths are correct

2. **Test tools manually**
   ```bash
   # Test the command directly
   python -c "print('test')"
   ```

3. **Check permissions**
   ```bash
   chmod +x ~/.hermes/tools/*
   ```

## OKF Format Issues

### YAML Frontmatter Parse Error

**Symptoms:**
```
Error: Invalid YAML in frontmatter
```

**Solutions:**

1. **Check YAML syntax**
   ```bash
   # Validate YAML
   python -c "import yaml; yaml.safe_load(open('docs/reference/solar-open2.md'))"
   ```

2. **Common YAML errors:**
   - Missing closing `---`
   - Incorrect indentation
   - Unquoted special characters
   - Trailing spaces after `---`

3. **Use this template:**
   ```yaml
   ---
   type: Model
   title: Example
   description: A description
   tags: [tag1, tag2]
   timestamp: 2026-07-17T00:00:00Z
   ---
   ```

### Link Not Found

**Symptoms:**
- Broken cross-references
- 404 errors in documentation

**Solutions:**

1. **Verify link paths**
   ```bash
   # Check if file exists
   ls docs/reference/solar-open2.md
   
   # Test relative path
   cd docs/notes/models/
   ls ../reference/solar-open2.md
   ```

2. **Use correct relative paths**
   ```markdown
   <!-- From docs/notes/models/ to docs/reference/ -->
   [Solar Open2](../reference/solar-open2.md)
   
   <!-- From docs/notes/models/ to same directory -->
   [Related Model](./other-model.md)
   ```

3. **Run link checker**
   ```bash
   # Find and check all links
   grep -roh '\[.*\](.*\.md)' docs/ | sort -u
   ```

### Missing Required Fields

**Symptoms:**
```
Error: Missing required 'type' field
```

**Solutions:**

1. **Add required fields**
   ```yaml
   ---
   type: Model  # Required
   title: Solar Open2
   description: Description here
   ---
   ```

2. **Use templates**
   ```bash
   cp docs/templates/template-model.md docs/reference/new-model.md
   ```

## Git and Version Control Issues

### _private Files Accidentally Committed

**Symptoms:**
```
Error: Sensitive files in commit
```

**Solutions:**

1. **Remove from git history**
   ```bash
   # Remove from tracking (keeps local file)
   git rm --cached _private/*
   
   # Or remove completely
   git rm -r _private/
   ```

2. **Add to gitignore**
   ```bash
   echo "_private/" >> .gitignore
   git add .gitignore
   ```

3. **Verify gitignore**
   ```bash
   git check-ignore -v _private/credentials/api-key.txt
   ```

### Merge Conflicts in OKF Files

**Symptoms:**
```
CONFLICT (content): Merge conflict in docs/reference/solar-open2.md
```

**Solutions:**

1. **Resolve YAML frontmatter conflict**
   ```markdown
   <<<<<<< HEAD
   ---
   type: Model
   timestamp: 2026-07-17T10:00:00Z
   =======
   ---
   type: Model
   timestamp: 2026-07-17T11:00:00Z
   >>>>>>> branch
   ```
   
   Keep the most recent timestamp.

2. **Resolve body content conflict**
   - Manually merge content sections
   - Preserve both contributions where applicable

3. **Use merge tools**
   ```bash
   git mergetool
   ```

### Large File Warnings

**Symptoms:**
```
Warning: File too large for git
```

**Solutions:**

1. **Use Git LFS for large files**
   ```bash
   git lfs install
   git lfs track "*.bin"
   git lfs track "*.pdf"
   ```

2. **Store large files externally**
   - Use cloud storage for datasets
   - Reference files with URLs in OKF documents

## Getting Help

### Community Resources

- **Upstage Documentation**: https://docs.upstage.ai/
- **Claude Code Community**: Check official Anthropic channels
- **Hermes Agent**: Check Hermes documentation

### Reporting Issues

When reporting issues, include:

1. **Environment information**
   ```bash
   claude --version
   python --version
   uname -a
   ```

2. **Configuration files**
   - Anonymized settings.json
   - Reproducible config

3. **Error messages**
   - Full error output
   - Stack traces
   - Timestamps

4. **Steps to reproduce**
   - Detailed reproduction steps
   - Expected vs actual behavior

## Quick Reference

### Diagnostic Commands

```bash
# Check environment
echo $SOLAR_API_KEY | head -c 10
claude --version
python --version

# Test API connectivity
curl -H "Authorization: Bearer $SOLAR_API_KEY" \
     https://api.upstage.ai/v1/models

# Validate YAML
python -c "import yaml; yaml.safe_load(open('path/to/file.md'))"

# Check git status
git status
git diff
git log --oneline -10
```

### Reset Procedures

```bash
# Reset Claude Code config
rm ~/.claude/settings.local.json

# Reset Hermes
hermes reset

# Clear all caches
rm -rf ~/.claude/cache/
rm -rf ~/.hermes/cache/

# Fresh start (backup first!)
cp -r .claude .claude.backup
```

---

## Related Resources

- [Getting Started Guide](getting-started.md) - Initial setup
- [Claude Code Integration](claude-code-open2.md) - Claude Code setup
- [Hermes Agent Integration](hermes-agent.md) - Hermes Agent setup
- [OKF Document Authoring](okf-authoring.md) - Document formatting
