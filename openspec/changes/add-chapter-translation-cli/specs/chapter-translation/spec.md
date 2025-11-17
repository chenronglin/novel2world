## ADDED Requirements
### Requirement: Chapter translation CLI execution
The system SHALL provide a `translate-chapter` CLI command that orchestrates chapter translation using curated terminology and recent chapter context.

#### Scenario: Translate chapter with knowledge base context
- **WHEN** the user runs `translate-chapter --project <id> --chapter <id>`
- **THEN** the system SHALL load the chapter content and summaries for the previous three chapters
- **AND** the system SHALL merge the approved terminology table into the agent prompt
- **AND** the system SHALL invoke the translation agent to generate the English draft
- **AND** the system SHALL persist the translation output for later optimization and review

### Requirement: Terminology consistency validation
The system SHALL verify that mandatory terminology occurrences in the translation align with the knowledge base mappings, surfacing any mismatches for remediation.

#### Scenario: Detect terminology drift
- **WHEN** the translation result is produced for a chapter
- **THEN** the system SHALL compare the count of each mandatory terminology item between the source and translation
- **AND** the system SHALL flag discrepancies where required terms are missing or mistranslated
- **AND** the system SHALL record the validation status alongside the translation record
