"""
    This module defines the endpoint handler (called listener) for the Support team endpoints.
"""

from sources.handlers.ServerListHandler import ServerListHandler


class SupportListener():
    """
        Class to define the support endpoints handler. It is callable and called when the right url is used.
    """

    def __init__(self):
        """
            The listener instanciates the handlers it will pass the request to so that it is processed.
        """
        self.server_list_handler = ServerListHandler()

    def get_wprocket_ips_human_readable(self):
        """
            Method generating the list of IPs used by WP Rocket and returning it in a list as a string.
        """
        response_payload = self.server_list_handler.generate_wp_rocket_ips_human_readable()
        return response_payload, 200

    def get_wprocket_ipv4_machine_readable(self):
        """
            Method generating the list of IPv4 used by WP Rocket and returning it as a machine readable string
        """
        response_payload = self.server_list_handler.generate_wp_rocket_ipv4_machine_readable()
        return response_payload, 200

    def get_wprocket_ipv6_machine_readable(self):
        """
            Method generating the list of IPv4 used by WP Rocket and returning it as a machine readable string
        """
        response_payload = self.server_list_handler.generate_wp_rocket_ipv6_machine_readable()
        return response_payload, 200
