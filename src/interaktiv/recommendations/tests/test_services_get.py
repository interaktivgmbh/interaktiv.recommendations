import plone.api as api
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from interaktiv.recommendations.restapi.get import RecommendationsGet
from interaktiv.recommendations.testing import INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING
from interaktiv.recommendations.tests.base_test import BaseTest
from interaktiv.recommendations.tools.recommender import RecommenderTool
from plone.app.contenttypes.content import Document
from plone.app.testing import FunctionalTesting


class TestRecommendationsGetService(BaseTest):
    layer: FunctionalTesting = INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING
    document: Document
    recommender: RecommenderTool
    service: RecommendationsGet

    def setUp(self):
        super().setUp()

        self._enable_recommendable_behavior(portal_type='Document')

        self.document = api.content.create(
            container=self.portal,
            type='Document',
            id='document_a',
            title='Document a'
        )

        self.recommender = api.portal.get_tool('portal_recommender')

        self.service = RecommendationsGet()
        self.service.context = self.document
        self.service.request = self.request

    def tearDown(self):
        api.portal.set_registry_record('recommendation_debug_mode', interface=IRecommendationSettings, value=False)

        if 'document_a' in self.portal:
            self.portal.manage_delObjects(['document_a'])

    def test_service__is_debug_mode__false(self):
        # do it
        result = self.service._is_debug_mode()

        # post condition
        self.assertFalse(result)

    def test_service__is_debug_mode__true(self):
        # setup
        api.portal.set_registry_record('recommendation_debug_mode', interface=IRecommendationSettings, value=True)

        # do it
        result = self.service._is_debug_mode()

        # post condition
        self.assertTrue(result)

    def test_service_reply__no_recommendations(self):
        # do it
        result = self.service.reply()

        # post condition
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), {'recommendations', 'debug'})

        self.assertFalse(result['debug'])
        self.assertListEqual(result['recommendations'], list())

    def test_service_reply__recommendations(self):
        # setup
        other_document = api.content.create(
            container=self.portal,
            type='Document',
            id='document_b'
        )

        self.recommender.refresh()

        # do it
        result = self.service.reply()

        # post condition
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), {'recommendations', 'debug'})

        self.assertFalse(result['debug'])
        self.assertIsInstance(result['recommendations'], list)
        self.assertEqual(len(result['recommendations']), 1)

        expected_recommendation = {
            'title': '',
            'id': 'document_b',
            'url': other_document.absolute_url(),
            'index': 1,
            'distance': 1.0
        }
        self.assertDictEqual(result['recommendations'][0], expected_recommendation)

        # cleanup
        self.portal.manage_delObjects([other_document.id])
