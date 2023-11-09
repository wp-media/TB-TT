"""
    Defiens a dataclass for the parameters to pass to DeployHandlerParam.deploy_commit
"""

from dataclasses import dataclass


@dataclass
class DeployHandlerParam:
    """
        Dataclass for all the parameters allowing to deploy a commit
    """
    app: str
    env: str
    commit: str
