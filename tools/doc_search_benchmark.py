#!/usr/bin/env python3
"""
Benchmark structured vs flat documentation retrieval.

This script generates comparable synthetic project documents under:
- test/docs: structured directories with YAML frontmatter
- test2: flat Markdown files without YAML frontmatter

Then it runs a deterministic retrieval simulation and reports:
- average search time
- average context characters/tokens consumed
- access success
- exact target file/section hit rate
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import statistics
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED_ROOT = ROOT / "test" / "docs"
FLAT_ROOT = ROOT / "test2"
GENERATED_MARKER = "<!-- generated-benchmark-doc -->"


@dataclass(frozen=True)
class DocSpec:
    rel_path: str
    doc_type: str
    status: str
    topics: tuple[str, ...]
    summary: str
    title: str
    sections: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Scenario:
    name: str
    query: str
    target_rel_path: str
    target_section: str


def slug(path: str) -> str:
    return (
        path.replace("/", "__")
        .replace(".md", "")
        .replace("_", "-")
        .lower()
    )


def frontmatter(doc: DocSpec) -> str:
    topics = "\n".join(f"  - {topic}" for topic in doc.topics)
    return f"""---
id: {slug(doc.rel_path)}
type: {doc.doc_type}
status: {doc.status}
topics:
{topics}
summary: {doc.summary}
last_updated: 2026-05-05
---

