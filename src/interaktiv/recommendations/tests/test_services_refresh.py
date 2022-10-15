import plone.api as api
from interaktiv.recommendations.restapi.refresh import RecommendationsRefresh
from interaktiv.recommendations.testing import INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING
from interaktiv.recommendations.tests.base_test import BaseTest
from interaktiv.recommendations.tools.recommender import RecommenderTool
from plone.app.contenttypes.content import Document
from plone.app.testing import FunctionalTesting


class TestRefreshService(BaseTest):
    layer: FunctionalTesting = INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING
    document: Document
    recommender: RecommenderTool
    service: RecommendationsRefresh

    def setUp(self):
        super().setUp()

        self._enable_recommendable_behavior(portal_type='Document')

        self.document = api.content.create(
            container=self.portal,
            type='Document',
            id='document_a'
        )

        self.recommender = api.portal.get_tool('portal_recommender')

        self.service = RecommendationsRefresh()
        self.service.context = self.document
        self.service.request = self.request

    def tearDown(self):
        if 'document_a' in self.portal:
            self.portal.manage_delObjects(['document_a'])

    def test_service_reply(self):
        # pre condition
        self.assertIsNone(self.recommender.vectorizer)
        self.assertIsNone(self.recommender.model_knn)

        # do it
        result = self.service.reply()

        # post condition
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), {'refreshed'})

        self.assertTrue(result['refreshed'])

        self.assertTrue(self.recommender.vectorizer)
        vocabulary = self.recommender.vectorizer.vocabulary_
        expected_vocabulary = {'document_a': 0}
        self.assertDictEqual(vocabulary, expected_vocabulary)

        self.assertTrue(self.recommender.model_knn)
        self.assertEqual(self.recommender.model_knn.n_samples_fit_, 1)
