import os
import time
import plone.api as api
from typing import NoReturn, List, TypedDict, Literal
from AccessControl.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import registerToolInterface
from Products.CMFPlone.CatalogTool import CatalogTool
from plone.dexterity.content import DexterityContent
from plone.indexer.interfaces import IIndexer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.i18nmessageid.message import Message
from zope.interface import Interface
from zope.interface import implementer
from interaktiv.recommendations.controlpanels.recommendations_settings import RecommendationsSettingsView
from interaktiv.recommendations.behaviors.recommendable import IRecommendableBehavior

BUILDOUT_DIR: str = os.environ.get('BUILDOUT_DIR', '')
INSTANCE_HOME: str = '/'.join(os.environ.get('INSTANCE_HOME', '').split('/')[:-2])
if BUILDOUT_DIR:
    RECOMMENDER_STORAGE_PATH: str = BUILDOUT_DIR + '/var/recommender.bin'
else:
    RECOMMENDER_STORAGE_PATH: str = INSTANCE_HOME + '/var/recommender.bin'


class TRecommendation(TypedDict):
    title: str
    id: str
    url: str
    index: int
    distance: float


class IRecommenderTool(Interface):
    """ IRecommenderTool.
    """


@implementer(IRecommenderTool)
class RecommenderTool(UniqueObject, SimpleItem):
    """ RecommenderTool.
    """

    id = 'portal_recommender'
    catalog: CatalogTool = None
    vectorizer: TfidfVectorizer = None
    model_knn: NearestNeighbors = None

    def __init__(self):
        self.setup()

    def setup(self):
        if not self.catalog:
            self.catalog = api.portal.get_tool('portal_catalog')

    @staticmethod
    def _add_status_message(msg: Message, _type: Literal['info', 'warn', 'error'] = 'info') -> NoReturn:
        api.portal.show_message(message=msg, request=getRequest(), type=_type)

    def get_documents(self) -> List[DexterityContent]:
        query = {
            'object_provides': IRecommendableBehavior.__identifier__
        }
        return [brain.getObject() for brain in self.catalog(query)]

    def get_text(self, obj: DexterityContent) -> str:
        indexer = queryMultiAdapter((obj, self.catalog), IIndexer, name='SearchableText')
        if not indexer:
            return str()

        text = indexer()
        return ' '.join([text.strip() for text in text.split()])

    def get_indexed_texts(self, document_objs: List[DexterityContent]) -> List[str]:
        texts = list()
        matrix_index = 0

        for document_obj in document_objs:
            text = self.get_text(document_obj)
            if not text:
                continue

            texts.append(text)
            document_obj.recommendation_matrix_index = matrix_index
            document_obj.reindexObject(idxs=['recommendation_matrix_index'])
            matrix_index += 1

        return texts

    def set_fitted_vectorizer(self, text_datas: List[str]) -> NoReturn:
        if not text_datas:
            msg = 'No Text Data Found. Consider Using RecommendableBehavior and reindexing object_provides Index.'
            self._add_status_message(msg, _type='error')
            return None

        tfidf = TfidfVectorizer(stop_words=None)
        tfidf.fit(text_datas)
        self.vectorizer = tfidf

    def set_fitted_knn_model(self, text_datas: List[str]) -> NoReturn:
        if not self.vectorizer:
            msg = 'Could not fit KNN-Model: Vectorizer not initialized.'
            self._add_status_message(msg, _type='error')
            return None

        model_knn = NearestNeighbors(metric='cosine', algorithm='auto', n_neighbors=1, n_jobs=-1)

        recommendation_matrix = self.vectorizer.transform(text_datas)
        model_knn.fit(recommendation_matrix)
        self.model_knn = model_knn

    def refresh(self) -> bool:
        start = time.time()

        documents = self.get_documents()
        texts = self.get_indexed_texts(documents)

        self.set_fitted_vectorizer(texts)
        self.set_fitted_knn_model(texts)

        end = time.time()

        if self.vectorizer and self.model_knn:
            time_passed = end - start
            msg = f'Recommender Successfully Refreshed in {time_passed} seconds.'
            self._add_status_message(msg, _type='info')
            return True
        else:
            msg = f'Failed Refreshing Recommender.'
            self._add_status_message(msg, _type='info')

        return False

    # TODO Split this into more Methods
    def get_recommendations(self, obj: DexterityContent, num: int = None, max_distance: float = 1.0
                            ) -> List[TRecommendation]:

        if not self.vectorizer:
            return list()

        if not self.model_knn:
            return list()

        if not num:
            num = RecommendationsSettingsView.get_setting('recommendation_max_elements')

        recommendations = list()

        text = self.get_text(obj)
        vectorized_texts = self.vectorizer.transform([text])

        # do not try to get more neighbors than fitted samples
        num_neighbors = num + 1
        if num_neighbors > self.model_knn.n_samples_fit_:
            num_neighbors = self.model_knn.n_samples_fit_

        distances, indexes = self.model_knn.kneighbors(vectorized_texts, n_neighbors=num_neighbors)

        nearest_indexes = list()
        index_to_distance = dict()
        for distance, index in zip(distances[0], indexes[0]):
            if distance > max_distance:
                continue
            if index == obj.recommendation_matrix_index:
                continue
            nearest_indexes.append(index)
            index_to_distance[index] = distance

        query = {
            'object_provides': IRecommendableBehavior.__identifier__,
            'recommendation_matrix_index': nearest_indexes
        }
        for brain in self.catalog(query):
            recommendations.append({
                'title': brain.Title,
                'id': brain.id,
                'url': brain.getURL(),
                'index': brain.recommendation_matrix_index,
                'distance': index_to_distance[brain.recommendation_matrix_index]
            })

        recommendations = sorted(recommendations, key=lambda x: x['distance'])

        return recommendations[:num]


InitializeClass(RecommenderTool)
registerToolInterface('portal_recommender', IRecommenderTool)
