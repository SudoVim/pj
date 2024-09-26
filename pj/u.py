#!/usr/bin/env python3
"""
Update submodules for a project using GitHub
"""

import subprocess
import sys
import argparse


def get_default_branch() -> str:
    """
    Get the default branch of the project.
    """
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
    return out.split()[-1].decode()


def update_submodule(submodule: str) -> None:
    """
    Update a single submodule
    """
    subprocess.check_call(["pjp"], cwd=submodule)


def has_changes() -> bool:
    """
    Check if there are changes to the project.
    """
    return bool(subprocess.check_output(["git", "diff", "-M", "-C"])) or bool(
        subprocess.check_output(["git", "diff", "-M", "-C", "--staged"])
    )


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description="Update submodules for a project using GitHub",
    )
    parser.add_argument("submodule", nargs="?", help="Update a single submodule")
    args = parser.parse_args(sys.argv[1:])

    raw = subprocess.check_output(
        [
            "git",
            "submodule",
        ]
    )
    submodules = [l.split()[1].decode() for l in raw.splitlines()]
    if not submodules:
        return 0

    for submodule in submodules:
        if args.submodule and args.submodule != submodule:
            continue

        update_submodule(submodule)
        subprocess.check_call(
            [
                "git",
                "add",
                submodule,
            ]
        )

    if not has_changes:
        print("No changes")
        return 0

    commit_title = (
        "Update submodules"
        if not args.submodule and len(submodules) > 1
        else f"Update {submodules[0]} submodule"
    )
    subprocess.check_call(["git", "checkout", "-b", "update-submodules"])
    subprocess.check_call(["git", "commit", "-m", commit_title])
    subprocess.check_call(
        [
            "gh",
            "pr",
            "create",
            "--base",
            get_default_branch(),
            "--title",
            commit_title,
        ]
    )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
