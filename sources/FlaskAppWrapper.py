"""
    Thie module has an abstract class to wrap Flask app.
"""

from abc import ABCMeta


class FlaskAppWrapper(metaclass=ABCMeta):
    """
        Abstract wrapper for Flask App, managing Flask specific configurations.
    """

    def __init__(self, app, **configs):
        self.app = app
        self.configs(**configs)

    def configs(self, **configs):
        """
            Stores configurations into Flask app config
        """
        for config, value in configs:
            self.app.config[config.upper()] = value

    # pylint: disable-next=keyword-arg-before-vararg
    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None, *args, **kwargs):
        """
            Add a new endpoint and its handler to the Flask app
        """
        if methods is None:
            methods = ['GET']
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)

    def run(self, **kwargs):
        """
            Starts the Flask app
        """
        self.app.run(**kwargs)
