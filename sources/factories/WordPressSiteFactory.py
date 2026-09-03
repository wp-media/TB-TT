"""
    This module defines the factory to interact with a WP test site: health checks and pending-update state.
"""
import time
import requests


class WordPressSiteFactory():
    """
        Class managing HTTP interactions with a single WP test site.
    """
    def __init__(self):
        """
            The factory instanciates the objects it needed to complete the processing of the request.
        """
        self.timeout = 10

    def __check_url(self, url, auth=None):
        """
            Performs a GET request against 'url' and returns a result dict describing whether it succeeded.
            'status' is one of 'ok' or 'fail'.
        """
        start_time = time.time()
        try:
            response = requests.get(url, auth=auth, timeout=self.timeout)
        except requests.exceptions.RequestException as error:
            return {'url': url, 'status': 'fail', 'detail': f'Request failed: {error}'}

        duration_ms = round((time.time() - start_time) * 1000)
        if response.status_code != 200:
            return {'url': url, 'status': 'fail', 'detail': f'Status code {response.status_code}'}
        return {'url': url, 'status': 'ok', 'detail': f'{duration_ms}ms'}

    def check_health(self, site):
        """
            Checks homepage (cached and cache-busted), login page, REST API root, and authenticated
            wp-admin access (via the REST API) of a WP test site.
            Returns a dict of check name -> result dict (see __check_url); 'status' is 'ok' or 'fail'.
        """
        base_url = site['url'].rstrip('/')
        cache_bust_param = int(time.time())
        auth = (site['app_user'], site['app_password'])

        return {
            'homepage (cached)': self.__check_url(base_url + '/'),
            'homepage (uncached)': self.__check_url(f'{base_url}/?nowprocket&tbtt_cache_bust={cache_bust_param}'),
            'login page': self.__check_url(base_url + '/wp-login.php'),
            'REST API': self.__check_url(base_url + '/wp-json/'),
            'wp-admin (authenticated)': self.__check_url(base_url + '/wp-json/wp/v2/users/me', auth=auth),
        }

    def check_updates_pending(self, site):
        """
            Calls the TB-TT Site Monitor plugin's REST route to check for pending core/plugin/theme updates.
            Returns a result dict; 'status' is 'fail' if the call itself failed, 'warning' if the call
            succeeded but updates are pending (not yet applied by WordPress's own auto-updates, which is
            expected from time to time and not itself an emergency), or 'ok' if nothing is pending.
        """
        base_url = site['url'].rstrip('/')
        url = base_url + '/wp-json/tbtt-monitor/v1/updates-pending'
        auth = (site['app_user'], site['app_password'])

        try:
            response = requests.get(url, auth=auth, timeout=self.timeout)
        except requests.exceptions.RequestException as error:
            return {'url': url, 'status': 'fail', 'detail': f'Request failed: {error}'}

        if response.status_code != 200:
            return {'url': url, 'status': 'fail', 'detail': f'Status code {response.status_code}'}

        payload = response.json()
        pending_parts = []
        if payload.get('plugins_pending'):
            pending_parts.append(f"{payload['plugins_pending']} plugin(s)")
        if payload.get('themes_pending'):
            pending_parts.append(f"{payload['themes_pending']} theme(s)")
        if payload.get('core_pending'):
            pending_parts.append(f"core ({payload.get('core_response_type')})")

        if pending_parts:
            return {'url': url, 'status': 'warning', 'detail': 'Pending updates: ' + ', '.join(pending_parts)}
        return {'url': url, 'status': 'ok', 'detail': 'No pending updates'}
