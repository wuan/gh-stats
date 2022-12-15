# gh-stats
Collect some GitHub repo statistics

* number of stars
* number of downloads
* repo views (count and uniques)
* repo clones (count and uniques)

Views and clones require a token with repo write access to work.

Token useage is encouraged to overcome the API limit for requests without token

## Usage

for now just set an environment variable `GH_USERNAMES=foo,bar` to scan both usernames for repos with at least one star.

Use the env variable `GH_TOKEN` to transfer the corresponding GitHub token.

Crontab example entry:

```cron
*/10 * * * * (cd gh-stats;. venv/bin/activate; git pull; GH_USERNAMES=<comma separated users> python src/h_stats.py) 2>&1 >/dev/null
```