---
type: Reference
title: Models Index
description: Index of documented model profiles and specifications
tags: [reference, models, index]
timestamp: 2026-07-17T00:00:00Z
---

# Models Index

This index lists all documented model profiles in this knowledge base.

## Documented Models

* [Solar Open2](solar-open2.md) - Upstage's open-weight LLM (32K context, Korean-optimized)

## Model Categories

- Open-Weight Models
- Proprietary API Models
- Specialized Models (Code, Vision, etc.)
- Korean-Language Models
- Efficient/Edge Models

## Upstage Solar Family

### Solar Open2
- **Developer**: Upstage
- **Parameters**: ~10.7B
- **Context**: 32K tokens
- **License**: Apache 2.0 (확인 필요)
- **Best For**: Korean language tasks, efficient inference

### Other Solar Models (to be documented)
- Solar Mini
- Solar Pro
- Solar Ultra

## Other Notable Models (for comparison)

### OpenAI
- GPT-4
- GPT-4 Turbo
- GPT-3.5 Turbo

### Anthropic
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

### Google
- Gemini Pro
- Gemini Ultra
- Gemma

### Meta
- Llama 2
- Llama 3
- Llama 3.1

###Mistral AI
- Mistral 7B
- Mixtral 8x7B
- Mistral Large

## Adding a Model

1. Create a new file: `docs/notes/models/<model-slug>.md`
2. Use the [Model Template](../templates/template-model.md)
3. Add an entry to this index
4. Update the parent index: `docs/notes/models/index.md`

## Model Comparison Template

When comparing models, include:

```markdown
# Comparison: Model A vs Model B

## Architecture
| Aspect | Model A | Model B |
|--------|---------|---------|
| Parameters | X B | Y B |
| Context | A tokens | B tokens |
| Architecture | Transformer | Transformer |

## Performance
| Benchmark | Model A | Model B |
|-----------|---------|---------|
| MMLU | X% | Y% |
| HumanEval | X% | Y% |

## Pricing
| Model | Input | Output |
|-------|-------|--------|
| Model A | $X/1M | $Y/1M |
| Model B | $X/1M | $Y/1M |

## Best Use Cases
- **Model A**: [Use case]
- **Model B**: [Use case]
```
