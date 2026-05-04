---
id: documentation-guide
type: template-guide
status: active
topics:
  - documentation-template
  - project-start
  - agent-readable-docs
  - project-continuity
summary: First-guide documentation policy for agent-readable projects with continuity, retrieval, and recovery practices.
last_updated: 2026-05-05
---

# Documentation Guide

Use this guide once at the beginning of a new project.

This document is a first-guide for a new project workspace. Treat it like the onboarding document a new team member reads before starting work.

The goal is not to minimize the number of documents. The goal is to keep project knowledge searchable, durable, recoverable, and easy for future agent sessions to continue without reading every historical discussion.

This guide defines project documentation, retrieval, history, task tracking, and recovery practices. It does not define command execution policy. If the project uses `AGENTS.md` or an equivalent agent execution policy, keep execution rules there and do not duplicate them here.

Use the files under `templates/` when creating actual project documents.

## Documentation Goals

Project documentation must support:

- consistent work across agent sessions
- fast retrieval of the right project context
- no silent loss of decisions, meeting context, or implementation history
- task continuity after interruptions
- recovery of project direction and implementation intent even if source files are lost
- clear separation between current state, historical context, decisions, specs, tasks, and archives

## Core Principle

Let the document set grow as the project grows, but keep each document discoverable and purposeful.

Do not avoid documents just to reduce file count. Large documents are expensive to read and risky to edit. Prefer well-named, well-indexed documents with metadata over one overloaded document.

Do not create empty structure that will not be maintained. Create a document when it preserves important context, supports recovery, or reduces future ambiguity.

## Recommended Directory Structure

Start small, then expand as real content appears.

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
    ADR-0001_short-decision-title.md

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

## Required First Document

Create `docs/PROJECT-CONTEXT.md` first.

This file is the durable project entrypoint and document router. A future agent session should be able to read this file and know:

- what the project is
- what phase it is in
- what is active now
- which documents should be read next
- which documents are current, archived, or superseded
- which tasks or modules are active

`PROJECT-CONTEXT.md` should not duplicate every detail. It should point to the correct document.

Use `templates/PROJECT-CONTEXT.template.md`.

## Document Retrieval Method

Use document metadata and routing before reading full documents.

Recommended retrieval flow:

```text
1. Read `docs/PROJECT-CONTEXT.md`.
2. Check `Document Routing` and `Task To Docs Map`.
3. Search frontmatter metadata by `type`, `topics`, `summary`, and `status`.
4. Select the top relevant document candidates.
5. Read only the selected documents or sections required for the task.
6. Follow `related`, `supersedes`, or `superseded_by` links only when needed.
```

Avoid reading every meeting log or every spec before starting work.

## Document Metadata

Every durable Markdown document should include YAML frontmatter.

Required fields:

```text
id
type
status
topics
summary
last_updated
```

Optional fields:

```text
related
supersedes
superseded_by
source_meeting
owner
```

Recommended `type` values:

```text
context
meeting
product
architecture
spec
decision
task
scenario
module-task
reference
archive
template
```

Recommended `status` values:

```text
draft
active
stable
completed
superseded
archived
```

Topic policy:

```text
- use lowercase kebab-case
- keep topic count small
- use stable concept names
- add topics only when they improve document discovery
```

## Document Naming Policy

Use predictable names so agents can identify document purpose before opening the file.

General rules:

- Use English kebab-case for file and directory names.
- Use `YYYY-MM-DD` for date-sensitive documents.
- Use `NNN` for ordered logs, scenarios, or repeated records.
- Do not encode volatile status in filenames. Put status in frontmatter.
- Keep filenames short but specific.
- If a file is renamed, update references or leave a pointer note.

Recommended patterns:

| Document type | Pattern |
| --- | --- |
| Project context | `docs/PROJECT-CONTEXT.md` |
| Meeting log | `docs/meetings/<year>/YYYY-MM-DD_NNN_short-topic.md` |
| Decision | `docs/decisions/ADR-NNNN_short-decision-title.md` |
| Product doc | `docs/product/<topic>.md` |
| Architecture doc | `docs/architecture/<topic>.md` |
| Module spec | `docs/specs/<module-name>.md` |
| Capability spec | `docs/specs/<module-name>/<specific-capability>.md` |
| Backlog | `docs/tasks/backlog.md` |
| Active tasks | `docs/tasks/active.md` |
| Completed tasks | `docs/tasks/completed.md` |
| Scenario task | `docs/tasks/scenarios/scenario-NNN_short-topic.md` |
| Module task | `docs/tasks/modules/<module-name>-<work-topic>.md` |
| Archive | `docs/archive/<year>/YYYY-MM_short-topic.md` |

Examples:

