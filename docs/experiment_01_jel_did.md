# Experiment 01 — JEL-DiD

Date: First real-package stress test

Package:

pedrohcgs/JEL-DiD

Paper:

Callaway, Goodman-Bacon, and Sant'Anna Difference-in-Differences survey project.

Repository characteristics:

* R-based workflow
* renv.lock present
* Public data included
* Large dependency graph (~203 packages)
* Representative of modern empirical economics workflows

---

# Objective

Move beyond toy examples and test reprocheck against a real replication package.

The goal was not success.

The goal was discovering failure modes.

---

# Prediction

Before execution, the following predictions were made.

## Detect

Expected:

* R package
* renv.lock
* Multiple scripts
* Master entry script

Prediction:

PASS

---

## Recipe

Expected:

* Dockerfile generated from renv.lock
* Exact package restoration

Prediction:

PASS

---

## Run

Expected:

Environment failure caused by a missing system dependency.

Prediction:

FAIL

---

## Check

Expected:

Unreachable because execution would likely fail before output generation.

Prediction:

UNREACHABLE

---

# Results

## Detect

Result:

PASS

Detected:

* R workflow
* R 4.4.2
* Multiple scripts
* Entry script correctly identified

Prediction accuracy:

CORRECT

---

## Recipe

Result:

PASS

Generated Dockerfile successfully.

renv.lock recognized.

Prediction accuracy:

CORRECT

---

## Run

Result:

FAIL

Build proceeded through approximately 174 packages before failure.

Failure occurred while loading:

Rglpk

Error:

Missing shared library:

libglpk.so.40

Important observation:

The package itself installed successfully.

The failure occurred during package load validation.

This was not a compilation failure.

This was a runtime shared-library failure.

Prediction accuracy:

CORRECT CATEGORY

INCORRECT MECHANISM

---

## Check

Result:

UNREACHABLE

No output generated.

Prediction accuracy:

CORRECT

---

# Key Discovery

The environment reconstruction layer is significantly stronger than expected.

Observations:

* RSPM binaries installed successfully
* GitHub packages installed successfully
* renv restoration worked
* Docker build progressed deep into dependency installation

The first blocking issue was not package installation.

The first blocking issue was missing operating-system libraries.

This substantially reduced perceived risk.

---

# Failure Modes Discovered

## FM-01 — MISSING_RUNTIME_LIBRARY

Description:

Package installs successfully.

Runtime shared library missing.

Example:

Rglpk

Missing:

libglpk.so.40

Impact:

HIGH

Expected frequency:

HIGH

---

## FM-02 — RENV_LIBRARY_PATH_MISMATCH

Description:

Packages restored into one library location.

Runtime activates a different renv path.

Impact:

MEDIUM

---

## FM-03 — DOUBLE_RESTORE

Description:

Dockerfile restores packages.

Project restores packages again during execution.

Impact:

LOW

---

## FM-04 — OUTPUT_FORMAT_INCOMPATIBLE

Description:

Economics packages typically emit:

* LaTeX
* PDF
* Excel

rather than:

output/code_output.csv

Impact:

VERY HIGH

Expected frequency:

VERY HIGH

---

## FM-05 — PUBLISHED_OUTPUT_IN_REPO

Description:

Many repositories already contain generated outputs.

Examples:

* _R.tex
* _stata.tex

Potential implication:

Some verification may be possible without execution.

Impact:

UNKNOWN

---

# Follow-Up Work

The next objective became:

Prove FM-01 is fixable.

Approach:

Introduce package-to-system-library mappings.

Examples:

* Rglpk → libglpk40
* sf → gdal/geos/proj libraries
* xml2 → libxml2-dev

The goal was to rerun JEL-DiD and discover the next failure.

---

# Lessons Learned

The roadmap should emerge from real packages.

Not from theoretical architecture discussions.

Preferred process:

Run package
→ Observe failure
→ Categorize failure
→ Build capability
→ Repeat

Each real package teaches more than speculative design.

---

# Experiment Status

SUCCESS

Although execution did not complete, the experiment achieved its objective.

Five new failure modes were identified.

The architecture survived first contact with a real economics replication package.
