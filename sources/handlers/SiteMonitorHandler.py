"""
    This module defines the handler for logic related to monitoring WP test sites (health and pending updates).
"""
from sources.factories.SiteConfigFactory import SiteConfigFactory
from sources.factories.WordPressSiteFactory import WordPressSiteFactory
from sources.factories.SlackMessageFactory import SlackMessageFactory


class SiteMonitorHandler():
    """
        Class managing the business logic related to monitoring WP test sites.

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.site_config_factory = SiteConfigFactory()
        self.wordpress_site_factory = WordPressSiteFactory()
        self.slack_message_factory = SlackMessageFactory()

    __STATUS_EMOJI = {
        'ok': ':white_check_mark:',
        'warning': ':warning:',
        'fail': ':x:',
    }

    def __overall_status(self, results):
        """
            Returns the worst status ('fail' > 'warning' > 'ok') across all check results.
        """
        statuses = {result['status'] for result in results.values()}
        if 'fail' in statuses:
            return 'fail'
        if 'warning' in statuses:
            return 'warning'
        return 'ok'

    def __build_slack_blocks(self, site, results):
        """
            Builds Slack Block Kit blocks summarizing the check results for a site.
        """
        overall_status = self.__overall_status(results)
        header_emoji = self.__STATUS_EMOJI[overall_status]

        blocks = [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"{header_emoji} *{site['label']}* ({site['url']})",
                },
            },
        ]

        lines = []
        for check_name, result in results.items():
            check_emoji = self.__STATUS_EMOJI[result['status']]
            lines.append(f"{check_emoji} {check_name}: {result['detail']}")

        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '\n'.join(lines),
            },
        })

        return blocks

    def validate_site(self, site_slug):
        """
            Raises a KeyError if 'site_slug' is not a known configured site.
        """
        self.site_config_factory.get_site(site_slug)

    def run_check(self, app_context, site_slug):
        """
            Runs the health checks and pending-updates check for the given site, then posts a
            combined summary to the auto-e2e-reports Slack channel. Returns the results dict.
            Meant to be run in a dedicated thread (see SiteMonitorListener), so errors are logged
            rather than raised.
        """
        app_context.push()
        try:
            site = self.site_config_factory.get_site(site_slug)

            results = self.wordpress_site_factory.check_health(site)
            results['pending updates'] = self.wordpress_site_factory.check_updates_pending(site)

            overall_status = self.__overall_status(results)
            status_text = {
                'ok': 'all checks passed',
                'warning': 'all checks passed, with warning(s)',
                'fail': 'one or more checks failed',
            }[overall_status]
            text = f"{site['label']} site check: {status_text}"
            blocks = self.__build_slack_blocks(site, results)

            channel = self.slack_message_factory.get_channel('auto-e2e-reports')
            self.slack_message_factory.post_message(app_context, channel, text, blocks)

            return results
        # pylint: disable-next=broad-exception-caught
        except Exception as error:
            app_context.app.logger.error("run_check: Error while checking site '%s': %s", site_slug, error)
            return None
