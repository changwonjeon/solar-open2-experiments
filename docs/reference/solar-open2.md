---
type: Model
title: Solar Open2
description: Upstage Solar Open2 model specifications and capabilities
tags: [model, ai, llm, solar, open2]
timestamp: 2026-07-17T00:00:00Z
resource: https://docs.upstage.ai/
---

# Solar Open2

Solar Open2 is Upstage's open-weight large language model designed for efficient inference and strong performance across a wide range of tasks.

## Overview

Solar (Specialized Large Language Model) is developed by Upstage, a Korean AI startup. Open2 refers to the open-weight version of the model.

## Model Specifications

| Property | Value |
|----------|-------|
| Developer | Upstage |
| Model Type | Decoder-only LLM |
| Context Length | 32K tokens |
| Parameters | <to be filled> |
| License | <to be confirmed> |
| Training Data | <to be confirmed> |

## Capabilities

- **Text Generation**: High-quality text generation across various domains
- **Code Understanding**: Strong code comprehension and generation
- **Multilingual**: Support for multiple languages including Korean
- **Instruction Following**: Good adherence to instructions and prompts
- **Reasoning**: Enhanced reasoning capabilities

## API Usage

```python
from upstage import Solar

# Initialize the model
model = Solar(model_name="solar-open2")

# Generate text
response = model.generate(
    prompt="Write a short story about AI",
    max_tokens=500
)
print(response)
```

## Integration with Claude Code

Solar Open2 can be configured as a custom model in Claude Code:

1. Set up the model endpoint
2. Configure Claude Code settings
3. Test the integration

## Integration with Hermes Agent

Hermes Agent supports Solar Open2 as a backend model:

1. Install Hermes Agent
2. Configure model provider settings
3. Select Solar Open2 as the model

## Performance Benchmarks

| Benchmark | Score | Notes |
|-----------|-------|-------|
| MMLU | <to be filled> | 5-shot |
| HumanEval | <to be filled> | Pass@1 |
| HellaSwag | <to be filled> | 10-shot |

## Known Limitations

- <Limitations to be documented>

## Updates Log

- 2026-07-17: Initial documentation created

## References

[1] Upstage Official Documentation - https://docs.upstage.ai/
[2] Solar Model Card - <link>
[3] GitHub Repository - <link>
