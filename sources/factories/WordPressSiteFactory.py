"""
    This module defines the factory to interact with a WP test site: health checks and pending-update state.
"""
import time
import requests

# Hosts running bot protection (e.g. WP Engine's firewall) reject the default 'python-requests/x.y.z'
# User-Agent outright, which made every check fail with a 403 that looked like a site outage. A
# descriptive User-Agent identifies the monitor and is accepted by the monitored hosts. Note it must
# NOT impersonate a browser either: some hosts' bot protection rejects browser-like User-Agents from
# server-side clients, so an honest, descriptive one is the only thing that satisfies both.
USER_AGENT = 'TB-TT-Site-Monitor/1.0 (+https://github.com/wp-media/TB-TT)'

# Connect timeout is kept short (a host that does not accept a connection quickly is down), while the
# read timeout is generous: a cache-busted homepage on a slow host legitimately takes several seconds,
# and a tighter budget reported false failures.
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 30


class WordPressSiteFactory():
    """
        Class managing HTTP interactions with a single WP test site.
    """
    def __init__(self):
        """
            The factory instanciates the objects it needed to complete the processing of the request.
        """
        self.timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)
        self.headers = {'User-Agent': USER_AGENT}

    def __failure_detail(self, response):
        """
            Builds the 'detail' of a failed check, adding the hints needed to tell apart the failure
            modes that a bare status code makes indistinguishable: a 404 served by the web server
            rather than by WordPress, a redirect to somewhere unexpected, and an authentication
            problem caused by missing credentials.
        """
        hints = []

        server = response.headers.get('Server')
        if server:
            hints.append(f'server: {server}')

        # An HTML 404 without WordPress's own markup means the web server answered before WordPress did,
        # which points at rewrite rules (.htaccess / mod_rewrite) rather than at a missing route.
        content_type = response.headers.get('Content-Type', '')
        if 'html' in content_type and 'wp-' not in response.text[:2048].lower():
            hints.append('response did not come from WordPress')

        if response.status_code in (401, 403):
            hints.append('check the application password and the host bot protection')

        if response.history:
            hints.append(f'redirected to {response.url}')

        detail = f'Status code {response.status_code}'
        if hints:
            detail += ' (' + '; '.join(hints) + ')'
        return detail

    def __check_url(self, url, auth=None):
        """
            Performs a GET request against 'url' and returns a result dict describing whether it succeeded.
            'status' is one of 'ok' or 'fail'.
        """
        start_time = time.time()
        try:
            response = requests.get(url, auth=auth, timeout=self.timeout, headers=self.headers)
        except requests.exceptions.RequestException as error:
            return {'url': url, 'status': 'fail', 'detail': f'Request failed: {error}'}

        duration_ms = round((time.time() - start_time) * 1000)
        if response.status_code != 200:
            return {'url': url, 'status': 'fail', 'detail': self.__failure_detail(response)}
        return {'url': url, 'status': 'ok', 'detail': f'{duration_ms}ms'}

    def check_health(self, site):
        """
            Checks homepage (cached and cache-busted), login page, REST API root, and authenticated
            wp-admin access (via the REST API) of a WP test site.
            Returns a dict of check name -> result dict (see __check_url); 'status' is 'ok' or 'fail'.
            When the homepage itself is unreachable the site is down or blocking the monitor, so the
            remaining checks are skipped: they would all fail for the same reason and reporting six
            identical failures hides which one is the actual problem.
        """
        base_url = site['url'].rstrip('/')
        cache_bust_param = int(time.time())
        auth = (site['app_user'], site['app_password'])

        homepage_result = self.__check_url(base_url + '/')
        if homepage_result['status'] == 'fail':
            return {
                'homepage (cached)': homepage_result,
                'other checks': {
                    'url': base_url,
                    'status': 'fail',
                    'detail': 'Skipped: the homepage is unreachable, so every other check would fail too',
                },
            }

        return {
            'homepage (cached)': homepage_result,
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
            response = requests.get(url, auth=auth, timeout=self.timeout, headers=self.headers)
        except requests.exceptions.RequestException as error:
            return {'url': url, 'status': 'fail', 'detail': f'Request failed: {error}'}

        if response.status_code != 200:
            return {'url': url, 'status': 'fail', 'detail': self.__failure_detail(response)}

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
