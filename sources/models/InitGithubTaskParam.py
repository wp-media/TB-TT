"""
    Defiens a dataclass for the parameters to pass to GithubTaskHandler.init_github_task
"""

from dataclasses import dataclass


@dataclass
class InitGithubTaskParam:
    """
        Dataclass for all the parameters allowing to initiate a task
    """
    title: str
    body: str
    handle_immediately: bool = False
    assignee: str = 'no-assignee'
    initiator: str = None
    flow: str = 'create_github_task'
