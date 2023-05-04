from typing import List

import plone.api as api
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.statusmessages.interfaces import IStatusMessage
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from interaktiv.recommendations.testing import INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING
from interaktiv.recommendations.tests.base_test import BaseTest
from interaktiv.recommendations.tools.recommender import RecommenderTool, TRecommendation
from numpy import matrix, ndarray
from plone.app.contenttypes.content import Document
from plone.app.testing import FunctionalTesting
from plone.app.textfield.value import RichTextValue
from scipy.sparse.csr import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from datetime import datetime


class TestRecommenderTool(BaseTest):
    layer: FunctionalTesting = INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING
    recommender: RecommenderTool = None

    def setUp(self):
        super().setUp()

        self._enable_recommendable_behavior(portal_type='Document')

        self.recommender = api.portal.get_tool('portal_recommender')
        self.recommender.vectorizer = None
        self.recommender.model_knn = None

    def _create_test_documents(self):
        return [
            api.content.create(
                container=self.portal,
                type='Document',
                id='house'
            ),
            api.content.create(
                container=self.portal,
                type='Document',
                id='mouse'
            )
        ]

    def _remove_test_documents(self):
        self.portal.manage_delObjects(['house', 'mouse'])

    def test_recommender_tool_setup(self):
        # setup
        self.recommender.catalog = None
        self.assertIsNone(self.recommender.catalog)

        # do it
        self.recommender.setup()

        # postcondition
        self.assertIsInstance(self.recommender.catalog, CatalogTool)

    def test_recommender__add_status_message(self):
        # do it
        self.recommender._add_status_message(msg='test status message', _type='error')

        # postcondition
        messages_obj = IStatusMessage(self.request)
        messages = messages_obj.show()

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'test status message')
        self.assertEqual(messages[0].type, 'error')

    def test_recommender_get_documents(self):
        # setup
        api.content.create(
            container=self.portal,
            type='Document',
            id='document-a'
        )
        api.content.create(
            container=self.portal,
            type='Folder',
            id='folder-a'
        )

        # do it
        result = self.recommender.get_documents()

        # postcondition
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Document)
        self.assertEqual(result[0].id, 'document-a')

        # cleanup
        self.portal.manage_delObjects(['document-a', 'folder-a'])

    def test_recommender_get_documents_only_published(self):
        # setup
        document_a = api.content.create(
            container=self.portal,
            type='Document',
            id='document-a'
        )
        api.content.create(
            container=self.portal,
            type='Document',
            id='document-b'
        )
        api.portal.set_registry_record('recommendation_only_published', interface=IRecommendationSettings, value=True)

        # precondition
        self.assertFalse(self.recommender.get_documents())

        # do it
        api.content.transition(document_a, transition='publish')
        result = self.recommender.get_documents()

        # postcondition
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Document)
        self.assertEqual(result[0].id, 'document-a')

        # cleanup
        self.portal.manage_delObjects(['document-a', 'document-b'])
        api.portal.set_registry_record('recommendation_only_published', interface=IRecommendationSettings, value=False)

    def test_recommender_get_text(self):
        # setup
        document = api.content.create(
            container=self.portal,
            type='Document',
            id='document-a',
            title='Title',
            description='Description',
            text=RichTextValue('<p><a href="test">Text</a></p>')
        )

        # do it
        result = self.recommender.get_text(document)

        # postcondition
        self.assertEqual(result, 'document-a Title Description Text')

    def test_recommender_get_indexed_texts(self):
        # setup
        documents = self._create_test_documents()

        # do it
        result = self.recommender.get_indexed_texts(documents)

        # postcondition
        expected_result = [
            'house',
            'mouse',
        ]
        self.assertListEqual(result, expected_result)

        self.assertEqual(self.portal['house'].recommendation_matrix_index, 0)
        self.assertEqual(api.content.find(recommendation_matrix_index=0)[0].id, 'house')
        self.assertEqual(self.portal['mouse'].recommendation_matrix_index, 1)
        self.assertEqual(api.content.find(recommendation_matrix_index=1)[0].id, 'mouse')

        # cleanup
        self._remove_test_documents()

    def test_recommender_set_fitted_vectorizer__no_texts(self):
        # do it
        self.recommender.set_fitted_vectorizer(text_datas=list())

        # postcondition
        self.assertIsNone(self.recommender.vectorizer)

        messages_obj = IStatusMessage(self.request)
        messages = messages_obj.show()

        self.assertEqual(len(messages), 1)
        self.assertIn('No Text Data Found.', messages[0].message)
        self.assertEqual(messages[0].type, 'error')

    def test_recommender_set_fitted_vectorizer__texts(self):
        # setup
        text_datas = [
            'House',
            'Mouse'
        ]

        # do it
        self.recommender.set_fitted_vectorizer(text_datas=text_datas)

        # postcondition
        self.assertIsInstance(self.recommender.vectorizer, TfidfVectorizer)

        vocabulary = self.recommender.vectorizer.vocabulary_
        expected_vocabulary = {'house': 0, 'mouse': 1}
        self.assertDictEqual(vocabulary, expected_vocabulary)

        transformed_texts = self.recommender.vectorizer.transform(['house', 'mouse', 'unknown'])
        self.assertIsInstance(transformed_texts, csr_matrix)
        transformed_texts_dense = transformed_texts.todense()
        self.assertIsInstance(transformed_texts_dense, matrix)
        self.assertEqual(transformed_texts_dense.shape, (3, 2))

        # 'house' vector
        self.assertEqual(transformed_texts_dense[0].tolist()[0], [1.0, 0.0])
        # 'mouse' vector
        self.assertEqual(transformed_texts_dense[1].tolist()[0], [0.0, 1.0])
        # 'unknown' vector
        self.assertEqual(transformed_texts_dense[2].tolist()[0], [0.0, 0.0])

    def test_recommender_set_fitted_knn_model__no_vectorizer(self):
        # do it
        self.recommender.set_fitted_knn_model(text_datas=list())

        # postcondition
        self.assertIsNone(self.recommender.model_knn)

        messages_obj = IStatusMessage(self.request)
        messages = messages_obj.show()

        self.assertEqual(len(messages), 1)
        self.assertIn('Vectorizer not initialized.', messages[0].message)
        self.assertEqual(messages[0].type, 'error')

    def test_recommender_set_fitted_knn_model__with_vectorizer(self):
        # setup
        text_datas = [
            'House',
            'Mouse'
        ]
        self.recommender.set_fitted_vectorizer(text_datas=text_datas)

        # do it
        self.recommender.set_fitted_knn_model(text_datas=text_datas)

        # postcondition
        self.assertIsInstance(self.recommender.model_knn, NearestNeighbors)

        self.assertEqual(self.recommender.model_knn.metric, 'cosine')
        self.assertEqual(self.recommender.model_knn.n_features_in_, 2)

        # 'house' vector = [1, 0]
        distances, indexes = self.recommender.model_knn.kneighbors([[1, 0]], n_neighbors=2)
        self.assertIsInstance(distances, ndarray)
        self.assertEqual(distances.shape, (1, 2))
        self.assertIsInstance(indexes, ndarray)
        self.assertEqual(indexes.shape, (1, 2))

        # distance 'house' to 'house'
        self.assertEqual(distances[0][0], 0.0)
        self.assertEqual(text_datas[indexes[0][0]], 'House')

        # distance 'house' to 'mouse'
        self.assertEqual(distances[0][1], 1.0)
        self.assertEqual(text_datas[indexes[0][1]], 'Mouse')

    def test_recommender_refresh__no_documents(self):
        # do it
        self.recommender.refresh()

        # postcondition
        messages_obj = IStatusMessage(self.request)
        messages = messages_obj.show()

        self.assertEqual(len(messages), 3)
        self.assertIn('No Text Data Found', messages[0].message)
        self.assertIn('Vectorizer not initialized', messages[1].message)
        self.assertIn('Failed Refreshing Recommender', messages[2].message)

        self.assertIsNone(self.recommender.vectorizer)
        self.assertIsNone(self.recommender.model_knn)

    def test_recommender_refresh__with_documents(self):
        # setup
        self._create_test_documents()

        # do it
        self.recommender.refresh()

        # postcondition
        messages_obj = IStatusMessage(self.request)
        messages = messages_obj.show()

        self.assertEqual(len(messages), 1)
        self.assertIn('Recommender Successfully Refreshed', messages[0].message)

        self.assertTrue(self.recommender.vectorizer)
        vocabulary = self.recommender.vectorizer.vocabulary_
        expected_vocabulary = {'house': 0, 'mouse': 1}
        self.assertDictEqual(vocabulary, expected_vocabulary)

        self.assertTrue(self.recommender.model_knn)
        self.assertEqual(self.recommender.model_knn.n_features_in_, 2)

        # cleanup
        self._remove_test_documents()

    def test_recommender_refresh__updates_last_refresh(self):
        # setup
        self._create_test_documents()

        old_date = datetime(2011, 11, 11)
        api.portal.set_registry_record('last_refresh', interface=IRecommendationSettings, value=old_date)

        # do it
        self.recommender.refresh()

        # post condition
        last_refresh = api.portal.get_registry_record('last_refresh', interface=IRecommendationSettings)
        self.assertIsInstance(last_refresh, datetime)
        today = datetime.now()
        self.assertEqual(last_refresh.date(), today.date())

    def test_recommender_get_recommendations__not_refreshed_no_documents(self):
        # setup
        unknown_document = api.content.create(
            container=self.portal,
            type='Document',
            id='unknown-document',
            title='Mouse House'
        )

        # do it
        results = self.recommender.get_recommendations(unknown_document)

        # postcondition
        self.assertListEqual(results, list())

        # cleanup
        self.portal.manage_delObjects(['unknown-document'])

    def test_recommender_get_recommendations__refreshed_no_documents(self):
        # setup
        self.recommender.refresh()

        unknown_document = api.content.create(
            container=self.portal,
            type='Document',
            id='unknown-document',
            title='Mouse House'
        )

        # do it
        results = self.recommender.get_recommendations(unknown_document)

        # postcondition
        self.assertListEqual(results, list())

        # cleanup
        self.portal.manage_delObjects(['unknown-document'])

    def test_recommender_get_recommendations__refreshed_with_documents(self):
        # setup
        documents = self._create_test_documents()
        self.recommender.refresh()

        unknown_document = api.content.create(
            container=self.portal,
            type='Document',
            id='unknown-document',
            title='Mouse House'
        )

        # do it
        results: List[TRecommendation] = self.recommender.get_recommendations(unknown_document)

        # postcondition
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        self.assertEqual(results[0]['id'], documents[0].id)
        self.assertEqual(results[0]['url'], documents[0].absolute_url())
        self.assertEqual(results[0]['index'], 0)

        self.assertEqual(results[1]['id'], documents[1].id)
        self.assertEqual(results[1]['url'], documents[1].absolute_url())
        self.assertEqual(results[1]['index'], 1)

        # cleanup
        self.portal.manage_delObjects(['unknown-document'])
        self._remove_test_documents()
