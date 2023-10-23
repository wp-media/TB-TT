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
        self.client = None

    def _get_ovh_client(self, app_context):
        """
            Return the ovh client and creates it if needed
        """
        if self.client is None:
            app_context.push()
            self.client = ovh.Client(
                endpoint='ovh-eu',               # Endpoint of API OVH Europe (List of available endpoints)
                application_key=current_app.config[cst.APP_CONFIG_TOKEN_OVH_APP_KEY],
                application_secret=current_app.config[cst.APP_CONFIG_TOKEN_OVH_APP_SECRET],
                consumer_key=current_app.config[cst.APP_CONFIG_TOKEN_OVH_CONSUMER_KEY],
            )
        return self.client

    def get_dedicated_servers(self, app_context):
        """
            Retrieves the list of dedicated servers available
        """
        client = self._get_ovh_client(app_context)
        result = client.get('/dedicated/server', iamTags=None)
        return result

    def get_dedicated_server_display_name(self, app_context, server_name):
        """
            Returns display_name of the dedicated server.
        """
        client = self._get_ovh_client(app_context)
        service_info = client.get(f'/dedicated/server/{server_name}/serviceInfos')
        service_id = service_info["serviceId"]
        service = client.get(f'/service/{service_id}')
        display_name = service["resource"]["displayName"]
        return display_name

    def get_dedicated_server_ips(self, app_context, server_name):
        """
            Return the IPv6 and IPv4 of a dedicated server
        """
        client = self._get_ovh_client(app_context)
        raw_result = client.get(f'/dedicated/server/{server_name}/ips')
        result = dict()
        for ip in raw_result:
            ip_split = ip.split("/")
            result[IpAddress.validIPAddress(ip_split[0])] = ip
        return result
