"""
    Defiens a dataclass for the parameters returned by Github after a release through webhook
"""

from dataclasses import dataclass


@dataclass
class GithubReleaseParam:
    """
        Dataclass for all the parameters of a GitHub release
    """
    repository_name: str
    version: str
    body: str
