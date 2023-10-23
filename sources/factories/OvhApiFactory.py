"""
    This module defines the factory for OVH API
"""
from flask import current_app
import sources.utils.IpAddress as IpAddress
import sources.utils.Constants as cst
import ovh


class OvhApiFactory():
    """
        Class managing the API for OVH

    """
    def __init__(self):
        """
            The factory instanciates the objects it needed to complete the processing of the request.
        """
        self.client = ovh.Client(
            endpoint='ovh-eu',               # Endpoint of API OVH Europe (List of available endpoints)
            application_key=current_app.config[cst.APP_CONFIG_TOKEN_OVH_APP_KEY],
            application_secret=current_app.config[cst.APP_CONFIG_TOKEN_OVH_APP_SECRET],
            consumer_key=current_app.config[cst.APP_CONFIG_TOKEN_OVH_CONSUMER_KEY],
        )

    def get_dedicated_servers(self, app_context):
        """
            Retrieves the list of dedicated servers available
        """
        result = self.client.get('/dedicated/server', iamTags=None)
        return result

    def get_dedicated_server_display_name(self, app_context, server_name):
        """
            Returns display_name of the dedicated server.
        """
        service_info = self.client.get(f'/dedicated/server/{server_name}/serviceInfos')
        service_id = service_info["serviceId"]
        service = self.client.get(f'/service/{service_id}')
        display_name = service["resource"]["displayName"]
        return display_name

    def get_dedicated_server_ips(self, app_context, server_name):
        """
            Return the IPv6 and IPv4 of a dedicated server
        """
        raw_result = self.client.get(f'/dedicated/server/{server_name}/ips')
        print(raw_result)
        result = dict()
        for ip in raw_result:
            ip_split = ip.split("/")
            result[IpAddress.validIPAddress(ip_split[0])] = ip
        return result
