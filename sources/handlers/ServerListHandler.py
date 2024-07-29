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

    def get_groupone_live1_ipv4(self):
        """
            Lists all IP used by live1 cluster from group.One
        """
        live1_ips = ''
        # Defined in k8s_live1_sips & k8s_live1_ingress:
        # https://gitlab.one.com/systems/chef-repo/-/blob/master/roles/onecom-global-firewall-macros.json#L173
        live1_ips += "46.30.212.67\n46.30.212.92\n"
        return live1_ips

    def get_groupone_live2_ipv4(self):
        """
            Lists all IP used by live2 cluster from group.One
        """
        live2_ips = ''
        # Defined in k8s_live2_sips:
        # https://gitlab.one.com/systems/chef-repo/-/blob/master/roles/onecom-global-firewall-macros.json#L173
        live2_ips += "46.30.212.68\n46.30.212.70\n46.30.212.71\n46.30.212.72\n46.30.212.73\n"
        # Defined in k8s_live2_ingress:
        live2_ips += "46.30.212.116\n"
        return live2_ips

    def get_groupone_k8spod1_ipv4(self):
        """
            Lists all IP used by k8spod1 cluster from group.One
        """
        k8spod1_ips = ''
        # Defined in k8spod1_sips & k8spod1_ingress:
        # https://gitlab.one.com/systems/chef-repo/-/blob/master/roles/onecom-global-firewall-macros.json#L173
        k8spod1_ips += "46.30.211.168\n46.30.212.120\n46.30.212.76\n46.30.212.77\n46.30.212.78\n46.30.212.79\n"
        return k8spod1_ips

    def get_groupone_cpcss_ipv4(self):
        """
            Lists all IPv4 used specifically by CPCSS service from group.One
        """
        ipv4 = ''
        ipv4 += "46.30.212.116\n"
        return ipv4

    def get_groupone_saas_ipv4(self):
        """
            Lists all IPv4 used specifically by WP Rocket SaaS service from group.One
        """
        ipv4 = ''
        ipv4 += "46.30.212.116\n"
        return ipv4

    def get_groupone_backend_ipv4(self):
        """
            Lists all IPv4 used specifically by backend service from group.One
        """
        ipv4 = ''
        ipv4 += "46.30.212.116\n"
        return ipv4

    def get_groupone_proxy_ipv4(self):
        """
            Lists all IPv4 used for the wpmedia pod proxies
        """
        ipv4 = ''
        ipv4 += "185.10.9.100\n"
        ipv4 += "185.10.9.101\n"
        ipv4 += "185.10.9.102\n"
        ipv4 += "185.10.9.103\n"
        return ipv4

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
        text += self.get_groupone_live2_ipv4()
        text += "\n"

        text += "Remove Unused CSS:\n"
        # SaaS CNAME in https://gitlab.one.com/systems/group.one-authdns/-/blob/main/octodns/wp-rocket.me.yaml?ref_type=heads
        text += self.get_groupone_live2_ipv4()
        text += self.get_groupone_live1_ipv4()
        text += self.get_groupone_k8spod1_ipv4()
        # OVH servers
        all_server_list = self.ovh_api_factory.get_dedicated_servers(app_context)
        ovh_ipv4 = ''
        ovh_ipv6 = ''
        for server_name in all_server_list:
            display_name = self.ovh_api_factory.get_dedicated_server_display_name(app_context, server_name)
            if 'worker' in display_name:
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
        text += self.get_groupone_backend_ipv4()
        text += "\n"

        text += "RocketCDN subscription:\n"
        text += "https://rocketcdn.me/api/\n"
        text += self.get_groupone_proxy_ipv4()
        text += self.get_groupone_live2_ipv4()

        return text

    def generate_wp_rocket_ipv4_machine_readable(self, app_context):
        """
            List all IPv4 used for WP Rocket, machine readable with one IP per line and no text
        """
        text = ""
        # CloudFlare proxy
        text += self.get_cloudflare_proxy_ipv4()
        # group.One
        text += self.get_groupone_proxy_ipv4()
        text += self.get_groupone_live2_ipv4()
        text += self.get_groupone_live1_ipv4()
        text += self.get_groupone_k8spod1_ipv4()
        # OVH servers
        all_server_list = self.ovh_api_factory.get_dedicated_servers(app_context)
        ovh_ipv4 = ''
        for server_name in all_server_list:
            display_name = self.ovh_api_factory.get_dedicated_server_display_name(app_context, server_name)
            if 'worker' in display_name:
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
            if 'worker' in display_name:
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
