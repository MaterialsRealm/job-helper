"""Command-line entry points."""

import argparse
import os
import sys
import time

from job_helper import __version__
from job_helper.wait_dashboard import render_dashboard


def job_wait_dashboard(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show wait estimates for Slurm jobs.")
    parser.add_argument(
        "-u",
        "--user",
        default=os.environ.get("USER", ""),
        help="Slurm user to inspect.",
    )
    parser.add_argument(
        "-p",
        "--partition",
        default="amd",
        help="Slurm partition for the cluster summary.",
    )
    parser.add_argument(
        "-t",
        "--states",
        default="PD,R",
        help="Job states passed to squeue, e.g. PD for pending or PD,R for pending/running.",
    )
    parser.add_argument("-w", "--watch", type=int, default=0, help="Refresh every N seconds.")
    args = parser.parse_args(argv)

    if not args.user:
        print("Could not determine user; pass --user.", file=sys.stderr)
        return 2

    while True:
        if args.watch:
            print("\033[2J\033[H", end="")
        try:
            print(render_dashboard(args.user, args.partition, args.states))
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            return 1
        if not args.watch:
            return 0
        time.sleep(args.watch)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="job-helper")
    parser.add_argument("--version", action="store_true", help="Show package version.")
    subparsers = parser.add_subparsers(dest="command")

    wait_parser = subparsers.add_parser("wait-dashboard", help="Show Slurm wait estimates.")
    wait_parser.add_argument("-u", "--user", default=os.environ.get("USER", ""))
    wait_parser.add_argument("-p", "--partition", default="amd")
    wait_parser.add_argument("-t", "--states", default="PD,R")
    wait_parser.add_argument("-w", "--watch", type=int, default=0)

    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if args.command == "wait-dashboard":
        return job_wait_dashboard(
            [
                "--user",
                args.user,
                "--partition",
                args.partition,
                "--states",
                args.states,
                "--watch",
                str(args.watch),
            ]
        )

    parser.print_help()
    return 0
