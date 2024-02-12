"""
    This module defines the handler for logic related to listing server IPs.
"""
from sources.factories.SlackMessageFactory import SlackMessageFactory
from sources.factories.OvhApiFactory import OvhApiFactory
from sources.utils import IpAddress


class ServerListHandler():
    """
        Class managing the business logic related to listing servers WP Media uses.

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.slack_message_factory = SlackMessageFactory()
        self.ovh_api_factory = OvhApiFactory()

    def get_groupone_live2_ips(self):
        """
            Lists all IP used by live2 cluster from group.One
        """
        live2_ips = ''
        # Defined in k8s_sips:
        # https://gitlab.one.com/systems/chef-repo/-/blob/master/roles/onecom-global-firewall-macros.json#L173
        live2_ips += "46.30.212.64\n46.30.212.65\n46.30.212.66\n46.30.212.67\n46.30.212.68\n46.30.212.69\n46.30.211.85\n"
        # Added for live2 according to JIRA: https://group-one.atlassian.net/browse/NET-283
        live2_ips += "46.30.212.70\n46.30.212.71\n46.30.212.72\n46.30.212.73\n"
        return live2_ips

    def generate_wp_rocket_ips(self, app_context):
        """
            Generates a text list of all IPs used by WP Rocket
        """
        text = "List of IPs used for WP Rocket:\n\n"

        text += "License validation/activation, update check, plugin information:\n"
        # Defined in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "https://wp-rocket.me\n"
        text += "185.10.9.101\n"
        text += "\n"

        text += "Load CSS Asynchronously:\n"
        # Defined in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "https://cpcss.wp-rocket.me\n"
        text += "46.30.212.116\n"
        text += self.get_groupone_live2_ips()
        text += "\n"

        text += "Remove Unused CSS:\n"
        # SaaS CNAME in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "46.30.212.106\n"
        text += self.get_groupone_live2_ips()
        # OVH servers
        all_server_list = self.ovh_api_factory.get_dedicated_servers(app_context)
        ovh_ipv4 = ''
        ovh_ipv6 = ''
        for server_name in all_server_list:
            display_name = self.ovh_api_factory.get_dedicated_server_display_name(app_context, server_name)
            if 'worker' in display_name:
                server_ips = self.ovh_api_factory.get_dedicated_server_ips(app_context, server_name)
                ovh_ipv4 += server_ips[IpAddress.IP_ADDRESS_IPV4] + "\n"
                ovh_ipv6 += server_ips[IpAddress.IP_ADDRESS_IPV6] + "\n"
        text += ovh_ipv4
        text += ovh_ipv6
        text += "\n"

        text += "Dynamic exclusions and inclusions:\n"
        # Defined in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "https://b.rucss.wp-rocket.me\n"
        text += "46.30.212.116\n"
        text += "\n"

        text += "RocketCDN subscription:\n"
        text += "https://rocketcdn.me/api/\n"
        text += "185.10.9.100\n"
        text += self.get_groupone_live2_ips()

        return text

    def send_wp_rocket_ips_to_slack(self, app_context, slack_user):
        """
            List all IPs used for WP Rocket and sends it in a Slack DM
        """
        text = self.generate_wp_rocket_ips(app_context)
        self.slack_message_factory.post_message(app_context, slack_user, text)
