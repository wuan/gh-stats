# gh-stats
Collect some GitHub repo statistics

## Usage

for now just set an environment variable `GH_USERNAMES=foo,bar` to scan both usernames for repos with at least one star.

Crontab example entry:

```cron
*/10 * * * * (cd gh-stats;. venv/bin/activate; git pull; GH_USERNAMES=<comma separated users> python gh_stats.py) 2>&1 >/dev/null
```