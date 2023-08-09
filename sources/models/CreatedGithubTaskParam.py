"""
    Defiens a dataclass for the parameters returned by Github after task creation
"""

from dataclasses import dataclass


@dataclass
class CreatedGithubTaskParam:
    """
        Dataclass for all the parameters allowing to initiate a task
    """
    item_id: str
    item_database_id: int
    project_number: int
