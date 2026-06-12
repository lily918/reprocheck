# KNOWN_LIMITATIONS.md

This document tracks limitations that are known and accepted at the current stage of development.

The goal is not to eliminate all limitations immediately. The goal is to discover real failure modes from real replication packages and address them systematically.

---

# Current Scope

reprocheck currently focuses on:

* Public replication packages
* R-based workflows
* Environment reconstruction
* Reproducibility verification

It does **not** currently verify whether a paper's methodology is scientifically correct.

The system verifies:

> Does the package reproduce the published results?

Not:

> Is the paper true?

---

# Environment Reconstruction Limitations

## Entry Script Detection

Current implementation relies primarily on filename heuristics.

Examples:

* master.R
* masterfile.R
* run.R
* reproduce.R
* main.R

Limitations:

* Multiple candidate scripts
* Non-standard naming conventions
* Workflow managers (Make, Snakemake, targets)

Current behavior:

* Best-effort guess
* Human review may be required

---

## Language Support

Currently supported:

* R

Not yet supported:

* Stata
* Python
* Julia
* Matlab
* Mixed-language workflows

---

## System Dependencies

Some R packages require operating system libraries.

Examples:

* Rglpk
* sf
* xml2
* curl
* openssl

Current approach:

* Package-to-system-library mapping

Limitation:

* Mapping is incomplete
* New packages may require new rules

---

## Workflow Managers

Not yet supported:

* Snakemake
* GNU Make
* targets
* drake

Current system assumes a directly executable entry script.

---

# renv Limitations

## FM-02 — RENV_LIBRARY_PATH_MISMATCH

Observed in real packages.

Cause:

* Packages restored during image build
* Runtime activates a different library path

Status:

* Known
* Not fully generalized

---

## FM-03 — DOUBLE_RESTORE

Observed in real packages.

Cause:

* Dockerfile performs renv::restore()
* Project script performs renv::restore() again

Status:

* Usually harmless
* Adds runtime overhead

---

# Output Verification Limitations

## FM-04 — OUTPUT_FORMAT_INCOMPATIBLE

Most economics packages do not emit:

output/code_output.csv

Instead they generate:

* LaTeX tables
* PDF tables
* Excel files
* RDS files
* HTML outputs

Current status:

* CSV pathway exists
* General output adapter not yet built

This is expected to be one of the most common failure classes.

---

## Published Number Extraction

Current state:

* paper_published.csv is created manually

Not yet implemented:

* PDF table extraction
* Automatic paper parsing
* Table-to-output alignment

---

## Label Matching

Current behavior:

Exact matching.

Example:

Table I / Non-oil / Intercept

must match exactly.

Not yet implemented:

* Fuzzy matching
* Alias matching
* Semantic matching

---

# Verification Limitations

## Rounding Ambiguity

Example:

Paper:

1.42

Code:

1.418

The true value may round to the published value.

Current handling:

* PASS
* UNCERTAIN
* FAIL

UNCERTAIN exists specifically to avoid false confidence.

Human review remains part of the design.

---

## Human Escalation

The system is not intended to be 100% autonomous.

Some cases will always require review.

Examples:

* Ambiguous matches
* Multiple candidate outputs
* Incomplete documentation
* Missing data
* Rounding edge cases

Escalation is a feature, not a bug.

---

# Methodology Layer

Not yet implemented.

Future goal:

Determine whether code implements the methodology described in the paper.

Examples:

* Difference-in-Differences specifications
* Instrumental variables
* Fixed-effects models
* Event studies

This is expected to be significantly harder than environment reconstruction.

---

# Recovery Notes

The original local project was partially lost due to iCloud placeholder corruption.

Core source files were reconstructed and recovered.

GitHub is now the primary source of truth.

Future work should be committed and pushed regularly.

---

# Guiding Principle

The roadmap comes from real replication packages.

Preferred workflow:

Run package
→ Observe failure
→ Categorize failure
→ Build capability
→ Repeat

Avoid building speculative infrastructure before a real package demonstrates the need.
