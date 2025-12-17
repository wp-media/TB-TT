"""
    Unit tests for the ServerListHandler.py main file
"""

from unittest.mock import Mock, patch

import requests

from sources.handlers.ServerListHandler import ServerListHandler

# pylint: disable=unused-argument


def mock_cloudflare_ipv4_response(*args, **kwargs):
    """
    Mocks the requests.get response for CloudFlare IPv4
    """

    class RequestReturn:
        """
        Mocks the return of requests.get
        """

        status_code = 200
        text = "173.245.48.0/20\n103.21.244.0/22\n103.22.200.0/22"

    return RequestReturn()


def mock_cloudflare_ipv6_response(*args, **kwargs):
    """
    Mocks the requests.get response for CloudFlare IPv6
    """

    class RequestReturn:
        """
        Mocks the return of requests.get
        """

        status_code = 200
        text = "2400:cb00::/32\n2606:4700::/32\n2803:f800::/32"

    return RequestReturn()


def mock_cloudflare_error_response(*args, **kwargs):
    """
    Mocks the requests.get response for CloudFlare with error status
    """

    class RequestReturn:
        """
        Mocks the return of requests.get with error
        """

        status_code = 404

    return RequestReturn()


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_ipv4_response,
)
def test_get_cloudflare_proxy_ipv4(mock_requests):
    """
    Tests the get_cloudflare_proxy_ipv4 method returns CloudFlare IPv4 addresses
    """
    handler = ServerListHandler()
    result = handler.get_cloudflare_proxy_ipv4()

    assert result == "173.245.48.0/20\n103.21.244.0/22\n103.22.200.0/22\n"
    mock_requests.assert_called_once()
    assert mock_requests.call_args[0][0] == "https://www.cloudflare.com/ips-v4/"


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_ipv6_response,
)
def test_get_cloudflare_proxy_ipv6(mock_requests):
    """
    Tests the get_cloudflare_proxy_ipv6 method returns CloudFlare IPv6 addresses
    """
    handler = ServerListHandler()
    result = handler.get_cloudflare_proxy_ipv6()

    assert result == "2400:cb00::/32\n2606:4700::/32\n2803:f800::/32\n"
    mock_requests.assert_called_once()
    assert mock_requests.call_args[0][0] == "https://www.cloudflare.com/ips-v6/"


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_error_response,
)
def test_get_cloudflare_proxy_ips_error(mock_requests):
    """
    Tests the get_cloudflare_proxy_ips method handles error status codes
    """
    handler = ServerListHandler()
    result = handler.get_cloudflare_proxy_ips("v4")

    assert "Error: Unable to fetch CloudFlare IPs. Status code: 404" in result
    mock_requests.assert_called_once()


@patch("sources.handlers.ServerListHandler.requests.get")
def test_get_cloudflare_proxy_ips_exception(mock_requests):
    """
    Tests the get_cloudflare_proxy_ips method handles request exceptions
    """
    mock_requests.side_effect = requests.exceptions.RequestException(
        "Connection timeout"
    )
    handler = ServerListHandler()
    result = handler.get_cloudflare_proxy_ips("v4")

    assert "Error: Unable to reach CloudFlare" in result


def test_get_groupone_ipv4():
    """
    Tests the get_groupone_ipv4 method returns the correct list of IPs
    """
    handler = ServerListHandler()
    result = handler.get_groupone_ipv4()

    # Verify it returns a string with newline-separated IPs
    assert isinstance(result, str)
    assert "\n" in result

    # Verify specific IPs are in the list
    expected_ips = [
        "46.30.211.168",
        "46.30.212.76",
        "46.30.212.77",
        "46.30.212.78",
        "46.30.212.79",
        "46.30.211.69",
        "46.30.212.200",
        "46.30.212.201",
        "46.30.212.202",
        "46.30.212.203",
        "46.30.211.203",
        "46.30.212.204",
        "46.30.212.205",
        "46.30.212.206",
        "46.30.212.207",
        "46.30.211.236",
        "5.249.224.8",
        "5.249.224.9",
        "5.249.224.10",
        "5.249.224.11",
    ]

    result_lines = [line for line in result.split("\n") if line]  # Filter out empty strings
    for ip in expected_ips:  # pylint: disable=invalid-name
        assert ip in result_lines, f"Expected IP {ip} not found in result"

    # Verify the count matches
    assert len(result_lines) == len(expected_ips)


