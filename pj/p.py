#!/usr/bin/env python3
"""
Pull the latest from the default branch
"""

import argparse
import subprocess
import sys


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description="Pull the latest from the default branch",
    )
    parser.parse_args(sys.argv[1:])

    p1 = subprocess.Popen(
        [
            "git",
            "remote",
            "show",
            "origin",
        ],
        stdout=subprocess.PIPE,
    )
    out = subprocess.check_output(
        [
            "grep",
            "HEAD branch",
        ],
        stdin=p1.stdout,
    )
    default_branch = out.split()[-1].decode()

    has_changes = bool(subprocess.check_output(["git", "diff", "-M", "-C"])) or bool(
        subprocess.check_output(["git", "diff", "-M", "-C", "--staged"])
    )

    if has_changes:
        subprocess.check_call(["git", "stash"])

    subprocess.check_call(["git", "checkout", default_branch])
    subprocess.check_call(["git", "pull"])
    out = subprocess.check_output(["git", "remote", "prune", "origin"])

    pruned_branches = set()
    for line in out.splitlines():
        if not line.startswith(b" * [pruned] origin/"):
            continue

        pruned_branches.add(line.split(b" * [pruned] origin/", 1)[1].decode())

    if pruned_branches:
        out = subprocess.check_output(["git", "branch"])

        all_branches = set([l.split(None, 1)[-1].decode() for l in out.splitlines()])

        remove_branches = pruned_branches & all_branches
        if remove_branches:
            subprocess.check_call(["git", "branch", "-D"] + list(remove_branches))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
