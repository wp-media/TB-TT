"""
    Unit tests for the SiteConfigFactory.py main file
"""
import pytest

from sources.factories.SiteConfigFactory import SiteConfigFactory


def test_get_site_known_site(monkeypatch):
    """
    Tests get_site returns the site config with its resolved application password
    """
    monkeypatch.setenv('TBTT_SITE_ONE_COM_APP_PASSWORD', 'resolved-password')

    factory = SiteConfigFactory()
    site = factory.get_site('one-com')

    assert site['label'] == 'one.com'
    assert site['app_password'] == 'resolved-password'


def test_get_site_unknown_site():
    """
    Tests get_site raises a KeyError for an unknown site slug
    """
    factory = SiteConfigFactory()

    with pytest.raises(KeyError):
        factory.get_site('does-not-exist')
