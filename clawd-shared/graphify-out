# OmniPools Architecture Brief — omnipoolsaz.com
**Generated:** 2026-04-13 from Graphify analysis (1733 nodes, 1927 edges, 430 communities)
**Stack:** Vite + React + TypeScript + Supabase + Tailwind

---

## Application Purpose
Pool electrical screening & design tool for Omni Pool Builders. Takes project intake data (address, equipment, pool specs) and runs electrical demand calculations, hydraulics analysis, heater sizing, site intelligence, and generates professional reports.

---

## Page Routes (src/pages/)
| Page | Purpose |
|------|---------|
| `Index.tsx` | Landing / entry point |
| `Dashboard.tsx` | Main project dashboard |
| `Projects.tsx` | Project listing/management |
| `PoolElectricalDemand.tsx` | **Core tool** — electrical demand calculator |
| `HydraulicsCalculator.tsx` | Hydraulic head loss & pipe sizing |
| `HeatCostCalculator.tsx` | Heater cost/efficiency analysis |
| `ToolFlow.tsx` | Guided workflow through tools |
| `AdminPanel.tsx` | Admin controls |
| `AssumptionsAdmin.tsx` | Configurable calculation defaults |
| `EquipmentAudit.tsx` | Equipment database audit |
| `HeaterAudit.tsx` | Heater database audit |
| `ImportWhitegoods.tsx` | Pipe/fitting/valve data import |
| `DatabaseHealth.tsx` | DB health monitoring |
| `SystemAudit.tsx` | System-wide audit |
| `ProfileSettings.tsx` | User profile |
| `TestScenarios.tsx` | Test scenario runner |
| `BaselineTest.tsx` | Baseline demand testing |
| `ControllerSpec.tsx` | Controller specification |
| `HeaterCalcTest.tsx` / `HeaterDbTest.tsx` / `HeaterLiveTest.tsx` | Heater test pages |
| `StoryDemo.tsx` | Story layer demo |
| `NotFound.tsx` | 404 |

---

## Core Engine Libraries (src/lib/)
| Module | Purpose |
|--------|---------|
| `intake/` | Project intake parsing — CRM notes, equipment images, pool stats |
| `electricalRules/` | NEC-compliant electrical calculations, standard loads detection |
| `hydraulics/` | Pipe sizing, head loss, flow rate calculations |
| `heaterCalculations/` | Tiered heat loss, BTU sizing, fuel cost analysis |
| `baselineDemand/` | House baseline electrical demand estimation |
| `feederSizing/` | Wire gauge & feeder sizing per NEC |
| `poolSubpanel/` | Subpanel load calculations |
| `unifiedElectrical/` | Unified electrical output combining all sources |
| `equipmentClassifier/` | Equipment type detection from specs/images |
| `controllerSelection/` | Automation controller recommendation |
| `siteIntelligence/` | Property/site data enrichment (satellite, weather, parcel) |
| `geocoding/` | Address → GPS → PLSS → parcel data |
| `propertySquareFootage/` | Square footage estimation |
| `panelPhotoConfidence/` | Panel photo analysis confidence scoring |
| `serviceUtilization/` | Service capacity utilization calculations |
| `installationSummary/` | Final installation summary generation |
| `preliminaryScreening/` | Quick pass/fail screening |
| `dataFlow/` | Data flow verification between parsers and calculators |
| `storyLayer/` | Narrative output generation |
| `verification/` | Calculation verification & validation |
| `systemAudit/` | System-wide audit tools |
| `testRuns/` | Test run infrastructure |
| `artifacts/` | Output artifact management |

---

## Component Tree (src/components/)
| Group | Purpose |
|-------|---------|
| `intake/` | Intake forms, data flow diagrams, health panels |
| `electrical/` | Electrical calculation cards, hooks, views |
| `hydraulics/` | Hydraulic calculator UI |
| `heater/` | Heater sizing UI |
| `parser/` | CRM/equipment parser UI |
| `ingestion/` | Data ingestion workflows |
| `controllerSelection/` | Controller selection UI |
| `siteIntelligence/` | Site intel cards |
| `output/` | Output views and reports |
| `results/` | Results display |
| `reports/` | Report generation |
| `scenarios/` | Test scenario management + data flow test helpers |
| `sessions/` | Session management |
| `tabs/` | Tab components (DesignerResultsTab is the main output) |
| `layout/` | Page layout |
| `auth/` | Authentication |
| `testing/` | Test utilities |
| `ui/` | Shared UI primitives (shadcn) |

---

## Supabase Edge Functions (supabase/functions/)
| Function | Purpose |
|----------|---------|
| `geocode-address` | Address geocoding |
| `site-intelligence` | Site data enrichment |
| `parse-crm-notes` | AI-powered CRM note parsing |
| `parse-equipment-image` | Equipment photo analysis |
| `parse-pool-stats` | Pool statistics extraction |
| `analyze-panel` | Electrical panel photo analysis |
| `heating-analysis` | Heater analysis |
| `generate-report` | PDF report generation |
| `ai-task-suggestions` | AI task recommendations |
| `tempest-weather` | Weather data integration |
| `import-whitegoods` | Pipe/fitting data import |
| `send-notification` | Notification dispatch |
| `upload-file` | File upload handling |
| `delete-account` | Account deletion |

---

## Key Data Flow
```
Intake (address, equipment, CRM notes)
  → Parsers (parse-crm-notes, parse-equipment-image, parse-pool-stats)
  → Equipment Classifier
  → Parallel Calculators:
      ├── Electrical Rules (NEC) → Baseline Demand → Feeder Sizing → Subpanel
      ├── Hydraulics → Head Loss → Pipe Sizing
      └── Heater Calculations → Tiered Heat Loss → BTU Sizing
  → Unified Electrical Output
  → Site Intelligence Enrichment (geocoding, weather, parcel)
  → Installation Summary
  → Story Layer (narrative generation)
  → Report Output (PDF, JSON, clipboard)
```

---

## Key Architectural Patterns
1. **Parser → Calculator → Output pipeline** — data flows through parsers into calculation engines, results unified at output
2. **Data Flow Verification** — built-in system to verify data integrity between pipeline stages
3. **Configurable assumptions** — calculation defaults stored in Supabase `calculation_assumptions` table
4. **Equipment database** — `equipment` table with pump/heater/filter specs, `omni_whitegoods_master` for pipes/fittings
5. **Scenario testing** — built-in test scenario infrastructure with data flow validation
6. **Tiered build classification** — Standard/Premium tiers affecting calculations
7. **Confidence scoring** — parsers and calculators output confidence levels

---

## Database (Supabase)
- `equipment` — pumps, heaters, filters with specs
- `omni_whitegoods_master` — pipes, fittings, valves
- `calculation_assumptions` — configurable defaults by category
- Projects, sessions, user data tables
- RLS policies for auth

---

*Source: Graphify AST extraction of 436 files, 566K words. Full graph at graphify-out/graph.json.*
