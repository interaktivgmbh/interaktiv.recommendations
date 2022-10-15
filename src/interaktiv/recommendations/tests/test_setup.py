import unittest

import plone.api as api
from interaktiv.recommendations.behaviors.recommendable import IRecommendableBehavior
from interaktiv.recommendations.interfaces import IInteraktivRecommendationsLayer
from interaktiv.recommendations.testing import INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING
from interaktiv.recommendations.tools.recommender import RecommenderTool
from plone.app.testing import IntegrationTesting, TEST_USER_ID, setRoles
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.browserlayer import utils
from Products.CMFPlone.controlpanel.browser.quickinstaller import InstallerView
# noinspection PyUnresolvedReferences
from Products.CMFPlone.utils import get_installer
from zope.component import getUtility


class TestSetup(unittest.TestCase):
    layer: IntegrationTesting = INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING
    installer: InstallerView = None
    product_name: str = 'interaktiv.recommendations'

    def setUp(self):
        super().setUp()

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        self.installer = get_installer(self.portal, self.request)

    def test_product_installed(self):
        # postcondition
        self.assertTrue(self.installer.is_product_installed(self.product_name))

    def test_interaktiv_recommendations_browserlayer_installed(self):
        # postcondition
        self.assertIn(IInteraktivRecommendationsLayer, utils.registered_layers())

    def test_recommender_tool_available(self):
        # postcondition
        self.assertIn('portal_recommender', self.portal)
        recommender = api.portal.get_tool('portal_recommender')
        self.assertIsInstance(recommender, RecommenderTool)

    def test_recommendation_matrix_index_added(self):
        # postcondition
        catalog = api.portal.get_tool('portal_catalog')
        self.assertIn('recommendation_matrix_index', catalog.Indexes)

    def test_recommendable_behavior_available(self):
        # postcondition
        recommendable_behavior = getUtility(IBehavior, name=IRecommendableBehavior.__identifier__)
        self.assertEqual(recommendable_behavior.interface, IRecommendableBehavior)
        self.assertTrue(IFormFieldProvider.providedBy(IRecommendableBehavior))

    def test_recommendations_settings_in_controlpanel_actions(self):
        # postcondition
        controlpanel = api.portal.get_tool('portal_controlpanel')
        controlpanel_action_ids = [action.id for action in controlpanel.listActions()]
        self.assertIn('recommendations_settings', controlpanel_action_ids)
