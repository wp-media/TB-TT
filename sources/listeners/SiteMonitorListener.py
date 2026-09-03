"""
    This module defines the endpoint handler (called listener) for the WP test site monitoring endpoint.
"""
from threading import Thread
from flask import request, current_app
from sources.handlers.SiteMonitorHandler import SiteMonitorHandler
from sources.utils import Security
import sources.utils.Constants as cst


class SiteMonitorListener():
    """
        Class to define the WP test site monitoring endpoint listener. It is callable and called when the right
        url is used. It is subject to API key authentication, meant to be called by an internal k8s CronJob.
    """

    def __init__(self):
        """
            The listener instanciates the handlers it will pass the request to so that it is processed.
        """
        self.site_monitor_handler = SiteMonitorHandler()

    def check_site(self, site_slug):
        """
            Method called to process a request on the registered endpoint.
            It is subject to API key authentication.
            It validates the site is known, then starts a dedicated thread to run the health and
            pending-updates checks for 'site_slug' and post the summary to Slack, and returns immediately.
            The Slack message is the source of truth for the result, not the HTTP response.
        """
        expected_api_key = current_app.config[cst.APP_CONFIG_TOKEN_API_KEY]
        security_check = Security.validate_api_key(request, expected_api_key)
        if not security_check:
            return 'Wrong or missing API key.', 401

        try:
            self.site_monitor_handler.validate_site(site_slug)
        except KeyError as error:
            return str(error), 404

        current_app.logger.info("check_site: Starting processing thread for site '%s'...", site_slug)
        thread = Thread(
            target=self.site_monitor_handler.run_check, kwargs={
                "app_context": current_app.app_context(), "site_slug": site_slug})
        thread.start()
        return {}, 202
