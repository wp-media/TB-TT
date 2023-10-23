"""
    Utility functions to handle IP Addresses.
"""
from ipaddress import ip_address, IPv4Address

IP_ADDRESS_IPV4 = "IPv4"
IP_ADDRESS_IPV6 = "IPv6"


def validIPAddress(IP: str) -> str:
    """
        Checks the IP address provided to identify if it is IPv4 or IPv6 or invalid.
    """
    try:
        return IP_ADDRESS_IPV4 if type(ip_address(IP)) is IPv4Address else IP_ADDRESS_IPV6
    except ValueError:
        return "Invalid"