```text
docs/meetings/2026/2026-05-05_001_project-start.md
docs/decisions/ADR-0001_use-agent-execution-policy.md
docs/specs/agent-runtime/tool-execution-policy.md
docs/tasks/scenarios/scenario-001_initial-project-setup.md
docs/tasks/modules/agent-runtime-context-recovery.md
docs/archive/2026/2026-05_completed-planning-history.md
```

## Meeting Logs

Meeting logs are created after a user discussion or project meeting.

Do not create meeting logs by guessing that one might be useful. Create one only after an actual discussion needs to be preserved.

Meeting logs are historical records. Do not silently delete old discussion content after it becomes resolved. Move or summarize it only with a change history entry.

Use `templates/meeting-log.template.md`.

## Task Management Policy

Use task documents when implementation work begins or when discussion creates actionable work.

Tasks should be small enough that a future session can continue them without re-reading all project history.

Recommended task files:

```text
docs/tasks/backlog.md
docs/tasks/active.md
docs/tasks/completed.md
docs/tasks/scenarios/scenario-NNN_short-topic.md
docs/tasks/modules/<module-name>-<work-topic>.md
```

Task records should include:

```text
id
status
goal
scope
related documents
related files
acceptance criteria
implementation notes
verification plan
verification result
open risks
handoff notes
change history
```

Use `backlog.md` for unstarted work, `active.md` for current work, and `completed.md` for completed work summaries. Use scenario or module task files when a task needs enough detail to preserve continuity.

Use `templates/task.template.md`, `templates/scenario.template.md`, or `templates/module-work.template.md`.

## Scenario And Module Work Notes

Use scenario work notes for user-visible workflows or end-to-end behavior.

Use module work notes for isolated implementation areas, such as parser, runtime, storage, UI, security, or integration modules.

Scenario/module notes should preserve:

- why the work exists
- expected behavior
- affected modules/files
- step-by-step plan
- implementation decisions
- verification scenarios
- known limitations
- recovery notes

These notes are especially useful when work spans multiple sessions.

## Recovery-Grade Documentation Policy

Project documentation should be strong enough to recover project intent and critical implementation direction even if source files are lost.

For important features, modules, or decisions, preserve:

- goal and user-facing behavior
- module boundaries
- key interfaces
- data structures
- runtime flow
- important algorithms or rules
- configuration and environment assumptions
- verification commands and expected results
- known risks and limitations
- links to related decisions, specs, and task notes

Do not rely on source code alone to preserve project knowledge.

## Archival Policy

When a document becomes too long, move completed or stale sections into an archive/reference file.

Archive only content that is no longer needed for active work but should remain preserved.

After moving content, leave a pointer in the original document:

```text
Moved content: <short description>
Moved to: <archive path>
Moved on: YYYY-MM-DD
Reason: <why it was archived>
```

Do not archive active constraints, current decisions, or unresolved questions.

Use `templates/archive.template.md`.

## Change History Policy

Do not erase meaningful history when updating a current-state document.

When content is corrected, replaced, completed, moved, or superseded:

```text
- update the current section
- preserve the previous state in Change History, a meeting log, a decision record, or an archive
- explain why the change happened when it is not obvious
- leave a pointer when content moves to another document
```

This policy exists because agents may over-clean documents and remove useful context. Prefer a short historical note over silent deletion.

## Optional Documents

Create these when real content exists:

- `product/`: product intent, users, goals, non-goals, workflows.
- `architecture/`: system structure, module map, runtime boundaries, data flow.
- `specs/`: implementation details for one module or capability.
- `decisions/`: decisions that should remain understandable later.
- `tasks/`: actionable work tracking and session continuity.
- `archive/`: inactive but preserved historical content.

Use the corresponding file from `templates/`.

## Language Policy

Recommended default:

- Conversation: any language comfortable for the project owner.
- Durable technical documents: English.
- File and directory names: English kebab-case.
- Meeting logs: English preferred for consistency, but preserve important original wording when useful.

## Relationship To `AGENTS.md`

This guide does not define agent execution behavior.

Use `AGENTS.md` or an equivalent agent execution policy for:

- agent operating mode
- project discovery
- command discovery
- cost control
- change limits
- verification rules
- safety rules
- handoff format

Use this documentation guide for:

- project context
- document retrieval
- meeting records
- task continuity
- scenario/module progress records
- durable decisions
- document organization
- change history
- recovery-grade notes

Do not duplicate `AGENTS.md` rules here.

## First Setup Checklist

At project start:

1. Create `docs/PROJECT-CONTEXT.md` from `templates/PROJECT-CONTEXT.template.md`.
2. Create `docs/meetings/<year>/`.
3. Fill known fields in `PROJECT-CONTEXT.md`.
4. Leave unknown project details as `TBD`.
5. Create the first meeting log only after an actual user discussion.
6. Create task, spec, decision, architecture, or archive documents only when real content exists.
7. Keep `PROJECT-CONTEXT.md` updated as the routing document for future sessions.
