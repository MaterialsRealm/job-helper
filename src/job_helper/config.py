"""User configuration for job-helper."""

from pathlib import Path
import os
import tomllib


DEFAULT_PARTITION = "amd"


def default_config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "job-helper" / "config.toml"
    return Path.home() / ".config" / "job-helper" / "config.toml"


def load_config(path: Path | None = None) -> dict:
    config_path = path or default_config_path()
    if not config_path.exists():
        return {}
    with config_path.open("rb") as config_file:
        return tomllib.load(config_file)


def configured_partition(config: dict) -> str | None:
    slurm_config = config.get("slurm", {})
    if not isinstance(slurm_config, dict):
        return None
    partition = slurm_config.get("partition")
    if not isinstance(partition, str):
        return None
    partition = partition.strip()
    return partition or None
