import unittest

import plone.api as api
from Products.CMFPlone.controlpanel.browser.quickinstaller import InstallerView
# noinspection PyUnresolvedReferences
from Products.CMFPlone.utils import get_installer
from interaktiv.recommendations.behaviors.recommendable import IRecommendableBehavior
from interaktiv.recommendations.interfaces import IInteraktivRecommendationsLayer
from interaktiv.recommendations.testing import INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING
from plone.api.exc import InvalidParameterError
from plone.app.testing import IntegrationTesting, TEST_USER_ID, setRoles
from plone.browserlayer import utils
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility


class TestReinstall(unittest.TestCase):
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

    def tearDown(self):
        super().tearDown()
        self._install_interaktiv_recommendations()

    def _install_interaktiv_recommendations(self):
        if not self.installer.is_product_installed(self.product_name):
            self.installer.install_product(self.product_name)

    def test_uninstall__interaktiv_recommendations_product(self):
        # setup
        dependencies = []
        products = [self.product_name] + dependencies
        for product in products:
            self.assertTrue(
                self.installer.is_product_installed(product),
                'Product should have been installed: {}'.format(product)
            )

        # do it
        self.installer.uninstall_product(self.product_name)

        # postcondition
        for product in products:
            self.assertFalse(
                self.installer.is_product_installed(product),
                'Product should have been uninstalled: {}'.format(product)
            )

    def test_interaktiv_recommendations_browserlayer_removed(self):
        # do it
        self.installer.uninstall_product(self.product_name)

        # postcondition
        self.assertNotIn(IInteraktivRecommendationsLayer, utils.registered_layers())

    def test_uninstall__recommender_tool_removed(self):
        # do it
        self.installer.uninstall_product(self.product_name)

        # postcondition
        self.assertNotIn('portal_recommender', self.portal)
        with self.assertRaises(InvalidParameterError):
            api.portal.get_tool('portal_recommender')

    def test_uninstall__recommendation_matrix_index_removed(self):
        # do it
        self.installer.uninstall_product(self.product_name)

        # postcondition
        catalog = api.portal.get_tool('portal_catalog')
        self.assertNotIn('recommendation_matrix_index', catalog.Indexes)

    def test_recommendable_behavior_removed_from_contenttype(self):
        # setup
        fti = queryUtility(IDexterityFTI, name='Document')
        behaviors = list(fti.behaviors)
        behaviors.append(IRecommendableBehavior.__identifier__)
        fti.behaviors = tuple(behaviors)

        # do it
        self.installer.uninstall_product(self.product_name)

        # postcondition
        fti = queryUtility(IDexterityFTI, name='Document')
        behaviors = list(fti.behaviors)
        self.assertNotIn(IRecommendableBehavior.__identifier__, behaviors)

    def test_recommendations_settings_not_in_controlpanel_actions(self):
        # do it
        self.installer.uninstall_product(self.product_name)

        # postcondition
        controlpanel = api.portal.get_tool('portal_controlpanel')
        controlpanel_action_ids = [action.id for action in controlpanel.listActions()]
        self.assertNotIn('recommendations_settings', controlpanel_action_ids)
