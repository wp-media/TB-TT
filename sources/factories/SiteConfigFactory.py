"""
    This module defines the factory for loading WP test site configuration and resolving their credentials.
"""
import json
from pathlib import Path
from decouple import config


class SiteConfigFactory():
    """
        Class managing access to the WP test sites configured for TB-TT's site monitoring.
    """
    def __init__(self):
        """
            The factory instanciates the objects it needed to complete the processing of the request.
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "wp-test-sites.json"
        with open(config_path, encoding='utf-8') as file_sites_config:
            self.sites_config = json.load(file_sites_config)

    def get_site(self, site_slug):
        """
            Returns the configuration of a WP test site, including its resolved application password,
            given its slug. Raises a KeyError if the site is unknown or its application password is not set.
        """
        if site_slug not in self.sites_config['sites']:
            raise KeyError(f'Unknown site: {site_slug}')

        site = dict(self.sites_config['sites'][site_slug])
        site['app_password'] = config(site['app_password_env'])
        return site
