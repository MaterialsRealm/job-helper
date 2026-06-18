"""Command-line entry points."""

import argparse
import os
import sys
import time
from pathlib import Path

from job_helper import __version__
from job_helper.config import (
    DEFAULT_PARTITION,
    configured_partition,
    default_config_path,
    load_config,
)
from job_helper.slurm import get_default_partition
from job_helper.wait_dashboard import render_dashboard


def resolve_partition(cli_partition: str | None, config_path: str | None = None) -> str:
    if cli_partition:
        return cli_partition

    config_file = (
        Path(os.path.expanduser(config_path))
        if config_path
        else default_config_path()
    )
    partition = configured_partition(load_config(config_file))
    if partition:
        return partition

    try:
        partition = get_default_partition()
    except RuntimeError:
        partition = None
    return partition or DEFAULT_PARTITION


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
        default=None,
        help="Slurm partition for the cluster summary.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Config file path. Defaults to ~/.config/job-helper/config.toml.",
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
    partition = resolve_partition(args.partition, args.config)

    while True:
        if args.watch:
            print("\033[2J\033[H", end="")
        try:
            print(render_dashboard(args.user, partition, args.states))
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
    wait_parser.add_argument("-p", "--partition", default=None)
    wait_parser.add_argument("--config", default=None)
    wait_parser.add_argument("-t", "--states", default="PD,R")
    wait_parser.add_argument("-w", "--watch", type=int, default=0)

    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if args.command == "wait-dashboard":
        wait_args = ["--user", args.user, "--states", args.states, "--watch", str(args.watch)]
        if args.partition:
            wait_args.extend(["--partition", args.partition])
        if args.config:
            wait_args.extend(["--config", args.config])
        return job_wait_dashboard(wait_args)

    parser.print_help()
    return 0
