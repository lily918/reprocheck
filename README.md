# reprocheck

A reproducibility-verification tool for empirical papers, work in progress. This
is the skeleton of the real product: point it at a replication package, and it
moves toward a graded verdict on whether the code reproduces the paper.

## The pipeline

    detect  ->  look at the package, figure out the R version + packages it needs
    recipe  ->  write a Dockerfile from that          (the machine writes the recipe)
    run     ->  build the container, run the code, capture outputs
    check   ->  compare the outputs to the paper's published numbers

## What works right now

- **detect** is automated. It reads every R script for `library()` / `::`
  imports, and if the package shipped an `renv.lock`, it pulls the exact R
  version and pinned package versions.

- **recipe** is automated. It writes a Dockerfile from what detect found.

- **check** is the grader. PASS / UNCERTAIN / FAIL / MISSING per number,
  never bluffs a pass.

- **run** shells out to Docker to build and run.

## Try it

```bash
# 1. See what the tool detects about a package
python3 reprocheck.py detect /path/to/package

# 2. Let it write the Dockerfile
python3 reprocheck.py recipe /path/to/package

# 3. Build + run it
python3 reprocheck.py run /path/to/package

# 4. Grade the outputs against the paper
python3 reprocheck.py check paper_published.csv code_output.csv
```

Or run everything:

```bash
python3 reprocheck.py pipeline /path/to/package paper_published.csv
```

## What I tested it on

- Base-R toy package
- Mankiw–Romer–Weil reproduction
- JEL-DiD Experiment 01

## Known limitations

1. **Entry script detection**
   - Currently filename-based heuristics only.

2. **Outputs aren't generalized yet**
   - Most economics packages write LaTeX, PDF, Excel, or RDS outputs.
   - `output/code_output.csv` is still a convention, not a universal adapter.

3. **Paper numbers aren't extracted automatically**
   - `paper_published.csv` is currently hand-created.

4. **Language support**
   - R-first.
   - Python, Stata, Julia not yet supported.

5. **Label matching**
   - Exact matching only.

## Failure taxonomy discovered so far

### FM-01 — MISSING_RUNTIME_LIBRARY

Binary R package installs successfully but fails to load because a shared
library is missing from the base image.

Example:

- `Rglpk`
- missing `libglpk.so.40`

### FM-02 — RENV_LIBRARY_PATH_MISMATCH

Docker restore succeeds but runtime activates a different renv library path.

### FM-03 — DOUBLE_RESTORE

Dockerfile restores packages and the project restores them again at runtime.

### FM-04 — OUTPUT_FORMAT_INCOMPATIBLE

Package writes LaTeX/PDF outputs rather than `code_output.csv`.

### FM-05 — PUBLISHED_OUTPUT_IN_REPO

Published tables already exist inside the repository and may be parseable
without executing code.

## Next objective

Get more real replication packages running and build the failure taxonomy from
observed breakage rather than assumptions.
