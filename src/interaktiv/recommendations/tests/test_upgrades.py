import unittest

# noinspection PyUnresolvedReferences
from Products.CMFPlone.utils import get_installer
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from interaktiv.recommendations.testing import INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING
from interaktiv.recommendations.upgrades import v0001_to_v0002
from plone.app.testing import IntegrationTesting, TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry
from plone.registry.registry import Registry
from zope.component import getUtility


class TestUpgrades(unittest.TestCase):
    layer: IntegrationTesting = INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING

    def setUp(self):
        super().setUp()

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Site Administrator'])

    def test_upgrade__v0001_to_v0002(self):
        # setup
        record = f'{IRecommendationSettings.__identifier__}.last_refresh'
        registry: Registry = getUtility(IRegistry)

        del registry.records[record]

        # precondition
        self.assertNotIn(record, registry)

        # do it
        v0001_to_v0002.upgrade()

        # postcondition
        self.assertIn(record, registry)
