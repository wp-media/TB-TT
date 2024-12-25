"""
    This module defines the handler for logic related to listing server IPs.
"""
import requests
from sources.factories.SlackMessageFactory import SlackMessageFactory
from sources.factories.OvhApiFactory import OvhApiFactory
from sources.utils import IpAddress, Duplication


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

    def get_cloudflare_proxy_ipv4(self):
        """
            Retrieves the list of IPv4 used by CloudFlare and returns it as a string, one IP per line.
            If an error occurs, it is returned.
        """
        return self.get_cloudflare_proxy_ips('v4')

    def get_cloudflare_proxy_ipv6(self):
        """
            Retrieves the list of IPv6 used by CloudFlare and returns it as a string, one IP per line.
            If an error occurs, it is returned.
        """
        return self.get_cloudflare_proxy_ips('v6')

    def get_cloudflare_proxy_ips(self, ip_version):
        """
            Retrieves the list of IP matching ip_version used by CloudFlare and returns it as a string, one IP per line.
            If an error occurs, it is returned.
        """
        url = 'https://www.cloudflare.com/ips-' + ip_version + '/'
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as error:
            return f"Error: Unable to reach CloudFlare. Error: {error}"
        if response.status_code == 200:
            ip_list = response.text.strip().split('\n')
            return '\n'.join(ip_list) + '\n'
        return f"Error: Unable to fetch CloudFlare IPs. Status code: {response.status_code}"

    def get_groupone_ipv4(self):
        """
            Lists all IP ranges used by group.One
        """
        groupone_ips = ''
        # Provided by group.One Ops based on
        # https://gitlab.group.one/systems/group.one-authdns/-/blob/main/ipam/internet.yaml?ref_type=heads
        # Contact group.One ops for more details
        groupone_ips += "185.10.8.0/22\n"
        groupone_ips += "46.30.210.0/24\n"
        groupone_ips += "46.30.211.0/24\n"
        groupone_ips += "46.30.212.0/24\n"
        groupone_ips += "46.30.214.0/24\n"
        groupone_ips += "5.249.224.0/24\n"
        return groupone_ips

    def generate_wp_rocket_ips_human_readable(self, app_context):
        """
            Generates a text list of all IPs used by WP Rocket, human readable
        """
        text = "List of IPs used for WP Rocket:\n\n"

        text += "License validation/activation, update check, plugin information:\n"
        # Defined in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "https://wp-rocket.me\n"
        text += self.get_cloudflare_proxy_ipv4()
        text += self.get_cloudflare_proxy_ipv6()
        text += "\n"

        text += "Load CSS Asynchronously:\n"
        # Defined in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "https://cpcss.wp-rocket.me\n"
        text += self.get_groupone_ipv4()
        text += "\n"

        text += "Remove Unused CSS:\n"
        # SaaS CNAME in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += self.get_groupone_ipv4()
        # OVH servers
        all_server_list = self.ovh_api_factory.get_dedicated_servers(app_context)
        ovh_ipv4 = ''
        ovh_ipv6 = ''
        for server_name in all_server_list:
            display_name = self.ovh_api_factory.get_dedicated_server_display_name(app_context, server_name)
            if 'worker' in display_name or 'mirror' in display_name:
                server_ips = self.ovh_api_factory.get_dedicated_server_ips(app_context, server_name)
                if server_ips is None:
                    continue
                ovh_ipv4 += server_ips[IpAddress.IP_ADDRESS_IPV4] + "\n"
                ovh_ipv6 += server_ips[IpAddress.IP_ADDRESS_IPV6] + "\n"
        text += ovh_ipv4
        text += ovh_ipv6
        # SaaS User Agents
        text += "User Agents:\n"
        # pylint: disable-next=line-too-long
        text += "WP-Rocket/SaaS Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36\n" # noqa
        # pylint: disable-next=line-too-long
        text += "WP-Rocket/SaaS Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36\n" # noqa
        text += "\n"

        text += "Dynamic exclusions and inclusions:\n"
        # Defined in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += "https://b.rucss.wp-rocket.me\n"
        text += self.get_groupone_ipv4()
        text += "\n"

        text += "RocketCDN subscription:\n"
        text += "https://rocketcdn.me/api/\n"
        text += self.get_groupone_ipv4()

        return text

    def generate_wp_rocket_ipv4_machine_readable(self, app_context):
        """
            List all IPv4 used for WP Rocket, machine readable with one IP per line and no text
        """
        text = ""
        # CloudFlare proxy
        text += self.get_cloudflare_proxy_ipv4()
        # group.One
        text += self.get_groupone_ipv4()
        # OVH servers
        all_server_list = self.ovh_api_factory.get_dedicated_servers(app_context)
        ovh_ipv4 = ''
        for server_name in all_server_list:
            display_name = self.ovh_api_factory.get_dedicated_server_display_name(app_context, server_name)
            if 'worker' in display_name or 'mirror' in display_name:
                server_ips = self.ovh_api_factory.get_dedicated_server_ips(app_context, server_name)
                if server_ips is None:
                    continue
                ovh_ipv4 += server_ips[IpAddress.IP_ADDRESS_IPV4] + "\n"
        text += ovh_ipv4
        deduplicated_text = Duplication.remove_duplicated_lines(text)
        return deduplicated_text

    def generate_wp_rocket_ipv6_machine_readable(self, app_context):
        """
            List all IPv6 used for WP Rocket, machine readable with one IP per line and no text
        """
        text = ""
        # CloudFlare proxy
        text += self.get_cloudflare_proxy_ipv6()
        # group.One
        # OVH servers
        all_server_list = self.ovh_api_factory.get_dedicated_servers(app_context)
        ovh_ipv6 = ''
        for server_name in all_server_list:
            display_name = self.ovh_api_factory.get_dedicated_server_display_name(app_context, server_name)
            if 'worker' in display_name or 'mirror' in display_name:
                server_ips = self.ovh_api_factory.get_dedicated_server_ips(app_context, server_name)
                if server_ips is None:
                    continue
                ovh_ipv6 += server_ips[IpAddress.IP_ADDRESS_IPV6] + "\n"
        text += ovh_ipv6
        deduplicated_text = Duplication.remove_duplicated_lines(text)
        return deduplicated_text

    def send_wp_rocket_ips_to_slack(self, app_context, slack_user):
        """
            List all IPs used for WP Rocket and sends it in a Slack DM
        """
        text = self.generate_wp_rocket_ips_human_readable(app_context)
        self.slack_message_factory.post_message(app_context, slack_user, text)