"""


def body(doc: DocSpec) -> str:
    parts = [GENERATED_MARKER, "", f"# {doc.title}", ""]
    for heading, content in doc.sections:
        parts.extend([f"## {heading}", "", content.strip(), ""])
    return "\n".join(parts)


def flat_name(doc: DocSpec) -> str:
    return doc.rel_path.replace("/", "__")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


DOCS: tuple[DocSpec, ...] = (
    DocSpec(
        "product/agentic-security-overview.md",
        "product",
        "active",
        ("product", "agentic-security", "workflow"),
        "Product intent and workflows for agentic security analysis.",
        "Product: Agentic Security Overview",
        (
            ("Purpose", "Define a security assistant that finds evidence-backed vulnerability candidates."),
            ("Target Users", "Security engineers, independent researchers, and developers reviewing security-sensitive code."),
            ("User Workflows", "Start from a repository, select a module, generate hypotheses, inspect evidence, and produce a review note."),
            ("Non-Goals", "Do not run destructive exploits or production-impacting scans."),
            ("Recovery Notes", "The product can be rebuilt from workflow, evidence, and module boundary documents."),
        ),
    ),
    DocSpec(
        "product/natural-language-compiler.md",
        "product",
        "draft",
        ("product", "natural-language-compiler", "compiler"),
        "Product context for natural-language-to-software artifact generation.",
        "Product: Natural Language Compiler",
        (
            ("Purpose", "Turn long natural-language intent into buildable software artifacts through an agentic compile loop."),
            ("User Workflows", "User writes a prose requirement, agent clarifies gaps, generates code, runs build, repairs failures."),
            ("Constraints", "Do not treat natural language as deterministic source without validation."),
            ("Open Questions", "How much internal feedback can run before asking the user for clarification."),
        ),
    ),
    DocSpec(
        "architecture/document-routing.md",
        "architecture",
        "active",
        ("architecture", "document-routing", "retrieval"),
        "Architecture for metadata-first document routing.",
        "Architecture: Document Routing",
        (
            ("System Overview", "PROJECT-CONTEXT acts as the router and frontmatter acts as a compact discovery layer."),
            ("Module Map", "Router, manifest reader, topic matcher, related-link follower, archive pointer resolver."),
            ("Runtime Boundaries", "Document routing does not define agent execution policy; AGENTS.md does."),
            ("Data Flow", "Context request -> PROJECT-CONTEXT -> metadata scan -> candidate docs -> selected sections."),
            ("Verification And Expected Results", "A retrieval scenario should reach the target file without scanning every document."),
        ),
    ),
    DocSpec(
        "architecture/cost-aware-agent-runtime.md",
        "architecture",
        "stable",
        ("architecture", "agent-runtime", "cost-control"),
        "Architecture for cost-aware agent execution and command selection.",
        "Architecture: Cost-Aware Agent Runtime",
        (
            ("System Overview", "Agent execution is separated from documentation routing and uses verified project facts."),
            ("Runtime Boundaries", "The runtime controls commands, approvals, verification scope, and safety boundaries."),
            ("Cost Control", "Prefer targeted reads, verified commands, cheap-first checks, and no repeated full-suite tests."),
            ("Security And Safety", "Dangerous commands, remote scripts, credential changes, and production-impacting actions require approval."),
        ),
    ),
    DocSpec(
        "architecture/recovery-model.md",
        "architecture",
        "active",
        ("architecture", "recovery", "continuity"),
        "Recovery model for rebuilding project intent from documents.",
        "Architecture: Recovery Model",
        (
            ("System Overview", "Documents preserve intent, boundaries, interfaces, decisions, task state, and verification records."),
            ("Recovery Flow", "PROJECT-CONTEXT -> active tasks -> specs -> ADRs -> change history -> archives."),
            ("Recovery Requirements", "Important modules must record interfaces, data structures, runtime flow, and expected verification results."),
            ("Known Risks", "If source code is the only record of design, source loss makes project recovery unreliable."),
        ),
    ),
    DocSpec(
        "specs/agent-runtime/tool-execution-policy.md",
        "spec",
        "active",
        ("spec", "agent-runtime", "tool-execution", "safety"),
        "Specification for scoped and auditable tool execution.",
        "Spec: Tool Execution Policy",
        (
            ("Purpose", "Define how an agent requests tool execution without receiving unrestricted system authority."),
            ("Interfaces", "ActionRequest, ScopeCheck, RiskScore, ApprovalGate, ExecutionResult."),
            ("Runtime Flow", "Agent proposes action -> policy checks scope/risk -> executor runs allowed action -> result is logged."),
            ("Security And Safety Notes", "Destructive, production-impacting, network-heavy, or credential-changing actions require user approval."),
            ("Verification", "Commands: targeted policy tests. Expected results: blocked risky actions and allowed read-only actions."),
            ("Recovery Notes", "Recreate this module from interface names, risk policy, approval rules, and execution result schema."),
        ),
    ),
    DocSpec(
        "specs/documentation/frontmatter-metadata.md",
        "spec",
        "stable",
        ("spec", "documentation", "frontmatter", "metadata"),
        "Specification for document metadata used by retrieval tools.",
        "Spec: Frontmatter Metadata",
        (
            ("Purpose", "Provide compact document discovery without loading full Markdown content."),
            ("Data Structures", "Required fields: id, type, status, topics, summary, last_updated."),
            ("Important Algorithms Or Rules", "Use stable lowercase kebab-case topics and avoid noisy topic inflation."),
            ("Verification", "Commands: metadata parser test. Expected results: all durable docs expose required fields."),
        ),
    ),
    DocSpec(
        "specs/documentation/archive-policy.md",
        "spec",
        "active",
        ("spec", "documentation", "archive", "history"),
        "Specification for moving stale content into archives without losing context.",
        "Spec: Archive Policy",
        (
            ("Purpose", "Move completed or stale content out of active documents while preserving retrievable history."),
            ("Runtime Flow", "Select stale content -> create archive -> leave pointer in source -> update change history."),
            ("Important Algorithms Or Rules", "Do not archive active constraints, current decisions, or unresolved questions."),
            ("Recovery Notes", "Archive pointers must include moved content, target path, date, and reason."),
        ),
    ),
    DocSpec(
        "specs/security/idor-analysis.md",
        "spec",
        "draft",
        ("spec", "security", "idor", "web-api"),
        "Specification for IDOR and authorization-bypass analysis.",
        "Spec: IDOR Analysis",
        (
            ("Purpose", "Compare two authorized test accounts and detect unauthorized cross-resource access."),
            ("Interfaces", "AccountA, AccountB, ResourceId, RequestTemplate, ResponseDiff, FindingCandidate."),
            ("Runtime Flow", "Discover resource pattern -> build paired requests -> compare authorization behavior -> record evidence."),
            ("Security And Safety Notes", "Use only test accounts and avoid destructive write actions."),
        ),
    ),
    DocSpec(
        "specs/low-level/arm64-boundary-analysis.md",
        "spec",
        "draft",
        ("spec", "low-level", "arm64", "reverse-engineering"),
        "Specification for ARM64 privilege-boundary analysis notes.",
        "Spec: ARM64 Boundary Analysis",
        (
            ("Purpose", "Identify candidate privilege boundaries in ARM64 binaries and firmware-adjacent code."),
            ("Data Structures", "FunctionSummary, CallEdge, BoundaryCandidate, InputSource, VerificationHint."),
            ("Runtime Flow", "Disassemble -> summarize functions -> identify boundary calls -> trace input flow -> record hypotheses."),
            ("Known Risks And Limitations", "Binary analysis may miss indirect calls and stripped symbols."),
        ),
    ),
    DocSpec(
        "decisions/ADR-0001_use-cost-aware-agents-md.md",
        "decision",
        "stable",
        ("decision", "agents-md", "cost-control"),
        "Decision to use Cost-Aware AGENTS.md for agent execution rules.",
        "ADR-0001: Use Cost-Aware AGENTS.md",
        (
            ("Context", "Agent sessions can waste tokens and repeat discovery without stable project rules."),
            ("Decision", "Use Cost-Aware AGENTS.md as the prescriptive execution policy."),
            ("Alternatives Considered", "Use generic AGENTS.md, tool-specific files only, or no shared agent policy."),
            ("Consequences", "Agents must discover project commands, classify verification cost, and preserve user changes."),
        ),
    ),
    DocSpec(
        "decisions/ADR-0002_split-templates-from-guide.md",
        "decision",
        "active",
        ("decision", "documentation", "templates"),
        "Decision to separate guide policy from reusable Markdown templates.",
        "ADR-0002: Split Templates From Guide",
        (
            ("Context", "A single guide containing all templates becomes too long and expensive to read."),
            ("Decision", "Keep policies in documentation-guide.md and put reusable forms under templates/."),
            ("Consequences", "Agents can read the guide once and open only the relevant template when creating a document."),
        ),
    ),
    DocSpec(
        "tasks/active.md",
        "task",
        "active",
        ("task", "active", "documentation"),
        "Active task list for documentation-template validation.",
        "Active Tasks",
        (
            ("Goal", "Validate structured vs flat documentation retrieval and refine the template set."),
            ("Current State", "Structured docs exist under test/docs and flat docs exist under test2."),
            ("Next Step", "Run retrieval benchmark and compare context cost, speed, and hit rate."),
            ("Verification Plan", "Use deterministic scenarios targeting known files and sections."),
        ),
    ),
    DocSpec(
        "tasks/backlog.md",
        "task",
        "active",
        ("task", "backlog", "documentation"),
        "Backlog of future documentation-template improvements.",
        "Backlog",
        (
            ("Goal", "Track unstarted documentation improvements."),
            ("Implementation Notes", "Candidate work includes template field refinement, archive examples, and document retrieval scoring."),
            ("Open Risks", "Too much process may increase onboarding friction."),
        ),
    ),
    DocSpec(
        "tasks/scenarios/scenario-001_initial-project-setup.md",
        "scenario",
        "completed",
        ("scenario", "project-start", "setup"),
        "Scenario for initial documentation setup.",
        "Scenario 001: Initial Project Setup",
        (
            ("Goal", "Create PROJECT-CONTEXT and recommended docs directories from the template set."),
            ("Expected Behavior", "A new agent can read PROJECT-CONTEXT and find the active work area."),
            ("Verification Scenarios", "Locate project goal, active constraints, document routing, and task map."),
            ("Recovery Notes", "If files are lost, recreate the initial docs structure from the guide and templates."),
        ),
    ),
    DocSpec(
        "tasks/modules/document-router-retrieval.md",
        "module-task",
        "active",
        ("module-work", "document-router", "retrieval"),
        "Module work note for document router retrieval validation.",
        "Module Work: Document Router Retrieval",
        (
            ("Module", "document-router"),
            ("Goal", "Measure whether metadata and directory structure reduce context consumption."),
            ("Key Interfaces", "Scenario, SearchResult, CandidateDoc, ContextCounter."),
            ("Runtime Flow", "Query -> candidate selection -> section match -> metric output."),
            ("Verification", "Commands: benchmark script. Expected results: structured docs use less context than flat docs."),
        ),
    ),
    DocSpec(
        "meetings/2026/2026-05-05_001_document-template-review.md",
        "meeting",
        "active",
        ("meeting", "documentation-template", "review"),
        "Discussion about documentation-template gaps and recovery requirements.",
        "2026-05-05 Meeting 001: Document Template Review",
        (
            ("Purpose", "Review missing policies in the documentation template set."),
            ("Discussion", "The documentation system must preserve continuity, task state, decisions, and recovery-grade implementation intent."),
            ("Decisions", "Use separate template files, preserve v2 guide policies, and avoid compressing away core intent."),
            ("Open Questions", "How much benchmark data is enough to validate structured retrieval."),
        ),
    ),
    DocSpec(
        "archive/2026/2026-05_completed-planning-history.md",
        "archive",
        "archived",
        ("archive", "planning-history", "documentation"),
        "Archived completed planning discussion for documentation template design.",
        "Archive: 2026-05 Completed Planning History",
        (
            ("Archived Content", "Completed discussion about AGENTS.md cost control and documentation-template structure."),
            ("Source Location", "Moved from long-running project discussion notes."),
            ("Reason For Archive", "The active guide should stay focused while preserving historical reasoning."),
            ("Archive Restrictions", "Active constraints, current decisions, and unresolved questions were not archived."),
        ),
    ),
)


def extra_docs() -> tuple[DocSpec, ...]:
    modules = (
        "auth-session",
        "billing-ledger",
        "cloud-inventory",
        "forensic-timeline",
        "binary-analysis",
        "report-generator",
        "workspace-state",
        "model-router",
    )
    docs: list[DocSpec] = []
    for idx, module in enumerate(modules, start=1):
        docs.extend(
            [
                DocSpec(
                    f"product/{module}-workflow.md",
                    "product",
                    "draft",
                    ("product", module, "workflow"),
                    f"Workflow notes for {module}.",
                    f"Product: {module} Workflow",
                    (
                        ("Purpose", f"Describe the product workflow around {module}."),
                        ("User Workflows", f"Users inspect {module}, review findings, and update task records."),
                        ("Constraints", "Keep completed context linked instead of deleted."),
                    ),
                ),
                DocSpec(
                    f"architecture/{module}-overview.md",
                    "architecture",
                    "draft",
                    ("architecture", module, "overview"),
                    f"Architecture overview for {module}.",
                    f"Architecture: {module} Overview",
                    (
                        ("System Overview", f"{module} is isolated behind a clear module boundary."),
                        ("Module Map", f"{module} owns its internal state and exposes a narrow interface."),
                        ("Runtime Boundaries", "Execution policy stays in AGENTS.md and is not duplicated here."),
                    ),
                ),
                DocSpec(
                    f"specs/{module}.md",
                    "spec",
                    "draft",
                    ("spec", module),
                    f"Specification for {module}.",
                    f"Spec: {module}",
                    (
                        ("Purpose", f"Define implementation behavior for {module}."),
                        ("Interfaces", "Input, Output, State, Error."),
                        ("Runtime Flow", "Validate input -> update state -> record evidence -> return result."),
                        ("Verification", "Commands: TBD. Expected results: TBD."),
                        ("Recovery Notes", "Preserve interfaces, state shape, runtime flow, and verification expectations."),
                    ),
                ),
                DocSpec(
                    f"tasks/modules/{module}-implementation.md",
                    "module-task",
                    "active" if idx % 2 == 0 else "draft",
                    ("module-work", module, "implementation"),
                    f"Module implementation task for {module}.",
                    f"Module Work: {module} Implementation",
                    (
                        ("Module", module),
                        ("Goal", f"Implement or refine {module}."),
                        ("Related Files", "TBD."),
                        ("Next Step", "TBD."),
                        ("Verification", "Commands: TBD. Expected results: TBD."),
                    ),
                ),
                DocSpec(
                    f"decisions/ADR-{idx + 10:04d}_{module}-boundary.md",
                    "decision",
                    "stable",
                    ("decision", module, "boundary"),
                    f"Decision record for {module} boundaries.",
                    f"ADR-{idx + 10:04d}: {module} Boundary",
                    (
                        ("Context", f"{module} needs a stable responsibility boundary."),
                        ("Decision", f"Keep {module} isolated and link related specs/tasks."),
                        ("Consequences", "Future changes should update related specs and task notes."),
                    ),
                ),
                DocSpec(
                    f"meetings/2026/2026-05-{idx + 5:02d}_001_{module}-discussion.md",
                    "meeting",
                    "completed",
                    ("meeting", module, "discussion"),
                    f"Discussion notes for {module}.",
                    f"2026-05-{idx + 5:02d} Meeting 001: {module} Discussion",
                    (
                        ("Purpose", f"Discuss {module} work."),
                        ("Discussion", "Preserve decisions and unresolved questions without silent deletion."),
                        ("Next Candidates", "Create a task note only when work needs to continue."),
                    ),
                ),
            ]
        )
    return tuple(docs)


def all_docs() -> tuple[DocSpec, ...]:
    return DOCS + extra_docs()


SCENARIOS: tuple[Scenario, ...] = (
    Scenario("tool policy safety approval", "destructive command approval tool execution policy", "specs/agent-runtime/tool-execution-policy.md", "Security And Safety Notes"),
    Scenario("metadata required fields", "required frontmatter fields metadata topics summary", "specs/documentation/frontmatter-metadata.md", "Data Structures"),
    Scenario("archive pointer rule", "archive pointer moved content reason active constraints", "specs/documentation/archive-policy.md", "Important Algorithms Or Rules"),
    Scenario("document routing flow", "document routing metadata candidate selected sections", "architecture/document-routing.md", "Data Flow"),
    Scenario("cost control runtime", "cheap verification repeated full suite cost control", "architecture/cost-aware-agent-runtime.md", "Cost Control"),
    Scenario("source loss recovery", "recover project intent source files lost interfaces data structures", "architecture/recovery-model.md", "Recovery Requirements"),
    Scenario("idor test accounts", "IDOR two test accounts response diff evidence", "specs/security/idor-analysis.md", "Runtime Flow"),
    Scenario("arm64 boundary", "ARM64 privilege boundary disassemble call edge input flow", "specs/low-level/arm64-boundary-analysis.md", "Runtime Flow"),
    Scenario("agents md decision", "why use cost-aware AGENTS md decision", "decisions/ADR-0001_use-cost-aware-agents-md.md", "Decision"),
    Scenario("split templates decision", "split templates from guide expensive to read", "decisions/ADR-0002_split-templates-from-guide.md", "Decision"),
    Scenario("active task next step", "active task next step retrieval benchmark", "tasks/active.md", "Next Step"),
    Scenario("document router module interface", "document router candidate doc context counter interface", "tasks/modules/document-router-retrieval.md", "Key Interfaces"),
    Scenario("initial setup recovery", "initial project setup recovery notes", "tasks/scenarios/scenario-001_initial-project-setup.md", "Recovery Notes"),
    Scenario("meeting decisions", "documentation template review decisions preserve v2 guide policies", "meetings/2026/2026-05-05_001_document-template-review.md", "Decisions"),
    Scenario("product non goals", "agentic security non goals destructive exploits", "product/agentic-security-overview.md", "Non-Goals"),
    Scenario("nl compiler workflow", "natural language compiler build repair workflow", "product/natural-language-compiler.md", "User Workflows"),
    Scenario("archive restrictions", "archive restrictions active constraints current decisions unresolved", "archive/2026/2026-05_completed-planning-history.md", "Archive Restrictions"),
    Scenario("backlog risk", "backlog process onboarding friction risk", "tasks/backlog.md", "Open Risks"),
)


def remove_generated_docs(root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if GENERATED_MARKER in text:
            path.unlink()


def generate_docs() -> None:
    remove_generated_docs(STRUCTURED_ROOT)
    remove_generated_docs(FLAT_ROOT)

    for doc in all_docs():
        structured_path = STRUCTURED_ROOT / doc.rel_path
        write_file(structured_path, frontmatter(doc) + body(doc))

        flat_path = FLAT_ROOT / flat_name(doc)
        write_file(flat_path, body(doc))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            fm = text[: end + len("\n---\n")]
            rest = text[end + len("\n---\n") :]
            return fm, rest
    return "", text


def terms(query: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]


def score_text(query_terms: list[str], text: str) -> int:
    lower = text.lower()
    return sum(lower.count(term) for term in query_terms)


def find_section(text: str, section: str) -> bool:
    return re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE) is not None


def estimate_tokens(chars: int) -> float:
    return chars / 4.0


@dataclass
class SearchResult:
    scenario: str
    success: bool
    exact_file: bool
    exact_section: bool
    context_chars: int
    elapsed_ms: float
    selected: str | None


class StructuredSearcher:
    def __init__(self, root: Path):
        self.root = root
        self.files = sorted(
            path
            for path in root.rglob("*.md")
            if GENERATED_MARKER in path.read_text(encoding="utf-8")
        )

    def search(self, scenario: Scenario) -> SearchResult:
        start = time.perf_counter()
        context = 0
        query_terms = terms(scenario.query)

        project_context = self.root / "PROJECT-CONTEXT.md"
        if project_context.exists():
            context += len(read_text(project_context))

        scored: list[tuple[int, Path]] = []
        for path in self.files:
            text = read_text(path)
            fm, _ = split_frontmatter(text)
            rel = str(path.relative_to(self.root))
            candidate_text = rel + "\n" + fm
            context += len(candidate_text)
            scored.append((score_text(query_terms, candidate_text), path))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected_paths = [path for score, path in scored[:3] if score > 0]
        if not selected_paths:
            selected_paths = [path for _, path in scored[:3]]

        selected = None
        exact_file = False
        exact_section = False
        target_rel = scenario.target_rel_path

        for path in selected_paths:
            text = read_text(path)
            context += len(text)
            rel = str(path.relative_to(self.root))
            if selected is None:
                selected = rel
            if rel == target_rel:
                exact_file = True
                exact_section = find_section(text, scenario.target_section)
                selected = rel
                break

        elapsed_ms = (time.perf_counter() - start) * 1000
        return SearchResult(
            scenario=scenario.name,
            success=bool(selected_paths),
            exact_file=exact_file,
            exact_section=exact_section,
            context_chars=context,
            elapsed_ms=elapsed_ms,
            selected=selected,
        )


class FlatSearcher:
    def __init__(self, root: Path):
        self.root = root
        self.files = sorted(
            path
            for path in root.glob("*.md")
            if GENERATED_MARKER in path.read_text(encoding="utf-8")
        )

    def search(self, scenario: Scenario) -> SearchResult:
        start = time.perf_counter()
        context = 0
        query_terms = terms(scenario.query)

        scored: list[tuple[int, Path]] = []
        for path in self.files:
            text = read_text(path)
            head = text[:900]
            candidate_text = path.name + "\n" + head
            context += len(candidate_text)
            scored.append((score_text(query_terms, candidate_text), path))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected_paths = [path for score, path in scored[:5] if score > 0]
        if not selected_paths:
            selected_paths = [path for _, path in scored[:5]]

        target_flat = flat_name(DocSpec(scenario.target_rel_path, "", "", (), "", "", ()))
        selected = None
        exact_file = False
        exact_section = False

        for path in selected_paths:
            text = read_text(path)
            context += len(text)
            if selected is None:
                selected = path.name
            if path.name == target_flat:
                exact_file = True
                exact_section = find_section(text, scenario.target_section)
                selected = path.name
                break

        elapsed_ms = (time.perf_counter() - start) * 1000
        return SearchResult(
            scenario=scenario.name,
            success=bool(selected_paths),
            exact_file=exact_file,
            exact_section=exact_section,
            context_chars=context,
            elapsed_ms=elapsed_ms,
            selected=selected,
        )


def summarize(results: list[SearchResult]) -> dict[str, float]:
    runs = len(results)
    return {
        "runs": runs,
        "access_success_rate": sum(r.success for r in results) / runs,
        "exact_file_rate": sum(r.exact_file for r in results) / runs,
        "exact_section_rate": sum(r.exact_section for r in results) / runs,
        "avg_context_chars": statistics.mean(r.context_chars for r in results),
        "avg_context_tokens": statistics.mean(estimate_tokens(r.context_chars) for r in results),
        "avg_elapsed_ms": statistics.mean(r.elapsed_ms for r in results),
    }


def print_table(structured: dict[str, float], flat: dict[str, float]) -> None:
    rows = [
        ("runs", structured["runs"], flat["runs"]),
        ("access_success_rate", structured["access_success_rate"], flat["access_success_rate"]),
        ("exact_file_rate", structured["exact_file_rate"], flat["exact_file_rate"]),
        ("exact_section_rate", structured["exact_section_rate"], flat["exact_section_rate"]),
        ("avg_context_chars", structured["avg_context_chars"], flat["avg_context_chars"]),
        ("avg_context_tokens_est", structured["avg_context_tokens"], flat["avg_context_tokens"]),
        ("avg_elapsed_ms", structured["avg_elapsed_ms"], flat["avg_elapsed_ms"]),
    ]
    print("| metric | structured_test | flat_test2 |")
    print("| --- | ---: | ---: |")
    for name, a, b in rows:
        if isinstance(a, float):
            print(f"| {name} | {a:.4f} | {b:.4f} |")
        else:
            print(f"| {name} | {a} | {b} |")


def run_benchmark(iterations: int) -> None:
    structured_searcher = StructuredSearcher(STRUCTURED_ROOT)
    flat_searcher = FlatSearcher(FLAT_ROOT)

    structured_results: list[SearchResult] = []
    flat_results: list[SearchResult] = []
    for _ in range(iterations):
        for scenario in SCENARIOS:
            structured_results.append(structured_searcher.search(scenario))
            flat_results.append(flat_searcher.search(scenario))

    structured_summary = summarize(structured_results)
    flat_summary = summarize(flat_results)
    print_table(structured_summary, flat_summary)

    structured_failures = [r for r in structured_results if not r.exact_section]
    flat_failures = [r for r in flat_results if not r.exact_section]
    print()
    print(f"structured_failures: {len(structured_failures)}")
    print(f"flat_failures: {len(flat_failures)}")
    if structured_failures[:5]:
        print("structured_failure_examples:")
        for failure in structured_failures[:5]:
            print(f"- {failure.scenario}: selected={failure.selected}")
    if flat_failures[:5]:
        print("flat_failure_examples:")
        for failure in flat_failures[:5]:
            print(f"- {failure.scenario}: selected={failure.selected}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--iterations", type=int, default=50)
    args = parser.parse_args()

    if args.generate:
        generate_docs()
    run_benchmark(args.iterations)


if __name__ == "__main__":
    main()
