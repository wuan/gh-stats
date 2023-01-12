#/usr/bin/env python
import datetime
import os
from collections import defaultdict

import statsd
from github import Github


#
# What could we add here as well?
#
# * Download count
#   * Including version information
# * Insights / Traffic (requires authentication)
#   * Clones (daily)
#   * Web-Visitors (daily)
#
#

def list_from_string(input: str):
    if not input:
        return []
    return input.split(",")


def download_statistics(statsd_client, username, reponame):
    releases = repo.get_releases()
    total_downloads = 0
    total_downloads_per_extension = defaultdict(lambda: 0)
    for release in releases:
        # print("       ", release)
        release_downloads = 0
        for asset in release.get_assets():
            release_downloads += asset.download_count
            extension = os.path.splitext(asset.name)[1]
            # print(f"         {asset.name} {asset.download_count} {extension} {total_downloads_per_extension[extension]}")
            total_downloads_per_extension[extension] += asset.download_count

        total_downloads += release_downloads
        # print(f"         {release.tag_name} {release_downloads}")

    metric_tags = {
        "username": username,
        "repository": reponame
    }
    if total_downloads > 0:
        print(f"    total downloads: {total_downloads}")
        statsd_client.gauge("downloads.total", total_downloads, tags=metric_tags)
    for extension, download_count in total_downloads_per_extension.items():
        if download_count > 0:
            print(f"    {extension} downloads: {download_count}")
            metric_tags["ext"] = extension
            statsd_client.gauge("downloads.by_ext", total_downloads, tags=metric_tags)


def views_statistics(statsd_client, username, reponame, today):
    metric_tags = {
        "username": username,
        "repository": reponame
    }
    for views in repo.get_views_traffic()["views"]:
        if views.timestamp.date() == today:
            print(f"    views today: count: {views.count}, unique: {views.uniques}")
            statsd_client.gauge("views.count", views.count, tags=metric_tags)
            statsd_client.gauge("views.uniques", views.uniques, tags=metric_tags)


def clones_statistics(statsd_client, username, reponame, today):
    metric_tags = {
        "username": username,
        "repository": reponame
    }
    for clones in repo.get_clones_traffic()["clones"]:
        if clones.timestamp.date() == today:
            print(f"    clones today: count: {clones.count}, unique: {clones.uniques}")
            statsd_client.gauge("clones.count", clones.count, tags=metric_tags)
            statsd_client.gauge("clones.uniques", clones.uniques, tags=metric_tags)


def repo_statistics(statsd_client, username, repo):
    for count, name in [
        (repo.stargazers_count, "stargazers"),
        (repo.forks_count, "forks"),
        (repo.network_count, 'network'),
        (repo.subscribers_count, 'subscribers'),
        (repo.open_issues_count, 'open_issues'),
    ]:
        if count > 0:
            metric_tags = {
                "username": username,
                "repository": repo.name
            }
            print(f"    {name}", count)
            statsd_client.gauge(name, count, tags=metric_tags)




def pulls_statistics(statsd_client, username, reponame):
    pulls = repo.get_pulls(state="open").totalCount
    if pulls > 0:
        metric_tags = {
            "username": username,
            "repository": reponame,
            "state": "open",
        }
        print("    pulls", pulls)
        statsd_client.gauge("pulls", pulls, tags=metric_tags)


if __name__ == "__main__":
    statsd_client = statsd.StatsClient('localhost', 8125, prefix="github_stats")

    usernames = list_from_string(os.environ.get("GH_USERNAMES", ""))

    today_timezone = datetime.timezone(datetime.timedelta(hours=-4))
    today = datetime.datetime.now(tz=today_timezone).date()

    for username in usernames:
        github_token = os.environ.get("GH_TOKEN")
        g = Github(login_or_token=github_token)
        # get that user by username
        user = g.get_user(username)

        for repo in user.get_repos():
            if repo.private:
                continue

            print(f"### {repo.name}")

            if github_token is not None:
                views_statistics(statsd_client, username, repo.name, today)
                clones_statistics(statsd_client, username, repo.name, today)
            pulls_statistics(statsd_client, username, repo.name)
            download_statistics(statsd_client, username, repo.name)
            repo_statistics(statsd_client, username, repo)
