"""Render Slurm wait estimates as a terminal dashboard."""

from datetime import datetime

from job_helper.config import DEFAULT_PARTITION
from job_helper.slurm import Job, get_jobs, get_partition_rows
from job_helper.tables import aligned_table, natural_columns


def parse_slurm_time(value: str) -> datetime | None:
    if not value or value in {"N/A", "Unknown", "None"}:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None


def human_delta(seconds: int) -> str:
    if seconds <= 0:
        return "now"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days} day" + ("" if days == 1 else "s"))
    if hours:
        parts.append(f"{hours} hr" + ("" if hours == 1 else "s"))
    if minutes or not parts:
        parts.append(f"{minutes} min")
    return " ".join(parts)


def human_clock(value: datetime, now: datetime) -> str:
    date = value.date()
    today = now.date()
    clock = value.strftime("%I:%M %p").lstrip("0")
    if date == today:
        return f"today {clock}"
    if date.toordinal() == today.toordinal() + 1:
        return f"tomorrow {clock}"
    if value.year == now.year:
        return f"{value.strftime('%b')} {value.day} {clock}"
    return f"{value.strftime('%b')} {value.day}, {value.year} {clock}"


def human_now(now: datetime) -> str:
    clock = now.strftime("%I:%M:%S %p").lstrip("0")
    return f"{now.strftime('%a %b')} {now.day}, {now.year} {clock}"


def job_rows(jobs: list[Job], now: datetime) -> list[list[str]]:
    rows: list[list[str]] = []
    for job in jobs:
        start = parse_slurm_time(job.start_time)
        wait = "unknown"
        start_text = job.start_time
        if start is not None:
            wait = human_delta(int((start - now).total_seconds()))
            start_text = human_clock(start, now)
        rows.append(
            [
                job.jobid,
                job.name,
                job.qos,
                job.state,
                job.nodes,
                job.cpus,
                wait,
                start_text,
                job.reason,
            ]
        )
    return rows


def render_jobs_table(jobs: list[Job], now: datetime) -> str:
    headers = ["JOBID", "NAME", "QOS", "STATE", "NODES", "CPUS", "WAIT", "START", "REASON"]
    rows = job_rows(jobs, now)
    columns = natural_columns(
        headers,
        rows,
        right_align={"NODES", "CPUS"},
        shrinkable={"NAME", "REASON"},
        max_widths={"NAME": 24, "WAIT": 18, "START": 18, "REASON": 40},
    )
    return aligned_table(columns, rows)


def render_partition_table(partition: str, rows: list[list[str]]) -> str:
    if not rows:
        return f"No partition data found for {partition}."
    headers = ["PARTITION", "AVAIL", "NODES", "STATE", "CPUS(A/I/O/T)"]
    columns = natural_columns(headers, rows, right_align={"NODES"})
    return aligned_table(columns, rows)


def render_dashboard(
    user: str,
    partition: str = DEFAULT_PARTITION,
    states: str = "PD,R",
    *,
    now: datetime | None = None,
    jobs: list[Job] | None = None,
    partition_rows: list[list[str]] | None = None,
) -> str:
    current_time = now or datetime.now()
    current_jobs = jobs if jobs is not None else get_jobs(user, states)
    current_partition_rows = (
        partition_rows
        if partition_rows is not None
        else get_partition_rows(partition)
    )

    lines = [
        f"Slurm wait dashboard for {user}",
        f"Updated: {human_now(current_time)}",
        "",
        f"Partition {partition}:",
        render_partition_table(partition, current_partition_rows),
        "",
    ]
    if not current_jobs:
        lines.append(f"No jobs found for states: {states}")
    else:
        lines.extend(
            [
                render_jobs_table(current_jobs, current_time),
                "",
                "Note: START is Slurm's estimate; it can move as priority, backfill, and other jobs change.",
            ]
        )
    return "\n".join(lines)
