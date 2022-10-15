import unittest

from interaktiv.recommendations.behaviors.recommendable import IRecommendableBehavior
from plone.app.testing import TEST_USER_ID, setRoles
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility


class BaseTest(unittest.TestCase):

    # noinspection PyUnresolvedReferences
    def setUp(self):
        super().setUp()

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Site Administrator'])

    @staticmethod
    def _enable_recommendable_behavior(portal_type):
        fti = queryUtility(IDexterityFTI, name=portal_type)
        behaviors = list(fti.behaviors)
        if IRecommendableBehavior.__identifier__ not in behaviors:
            behaviors.append(IRecommendableBehavior.__identifier__)
            fti.behaviors = tuple(behaviors)
