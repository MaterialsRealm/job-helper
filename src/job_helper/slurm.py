"""Small Slurm query helpers."""

import subprocess
from dataclasses import dataclass


SQUEUE_FORMAT = "%i|%j|%q|%T|%D|%C|%M|%l|%R|%S"
SINFO_FORMAT = "%P|%a|%D|%t|%C"


@dataclass(frozen=True)
class Job:
    jobid: str
    name: str
    qos: str
    state: str
    nodes: str
    cpus: str
    elapsed: str
    limit: str
    reason: str
    start_time: str


def run_slurm_command(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"{' '.join(cmd)} failed: {msg}")
    return proc.stdout


def get_jobs(user: str, states: str, *, runner=run_slurm_command) -> list[Job]:
    out = runner(["squeue", "-u", user, "-t", states, "-h", "-o", SQUEUE_FORMAT])
    jobs: list[Job] = []
    for line in out.splitlines():
        parts = line.split("|", 9)
        if len(parts) != 10:
            continue
        jobs.append(Job(*[part.strip() for part in parts]))
    return jobs


def get_partition_rows(partition: str, *, runner=run_slurm_command) -> list[list[str]]:
    out = runner(["sinfo", "-p", partition, "-h", "-o", SINFO_FORMAT])
    return [
        [part.strip() for part in line.split("|", 4)]
        for line in out.splitlines()
        if line.strip()
    ]
