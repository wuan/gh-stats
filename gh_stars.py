#!/usr/bin/env python
import os

import statsd
from github import Github


def list_from_string(input: str):
    if not input:
        return []
    return input.split(",")


if __name__ == "__main__":
    statsd_client = statsd.StatsClient('localhost', 8125, prefix="github_stats")

    usernames = list_from_string(os.environ.get("GH_USERNAMES", ""))

    for username in usernames:
        g = Github()
        # get that user by username
        user = g.get_user(username)

        for repo in user.get_repos():
            stargazers_count = repo.stargazers_count
            if stargazers_count > 0:
                metric_tags = {
                    "username": username,
                    "repository": repo.name
                }
                print(username, repo.name, stargazers_count)
                statsd_client.gauge("stargazers", stargazers_count, tags=metric_tags)
