#!/usr/bin/env python3
"""
checker.py  --  the first real brick of the verification product.

It answers the only question a journal actually pays for:
    "Do the numbers the code produced match the numbers printed in the paper?"

It does NOT run anyone's code (that's the Runner's job, the Docker part).
It just compares two lists of numbers and labels each one:

    PASS       the code's number rounds to what the paper printed
    UNCERTAIN  close, but doesn't quite round to it -- a human should glance
    FAIL       clearly different
    MISSING    the paper reports this number, but the code never produced it

Run it like this:
    python3 checker.py paper_published.csv code_output.csv
"""

import csv
import sys

# How wide the "UNCERTAIN" zone is, measured in units of the last printed digit.
UNCERTAIN_FACTOR = 1.0


def decimals_of(text):
    """How many digits are printed after the decimal point, e.g. '1.42' -> 2."""
    text = text.strip()
    if "." in text:
        return len(text.split(".")[1])
    return 0


def load_published(path):
    """Read the paper's numbers. Keep them as STRINGS so '0.60' keeps its
    two decimals (that tells us the paper's precision)."""
    rows = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            key = (r["table"], r["sample"], r["quantity"])
            rows[key] = r["published"].strip()
    return rows


def load_output(path):
    """Read the code's numbers as actual numbers (full precision)."""
    rows = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            key = (r["table"], r["sample"], r["quantity"])
            rows[key] = float(r["value"])
    return rows


def classify(published_str, code_value):
    """
    The paper printed, say, 1.42. That really means
    somewhere in [1.415, 1.425) because the author rounded.

    PASS       -> inside rounding interval
    UNCERTAIN  -> just outside rounding interval
    FAIL       -> clearly different
    """
    d = decimals_of(published_str)

    published = float(published_str)

    unit = 10 ** (-d)
    half = unit / 2.0

    diff = abs(code_value - published)

    if diff <= half:
        return "PASS"
    elif diff <= half + UNCERTAIN_FACTOR * unit:
        return "UNCERTAIN"
    else:
        return "FAIL"


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 checker.py <paper_published.csv> <code_output.csv>")
        sys.exit(2)

    published = load_published(sys.argv[1])
    output = load_output(sys.argv[2])

    results = []

    for key in published:
        pub_str = published[key]

        if key not in output:
            results.append((key, pub_str, None, "MISSING"))
        else:
            status = classify(pub_str, output[key])
            results.append((key, pub_str, output[key], status))

    print()
    print(f"{'SAMPLE':<14}{'QUANTITY':<14}{'PAPER':>8}{'CODE':>12}   STATUS")
    print("-" * 62)

    for (table, sample, quantity), pub_str, code_val, status in results:
        code_txt = "   --   " if code_val is None else f"{code_val:.4f}"

        print(
            f"{sample:<14}"
            f"{quantity:<14}"
            f"{pub_str:>8}"
            f"{code_txt:>12}   "
            f"{status}"
        )

    counts = {"PASS": 0, "UNCERTAIN": 0, "FAIL": 0, "MISSING": 0}

    for *_unused, status in results:
        counts[status] += 1

    print("-" * 62)
    print(
        f"PASS: {counts['PASS']}   "
        f"UNCERTAIN: {counts['UNCERTAIN']}   "
        f"FAIL: {counts['FAIL']}   "
        f"MISSING: {counts['MISSING']}"
    )

    if (
        counts["FAIL"] == 0
        and counts["MISSING"] == 0
        and counts["UNCERTAIN"] == 0
    ):
        verdict = "VERIFIED  (every reported number reproduced)"
        code = 0
    elif counts["FAIL"] == 0 and counts["MISSING"] == 0:
        verdict = (
            "NEEDS REVIEW  "
            "(some numbers are borderline -- send to a human)"
        )
        code = 1
    else:
        verdict = "FAILED  (some numbers did not reproduce)"
        code = 1

    print(f"VERDICT: {verdict}")
    print()

    sys.exit(code)


if __name__ == "__main__":
    main()
