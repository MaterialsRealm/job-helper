## Slurm wait dashboard

Run directly after installing with `uv tool install /home/qz3973/job-helper --force`:

```bash
job-wait-dashboard
job-wait-dashboard --partition amd
job-helper wait-dashboard --partition amd
```

If `--partition` is omitted, `job-helper` checks
`~/.config/job-helper/config.toml`, then Slurm's default partition from
`sinfo`, then falls back to `amd`.

Example config:

```toml
[slurm]
partition = "amd"
```
