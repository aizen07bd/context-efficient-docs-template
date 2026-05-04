# Context-Efficient Project Documentation Template

An agent-readable documentation template set for reducing context waste, improving project continuity, and preserving enough written records to recover project intent across sessions.

This project is based on a simple premise:

> AI agents do not only need more documents. They need documents that are easy to locate, cheap to read, and strong enough to preserve project continuity.

## Abstract

Long-running AI-assisted projects often suffer from context drift, repeated document discovery, missing decisions, overwritten history, and high token consumption. This template set proposes a documentation structure that combines:

- a project context router
- metadata-based document discovery
- predictable file naming
- task and scenario continuity records
- decision and archive records
- recovery-grade implementation notes

We also ran a small deterministic benchmark comparing a structured document layout against a flat folder containing the same Markdown documents. In this experiment, the structured layout reached the same target documents and sections while using about **25% less estimated context tokens**.

## Purpose

This template set is intended for internal project documentation where AI coding agents are used across multiple sessions.

It is designed to help agents:

- find the right document faster
- avoid reading unrelated history
- preserve decisions and task state
- continue interrupted work
- avoid silent deletion of useful context
- recover project intent even if source files are lost

This template set focuses on documentation structure and record management, not command execution policy.

## Template Set

```text
DocsTempletv2/
  documentation-guide.md
  templates/
    PROJECT-CONTEXT.template.md
    meeting-log.template.md
    product.template.md
    architecture.template.md
    spec.template.md
    ADR.template.md
    task.template.md
    scenario.template.md
    module-work.template.md
    archive.template.md
```

## Recommended Project Layout

When applied to a project, the documentation structure is intended to look like this:

```text
docs/
  PROJECT-CONTEXT.md

  meetings/
    <year>/
      YYYY-MM-DD_NNN_short-topic.md

  product/
    overview.md
    goals-and-non-goals.md
    user-workflows.md

  architecture/
    overview.md
    module-map.md
    data-flow.md
    runtime-boundaries.md

  specs/
    <module-name>.md
    <module-name>/
      overview.md
      <specific-capability>.md

  decisions/
    ADR-NNNN_short-decision-title.md

  tasks/
    backlog.md
    active.md
    completed.md
    scenarios/
      scenario-NNN_short-topic.md
    modules/
      <module-name>-<work-topic>.md

  archive/
    <year>/
      YYYY-MM_short-topic.md
```

## Key Ideas

### 1. `PROJECT-CONTEXT.md` as a Router

`PROJECT-CONTEXT.md` is not meant to contain every detail. It acts as the durable entrypoint and routing document.

It should tell a future agent:

- what the project is
- what is active now
- which documents matter for the current task
- where active tasks and decisions live
- which documents are archived or superseded

### 2. Metadata-First Discovery

Each durable Markdown document uses YAML frontmatter:

```text
id
type
status
topics
summary
last_updated
```

Optional fields include:

```text
related
supersedes
superseded_by
source_meeting
owner
```

This lets an agent select candidate documents using compact metadata before loading full content.

### 3. Predictable Naming

File names use stable English kebab-case and predictable patterns.

Examples:

```text
meetings/2026/2026-05-05_001_project-start.md
decisions/ADR-0001_use-agent-execution-policy.md
specs/agent-runtime/tool-execution-policy.md
tasks/scenarios/scenario-001_initial-project-setup.md
tasks/modules/agent-runtime-context-recovery.md
archive/2026/2026-05_completed-planning-history.md
```

The goal is to make document purpose clear before opening the file.

### 4. Task Continuity

Task documents preserve:

- goal
- scope
- related documents
- related files
- acceptance criteria
- implementation notes
- verification plan and result
- open risks
- handoff notes
- change history

This allows a future agent session to continue work without replaying the entire conversation.

### 5. Recovery-Grade Notes

Important features, modules, and decisions should preserve enough information to recover the project direction even if source files are lost.

For important work, documents should record:

- goal and user-facing behavior
- module boundaries
- key interfaces
- data structures
- runtime flow
- important algorithms or rules
- configuration and environment assumptions
- verification commands and expected results
- known risks and limitations

### 6. No Silent History Loss

Agents may over-clean documents and accidentally remove useful context.

This template set requires:

- meaningful history to be preserved
- completed or stale content to be archived instead of deleted
- pointers to be left when content moves
- superseded documents to be marked instead of silently replaced

## Benchmark

We ran a deterministic document-retrieval benchmark to compare:

The tested variables are document structure, directory layout, YAML frontmatter, and document-routing metadata.

- `test/docs`: structured directories with YAML frontmatter
- `test2`: flat folder with all Markdown files in one directory and no frontmatter

Benchmark script:

[tools/doc_search_benchmark.py](/Users/kris/code/ai/proj/totalvulscaner/tools/doc_search_benchmark.py)

Detailed benchmark note:

[docs/document-retrieval-benchmark.md](/Users/kris/code/ai/proj/totalvulscaner/docs/document-retrieval-benchmark.md)

## Benchmark Setup

The benchmark generated comparable synthetic project documents for both layouts.

Configuration:

- generated documents: 66 per layout
- search scenarios: 18
- repeated runs: 1,800 per layout
- target: locate the correct file and section
- measured values:
  - access success
  - exact file hit
  - exact section hit
  - context characters consumed
  - estimated context tokens
  - elapsed time

## Benchmark Results

| Metric | Structured `test/docs` | Flat `test2` |
| --- | ---: | ---: |
| runs | 1800 | 1800 |
| access success | 100% | 100% |
| exact file hit | 100% | 100% |
| exact section hit | 100% | 100% |
| average context chars | 20,223 | 27,032.56 |
| estimated average tokens | 5,055.75 | 6,758.14 |
| average elapsed ms | 1.3950 | 1.0031 |

## Result Interpretation

Both layouts reached the correct target file and section in all benchmark scenarios.

The structured layout consumed less context:

```text
structured context chars: 20,223
flat context chars:       27,032.56
reduction:                about 25.2%
```

Estimated token usage showed the same reduction pattern.

The flat layout was slightly faster in local file IO time. However, for AI agent workflows, local file IO is usually less important than how much content must be loaded into model context.

In this benchmark, the structured layout did not improve accuracy because both layouts reached 100%. Its advantage was reaching the same result with less context.

Therefore, the observed reduction should be attributed to structured documentation and metadata-based retrieval.

## Limitations

This benchmark is not a full LLM-agent evaluation.

Limitations:

- deterministic search simulation
- synthetic documents
- controlled query scenarios
- no actual model reasoning variance
- no noisy real-world project history
- no human quality evaluation
- no multi-session drift measurement

The result should not be read as “structured documentation is always faster.”

The narrower conclusion is:

> In this controlled retrieval test, structured documentation with metadata and routing reached the same targets while using about 25% less estimated context.

## Suggested Use

Use this template set when a project needs:

- long-running AI-assisted development
- repeatable session handoff
- recoverable project history
- structured decision records
- task continuity across interruptions
- lower context consumption during document lookup

## Current Status

This is an experimental documentation template set with a small benchmark. It is not a general proof. The next useful step would be testing it with real projects and real AI agent sessions.
