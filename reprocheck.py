#!/usr/bin/env python3
"""
reprocheck  --  a reproducibility-verification tool (work in progress).

Pipeline:
    detect    -> inspect package, infer R version + packages
    recipe    -> generate Dockerfile
    run       -> build/run container and capture logs
    check     -> compare code output to published paper numbers
    pipeline  -> detect -> recipe -> run -> check in one command
"""

import os
import shutil
import subprocess
import sys

import detector
import recipe as recipe_mod


def cmd_detect(package_dir):
    manifest = detector.detect(package_dir)
    detector.print_manifest(manifest)
    return manifest


def cmd_recipe(package_dir, promote=False):
    manifest = detector.detect(package_dir)
    detector.print_manifest(manifest)

    dockerfile = recipe_mod.generate_dockerfile(manifest)
    out_path = os.path.join(package_dir, "Dockerfile.reprocheck")

    with open(out_path, "w") as f:
        f.write(dockerfile)

    print("Generated Dockerfile:")
    print("-" * 62)
    print(dockerfile, end="")
    print("-" * 62)
    print(f"Written to: {out_path}")

    if promote:
        final_path = os.path.join(package_dir, "Dockerfile")
        shutil.copyfile(out_path, final_path)
        print(f"Promoted to: {final_path}")
    else:
        print("Review it, rename to 'Dockerfile' if it looks right, then `run`.")
    print()

    return out_path


def cmd_run(package_dir):
    dockerfile = os.path.join(package_dir, "Dockerfile")
    if not os.path.exists(dockerfile):
        alt = os.path.join(package_dir, "Dockerfile.reprocheck")
        print(f"No 'Dockerfile' in {package_dir}.")
        if os.path.exists(alt):
            print(f"Found '{alt}'. Review it and rename it to 'Dockerfile' first.")
        else:
            print("Run `recipe` first to generate one.")
        sys.exit(2)

    tag = "reprocheck-run"
    log_path = os.path.join(package_dir, "run.log")

    print("Building the container...")
    build = subprocess.Popen(
        ["docker", "build", "-t", tag, package_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    with open(log_path, "w") as log:
        for line in build.stdout:
            print(line, end="")
            log.write(line)

    build.wait()
    if build.returncode != 0:
        print("Build failed. Read the error above; that's the environment problem.")
        print(f"Log written to: {log_path}")
        sys.exit(1)

    print("Running the code in the container...")
    abspath = os.path.abspath(package_dir)
    run = subprocess.Popen(
        ["docker", "run", "--rm", "-v", f"{abspath}:/project", tag],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    with open(log_path, "a") as log:
        log.write("\n\n--- RUN ---\n")
        for line in run.stdout:
            print(line, end="")
            log.write(line)

    run.wait()
    if run.returncode != 0:
        print("The code did not finish cleanly. That's a real result -- log it.")
        print(f"Log written to: {log_path}")
        sys.exit(1)

    output_csv = os.path.join(package_dir, "output", "code_output.csv")
    if os.path.exists(output_csv):
        print(f"Done. Found output CSV: {output_csv}")
        return output_csv

    print("Done, but no output/code_output.csv was found.")
    print("This package likely writes outputs in another format.")
    return None


def cmd_check(published_csv, output_csv):
    here = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [sys.executable, os.path.join(here, "checker.py"), published_csv, output_csv]
    )
    return result.returncode


def cmd_pipeline(package_dir, published_csv):
    print("== DETECT ==")
    cmd_detect(package_dir)

    print("== RECIPE ==")
    cmd_recipe(package_dir, promote=True)

    print("== RUN ==")
    output_csv = cmd_run(package_dir)

    if not output_csv:
        print("ERROR: pipeline cannot check because no output/code_output.csv was produced.")
        sys.exit(1)

    print("== CHECK ==")
    code = cmd_check(published_csv, output_csv)
    sys.exit(code)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "detect" and len(args) == 1:
        cmd_detect(args[0])
    elif command == "recipe" and len(args) == 1:
        cmd_recipe(args[0])
    elif command == "run" and len(args) == 1:
        cmd_run(args[0])
    elif command == "check" and len(args) == 2:
        cmd_check(args[0], args[1])
    elif command == "pipeline" and len(args) == 2:
        cmd_pipeline(args[0], args[1])
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
