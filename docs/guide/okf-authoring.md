---
type: Guide
title: OKF Document Authoring
description: Guide to creating OKF-format documents for the knowledge base
tags: [guide, okf, authoring, documentation]
timestamp: 2026-07-17T00:00:00Z
---

# OKF Document Authoring

This guide explains how to create and maintain documents in the Open Knowledge Format (OKF) for this knowledge base.

## What is OKF?

OKF (Open Knowledge Format) is a universal, vendor-neutral format for representing knowledge as plain markdown files with YAML frontmatter. It is designed to be:

- **Readable** by humans without tooling
- **Parseable** by AI agents without bespoke SDKs
- **Diffable** in version control
- **Portable** across tools and organizations

## OKF Document Structure

Every OKF document has two parts:

1. **YAML Frontmatter** - Metadata block at the top
2. **Markdown Body** - Free-form content

### Required Frontmatter Fields

```yaml
---
type: <Type name>              # REQUIRED - identifies the concept type
---
```

The `type` field is mandatory and identifies what kind of concept this document represents.

### Recommended Frontmatter Fields

```yaml
---
type: Model                    # REQUIRED
title: Solar Open2             # Human-readable display name
description: Upstage's open-weight LLM  # One-line summary
tags: [llm, ai, solar]         # Cross-cutting categorization
timestamp: 2026-07-17T00:00:00Z  # Last modification time
resource: https://docs.upstage.ai/  # Canonical URI
---
```

### Optional Frontmatter Fields

You can include any additional metadata fields:

```yaml
---
type: Paper
title: "Attention Is All You Need"
authors: ["Ashish Vaswani", "Noam Shazeer", "..."]
venue: "NeurIPS 2017"
year: 2017
arxiv_id: "1706.03762"
code_url: "https://github.com/tensorflow/tensor2tensor"
---
```

## Document Types Reference

| Type | Purpose | Example Use Case |
|------|---------|------------------|
| `Model` | AI/ML model documentation | Solar Open2 model card |
| `Paper` | Research paper summaries | Paper reviews and notes |
| `Experiment` | Experiment records | Model evaluation results |
| `Person` | Researcher profiles | Key contributor notes |
| `Project` | Project documentation | Experiment project tracking |
| `Guide` | How-to guides | Usage tutorials |
| `Reference` | Technical references | API documentation |
| `Dataset` | Dataset descriptions | Data catalog entries |
| `Benchmark` | Benchmark results | Model performance comparisons |
| `Playbook` | Step-by-step procedures | Operational runbooks |
| `LogEntry` | Log and notes | Chronological records |
| `Writing` | Written content | Essays, articles, blog posts |

## Body Structure Conventions

The body is standard markdown. Use these conventional headings when applicable:

### # Schema

For structured data descriptions:

```markdown
# Schema

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR | User's name |
```

### # Examples

For usage examples:

```markdown
# Examples

```python
from solar import Solar
model = Solar("solar-open2")
response = model.generate("Hello, world!")
```
```

### # Citations

For external sources:

```markdown
# Citations

[1] [Paper Title](https://arxiv.org/abs/1234.5678)
[2] [Documentation](https://docs.example.com)
```

## Cross-Linking

Link between documents using markdown links:

### Bundle-Relative Links (Recommended)

```markdown
See the [Solar Open2 model](../reference/solar-open2.md) for details.
```

### Same-Directory Links

```markdown
See [related-concept.md](./related-concept.md) for more information.
```

### External Links

```markdown
For more information, see [the official documentation](https://docs.upstage.ai/).
```

## Creating New Documents

### Step 1: Choose the Right Type

Select the appropriate `type` based on what the document represents:

- Is it a model? → `Model`
- Is it a paper summary? → `Paper`
- Is it an experiment? → `Experiment`
- Is it a guide? → `Guide`

### Step 2: Create from Template

Copy the appropriate template:

```bash
# Model
cp docs/templates/template-model.md docs/reference/my-model.md

# Paper
cp docs/templates/template-paper.md docs/notes/papers/my-paper.md

# Experiment
cp docs/templates/template-experiment.md docs/experiments/my-experiment.md
```

