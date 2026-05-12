# Scenario Reports Home

Canonical location for all scenario.test_report artifacts.

## Path Convention
`C:\Users\aaron\clawd-shared\scenario-reports\{scenario-id}.md`

## Registration Rule
Every scenario report MUST also be registered as a Ledger event:
- event_type: `scenario.test_report`
- project_id: relevant project
- payload must include: scenario_id, result (PASS/FAIL/INCONCLUSIVE), file_path, evidence_pointers[]

## Template
See signal-catalog-v1.1.md for the scenario.test_report shape.
