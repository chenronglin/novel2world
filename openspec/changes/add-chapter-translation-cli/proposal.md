# Change: Add chapter translation CLI pipeline

## Why
Current tooling lacks an executable workflow to run the multi-agent translation pipeline end-to-end, blocking validation of the knowledge base and translation flow described in the PRD.

## What Changes
- Introduce a CLI command that accepts project and chapter identifiers and orchestrates analysis, translation, and consistency validation.
- Integrate terminology knowledge base lookup so agents operate on curated English equivalents.
- Persist translation outputs alongside validation results for downstream optimization and human review.

## Impact
- Affected specs: `chapter-translation`
- Affected code: `main.py`, new translation pipeline module(s), persistence layer for translation outputs