### Step 3: Fill in Frontmatter

Edit the YAML frontmatter:

```yaml
---
type: Model
title: My Custom Model
description: A description of what this model does
tags: [custom, experimental]
timestamp: 2026-07-17T00:00:00Z
---
```

### Step 4: Write the Body

Use markdown to structure your content:

```markdown
# Overview

Introduction to the model/concept.

# Architecture

Technical details about the architecture.

# Usage

How to use this model/concept.

# Examples

```python
# Code examples
```

# Limitations

Known limitations and constraints.

# References

[1] Citation 1
[2] Citation 2
```

## Best Practices

### 1. Be Consistent

- Use the same type names across similar documents
- Follow the folder structure conventions
- Use consistent timestamp formats (ISO 8601)

### 2. Write Clear Descriptions

- Keep descriptions concise (1-2 sentences)
- Make them informative for search and preview
- Avoid vague or generic descriptions

### 3. Use Tags Wisely

- Tags should be lowercase
- Use tags for cross-cutting categories
- Don't over-tag (3-5 tags is usually enough)

### 4. Maintain Links

- Verify links work before committing
- Use relative links for internal references
- Update links when moving documents

### 5. Keep Timestamps Updated

- Update timestamp when making significant changes
- Use ISO 8601 format: `2026-07-17T10:30:00Z`

## Document Lifecycle

### 1. Draft

- Create new document from template
- Fill in basic frontmatter
- Write initial content

### 2. Review

- Check for completeness
- Verify links and references
- Ensure OKF compliance

### 3. Publish

- Add to git
- Update index files if needed
- Notify relevant stakeholders

### 4. Maintain

- Update as information changes
- Fix broken links
- Add new references

## Validation

Before committing, verify your document:

```bash
# Check frontmatter syntax
python -c "import yaml; yaml.safe_load(open('docs/reference/my-model.md'))"

# Check markdown links
grep -o '\[.*\](.*)' docs/reference/my-model.md

# Check required fields
grep -E '^type:' docs/reference/my-model.md
```

## Examples

### Complete Model Document

```markdown
---
type: Model
title: Solar Open2
description: Upstage's 10.7B parameter open-weight language model
tags: [llm, ai, solar, open2, korean]
timestamp: 2026-07-17T00:00:00Z
resource: https://docs.upstage.ai/
---

# Overview

Solar Open2 is a decoder-only language model developed by Upstage, a Korean AI startup. It is available as an open-weight model for research and commercial use.

# Architecture

Solar Open2 uses a transformer-based architecture with:

- 10.7 billion parameters
- 32K context window
- Grouped Query Attention (GQA)
- Rotary Position Embeddings (RoPE)

# Training

The model was trained on a diverse corpus of:

- High-quality web text
- Code repositories
- Multilingual content (emphasis on Korean)
- Technical documentation

# Capabilities

- **Text Generation**: Fluent text generation across domains
- **Code Understanding**: Strong code comprehension
- **Multilingual**: Excellent Korean and English support
- **Instruction Following**: Good adherence to prompts
- **Reasoning**: Enhanced logical reasoning

# Usage Example

```python
import upstage

client = upstage.Client(api_key="your-api-key")
response = client.chat.completions.create(
    model="solar-10.7b-chat",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

# Performance

| Benchmark | Score | Notes |
|-----------|-------|-------|
| MMLU | TBD | 5-shot evaluation |
| HumanEval | TBD | Pass@1 metric |
| HellaSwag | TBD | 10-shot evaluation |

# Limitations

- Knowledge cutoff: 2024
- May produce hallucinations on niche topics
- Limited fine-tuning documentation available

# References

[1] [Upstage Solar Documentation](https://docs.upstage.ai/)
[2] [Solar Model Card](https://huggingface.co/upstage/solar-10.7b)
[3] [Upstage GitHub](https://github.com/UpstageAI)
```

## Related Resources

- [OKF Specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
- [Getting Started Guide](getting-started.md)
- [Template Files](../templates/)
- [Index Files](../index.md)