def test_get_groupone_ipv4_format():
    """
    Tests that get_groupone_ipv4 returns IPs in the correct format (one per line)
    """
    handler = ServerListHandler()
    result = handler.get_groupone_ipv4()

    # Verify each line contains a valid IP format
    for line in result.split("\n"):
        if line:  # Skip empty lines
            # Check basic IP format (X.X.X.X)
            parts = line.split(".")
            assert len(parts) == 4, f"Invalid IP format: {line}"
            for part in parts:
                assert part.isdigit(), f"Invalid IP part: {part}"
                assert 0 <= int(part) <= 255, f"Invalid IP octet: {part}"


def test_get_groupone_ipv6():
    """
    Tests the get_groupone_ipv6 method returns the correct IPv6 range
    """
    handler = ServerListHandler()
    result = handler.get_groupone_ipv6()

    assert "2a02:2350:4:200::/55" in result
    assert result.endswith("\n")


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_ipv4_response,
)
def test_generate_wp_rocket_ips_human_readable(mock_requests):
    """
    Tests the generate_wp_rocket_ips_human_readable method includes all sections
    """
    handler = ServerListHandler()
    result = handler.generate_wp_rocket_ips_human_readable()

    # Verify it includes main sections
    assert "List of IPs used for WP Rocket:" in result
    assert "License validation/activation" in result
    assert "https://wp-rocket.me" in result
    assert "Load CSS Asynchronously:" in result
    assert "https://cpcss.wp-rocket.me" in result
    assert "Remove Unused CSS:" in result
    assert "User Agents:" in result
    assert "WP-Rocket/SaaS" in result
    assert "Dynamic exclusions and inclusions:" in result
    assert "https://b.rucss.wp-rocket.me" in result
    assert "RocketCDN subscription:" in result
    assert "https://rocketcdn.me/api/" in result

    # Verify it includes group.one IPs
    assert "46.30.211.168" in result
    assert "5.249.224.11" in result


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_ipv4_response,
)
@patch("sources.utils.Duplication.remove_duplicated_lines")
def test_generate_wp_rocket_ipv4_machine_readable(mock_dedup, mock_requests):
    """
    Tests the generate_wp_rocket_ipv4_machine_readable method
    """
    mock_dedup.return_value = "173.245.48.0/20\n46.30.211.168\n"

    handler = ServerListHandler()
    result = handler.generate_wp_rocket_ipv4_machine_readable()

    # Verify deduplication was called
    mock_dedup.assert_called_once()

    # Verify the result is machine-readable (no text headers)
    assert "List of IPs" not in result
    assert "CloudFlare" not in result


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_ipv6_response,
)
@patch("sources.utils.Duplication.remove_duplicated_lines")
def test_generate_wp_rocket_ipv6_machine_readable(mock_dedup, mock_requests):
    """
    Tests the generate_wp_rocket_ipv6_machine_readable method
    """
    mock_dedup.return_value = "2400:cb00::/32\n2a02:2350:4:200::/55\n"

    handler = ServerListHandler()
    result = handler.generate_wp_rocket_ipv6_machine_readable()

    # Verify deduplication was called
    mock_dedup.assert_called_once()

    # Verify the result is machine-readable (no text headers)
    assert "List of IPs" not in result
    assert "CloudFlare" not in result


@patch(
    "sources.handlers.ServerListHandler.requests.get",
    side_effect=mock_cloudflare_ipv4_response,
)
def test_send_wp_rocket_ips_to_slack(mock_requests):
    """
    Tests the send_wp_rocket_ips_to_slack method calls post_message
    """
    handler = ServerListHandler()
    mock_app_context = Mock()
    mock_slack_user = "U123456"

    # Mock the post_message method
    handler.slack_message_factory.post_message = Mock()

    handler.send_wp_rocket_ips_to_slack(mock_app_context, mock_slack_user)

    # Verify post_message was called
    handler.slack_message_factory.post_message.assert_called_once()
    call_args = handler.slack_message_factory.post_message.call_args[0]

    assert call_args[0] == mock_app_context
    assert call_args[1] == mock_slack_user
    assert "List of IPs used for WP Rocket:" in call_args[2]


def test_get_groupone_ipv4_no_ranges():
    """
    Tests that get_groupone_ipv4 returns individual IPs, not CIDR ranges
    """
    handler = ServerListHandler()
    result = handler.get_groupone_ipv4()

    # Verify no CIDR notation is present (no /XX patterns)
    assert "/" not in result, "Result should not contain CIDR notation (e.g., /22, /24)"

    # Verify all lines are individual IPs
    for line in result.split("\n"):
        if line:
            assert "/" not in line, f"Line should not contain CIDR notation: {line}"
