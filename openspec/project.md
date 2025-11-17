# Project Context

## Purpose
Build an AI-assisted production pipeline for translating long-form Chinese novels into high-quality, terminology-consistent English drafts, combining automated agents with human review.

## Tech Stack
- Python 3.13 (CLI entry point in `main.py`)
- agno (multi-agent orchestration/runtime)
- OpenAI API (LLM-driven analysis, translation, and QA)
- uv package manager with Aliyun PyPI mirror

## Project Conventions

### Code Style
Follow PEP 8 styling, use type hints where practical, prefer explicit function naming, and keep modules small and task-focused.

### Architecture Patterns
Pipeline-oriented architecture built around specialized agents:
- **Analysis Agent** extracts chapter summaries, character lists, and terminology without performing translation.
- **Knowledge Base Manager** stores curated terminology with approved English equivalents prior to translation.
- **Translation Agent** consumes normalized chapter text plus recent context and terminology to produce draft translations with strict terminology adherence.
- **Optimization Agent** (optional) polishes translations while preserving enforced terminology.
- **Consistency Checks** combine rule-based counters and LLM validation to detect drift before handoff to human editors.

### Testing Strategy
Testing approach not yet implemented; plan to introduce pytest-based unit coverage for each agent module plus integration tests for the end-to-end chapter pipeline.

### Git Workflow
Adopt a feature-branch workflow with conventional commits once the repository is initialized; keep agent changes isolated per feature and require review before merge.

## Domain Context
Workflow prioritizes terminology consistency: every character and term must be captured, deduplicated, and paired with an approved English translation before any chapter processing. Chapter translations ingest the last three chapter summaries and the complete terminology table to provide context. Counts of keyword usage between source and translation are compared to guard against drift, with pronoun variations allowed only for character names.

## Important Constraints
- Terminology database must be finalized ahead of translation to avoid inconsistent outputs.
- Translation outputs must pass both rule-based and LLM-based consistency checks before human review.
- External LLM calls should avoid leaking unpublished manuscript content beyond required prompts.
- System must support long-form chapters without exceeding context limits by summarizing prior chapters.

## External Dependencies
- OpenAI API for LLM-powered agents.
- Future connectors for DOCX/text ingestion (TBD).
- Internal terminology knowledge base storage (schema design pending).
