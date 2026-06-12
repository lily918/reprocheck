"""
detector.py  --  Stage 1 of the tool: look at a package and figure out what
environment it needs, WITHOUT a human reading it.

It fuses two signals:
  1. What the code IMPORTS  (every library()/require()/pkg:: in the R scripts)
  2. What an renv.lock PINS  (exact R version + exact package versions, if present)

Output: a "manifest" describing the environment to rebuild.
"""

import json
import os
import re

# Packages that ship with R itself -- never need installing.
BASE_PKGS = {
    "base", "compiler", "datasets", "graphics", "grDevices", "grid",
    "methods", "parallel", "splines", "stats", "stats4", "tcltk",
    "tools", "utils",
}

# A sensible default if the package gives no R version hint at all.
DEFAULT_R_VERSION = "4.4.1"

# Matches library(x), require(x), requireNamespace("x"), and x::something
IMPORT_PATTERNS = [
    re.compile(r"""\blibrary\(\s*['"]?([A-Za-z][A-Za-z0-9._]*)['"]?\s*\)"""),
    re.compile(r"""\brequire\(\s*['"]?([A-Za-z][A-Za-z0-9._]*)['"]?\s*\)"""),
    re.compile(r"""\brequireNamespace\(\s*['"]([A-Za-z][A-Za-z0-9._]*)['"]"""),
    re.compile(r"""\b([A-Za-z][A-Za-z0-9._]*)::"""),
]

# Filenames that usually mean "this is the script that runs everything."
ENTRY_HINTS = [
    "masterfile",
    "master",
    "_main",
    "main",
    "run_all",
    "run",
    "reproduce",
    "makefile",
]


def find_r_scripts(package_dir):
    scripts = []

    for root, _dirs, files in os.walk(package_dir):
        if ".git" in root:
            continue

        for fn in files:
            if fn.lower().endswith(".r"):
                scripts.append(os.path.join(root, fn))

    return scripts


def detect_imports(scripts):
    found = set()

    for path in scripts:
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue

        for pat in IMPORT_PATTERNS:
            for m in pat.findall(text):
                found.add(m)

    return sorted(
        p for p in found
        if p not in BASE_PKGS and len(p) > 1
    )


def read_renv_lock(package_dir):
    lock_path = os.path.join(package_dir, "renv.lock")

    if not os.path.exists(lock_path):
        return None

    try:
        data = json.load(open(lock_path))
    except (json.JSONDecodeError, OSError):
        return None

    r_version = data.get("R", {}).get("Version")

    versions = {
        name: info.get("Version")
        for name, info in data.get("Packages", {}).items()
    }

    return {
        "r_version": r_version,
        "versions": versions,
        "all_packages": sorted(versions.keys()),
        "has_lock": True,
    }


def guess_entry_script(scripts, package_dir):
    """
    Pick the most likely 'run everything' script.
    """

    def score(path):
        name = os.path.basename(path).lower()

        for i, hint in enumerate(ENTRY_HINTS):
            if hint in name:
                return i

        return len(ENTRY_HINTS) + 1

    if not scripts:
        return None

    best = min(scripts, key=score)

    name = os.path.basename(best).lower()

    if any(h in name for h in ENTRY_HINTS):
        return os.path.relpath(best, package_dir)

    return None


def detect(package_dir):
    scripts = find_r_scripts(package_dir)

    imports = detect_imports(scripts)

    lock = read_renv_lock(package_dir)

    r_version = (
        lock["r_version"]
        if lock and lock.get("r_version")
        else DEFAULT_R_VERSION
    )

    r_version_source = (
        "renv.lock"
        if (lock and lock.get("r_version"))
        else "default (no hint found)"
    )

    packages = []

    for pkg in imports:
        pinned = lock["versions"].get(pkg) if lock else None

        packages.append({
            "name": pkg,
            "version": pinned,
        })

    return {
        "package_dir": package_dir,
        "n_scripts": len(scripts),
        "r_version": r_version,
        "r_version_source": r_version_source,
        "has_renv_lock": bool(lock),
        "packages": packages,
        "renv_packages": lock["all_packages"] if lock else [],
        "entry_script": guess_entry_script(scripts, package_dir),
    }


def print_manifest(m):
    print()
    print(f"  package         : {m['package_dir']}")
    print(f"  R scripts found : {m['n_scripts']}")
    print(f"  R version       : {m['r_version']}  (from {m['r_version_source']})")
    print(f"  renv.lock       : {'yes' if m['has_renv_lock'] else 'no'}")
    print(
        f"  entry script    : "
        f"{m['entry_script'] or '(could not guess -- you set it)'}"
    )
    print(f"  packages needed : {len(m['packages'])}")

    for p in m["packages"]:
        v = p["version"] or "(version not pinned)"
        print(f"      - {p['name']:<16} {v}")

    print()
