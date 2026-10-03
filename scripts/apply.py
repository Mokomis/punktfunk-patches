#!/usr/bin/env python3
"""Validate and optionally apply the archived patch to its exact tested source base."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def git(root, *args, check=False):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=check)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="check without changing files (default)")
    mode.add_argument("--apply", action="store_true", help="apply after successful checks")
    args = parser.parse_args()
    data = Path(__file__).resolve().parents[1] / "patchsets/0.42.0-reconnect-fix.3"
    manifest = json.loads((data / "manifest.json").read_text())
    patch = data / "reconnect-fix.patch"
    if hashlib.sha256(patch.read_bytes()).hexdigest() != manifest["patch_sha256"]:
        sys.exit("patch checksum mismatch")
    root = args.checkout.resolve()
    head = git(root, "rev-parse", "HEAD", check=True).stdout.strip()
    if head != manifest["base_commit"]:
        sys.exit("checkout is not the tested v0.42.0 commit; review and port fixes for this release first")
    if git(root, "apply", "--reverse", "--check", str(patch)).returncode == 0:
        print("patchset is already applied")
        return
    if git(root, "diff", "--quiet").returncode or git(root, "diff", "--cached", "--quiet").returncode:
        sys.exit("checkout has tracked changes; use a clean checkout")
    result = git(root, "apply", "--check", str(patch))
    if result.returncode:
        sys.exit(result.stderr.strip() or "patch does not apply cleanly")
    if args.apply:
        git(root, "apply", str(patch), check=True)
        print("patchset applied; build and verify before installing")
    else:
        print("patch checksum, tested base and application check passed; files unchanged")


if __name__ == "__main__":
    main()
