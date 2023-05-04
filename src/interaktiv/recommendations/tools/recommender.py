import os
import time
from datetime import datetime
from typing import NoReturn, List, TypedDict, Literal, Union, Optional, Any

import plone.api as api
from AccessControl.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import registerToolInterface
from Products.CMFPlone.CatalogTool import CatalogTool
from interaktiv.recommendations.behaviors.recommendable import IRecommendableBehavior
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import DexterityContent
from plone.indexer.interfaces import IIndexer
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.interface import implementer

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
    vectorizer: Union[TfidfVectorizer, Pipeline] = None
    model_knn: NearestNeighbors = None

    def __init__(self):
        self.setup()

    def setup(self):
        if not self.catalog:
            self.catalog = api.portal.get_tool('portal_catalog')

    @staticmethod
    def get_setting(name: str) -> Optional[Union[str, Any]]:
        try:
            return api.portal.get_registry_record(name, interface=IRecommendationSettings)
        except InvalidParameterError:
            return None

    @staticmethod
    def _add_status_message(msg: str, _type: Literal['info', 'warn', 'error'] = 'info') -> NoReturn:
        api.portal.show_message(message=msg, request=getRequest(), type=_type)

    def get_documents(self) -> List[DexterityContent]:
        query = {
            'object_provides': IRecommendableBehavior.__identifier__
        }

        only_published = self.get_setting(name='recommendation_only_published')
        if only_published:
            query['review_state'] = 'published'

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

        use_svd = self.get_setting(name='recommendation_svd_usage')

        if use_svd:
            svd_dimensions = self.get_setting(name='recommendation_svd_dimensions')
            vectorizer = make_pipeline(
                TfidfVectorizer(stop_words=None),
                TruncatedSVD(n_components=svd_dimensions),
                Normalizer(copy=False)
            )
        else:
            vectorizer = TfidfVectorizer(stop_words=None)

        vectorizer.fit(text_datas)
        self.vectorizer = vectorizer

    def set_fitted_knn_model(self, text_datas: List[str]) -> NoReturn:
        if not self.vectorizer:
            msg = 'Could not fit KNN-Model: Vectorizer not initialized.'
            self._add_status_message(msg, _type='error')
            return None

        model_knn = NearestNeighbors(metric='cosine', algorithm='auto', n_neighbors=1, n_jobs=-1)

        recommendation_matrix = self.vectorizer.transform(text_datas)
        model_knn.fit(recommendation_matrix)
        self.model_knn = model_knn

    @staticmethod
    def set_last_refresh() -> NoReturn:
        today = datetime.now()
        api.portal.set_registry_record('last_refresh', interface=IRecommendationSettings, value=today)

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
            self._add_status_message(msg)
            self.set_last_refresh()
            return True

        msg = f'Failed Refreshing Recommender.'
        self._add_status_message(msg)
        return False

    # TODO Split this into more Methods
    def get_recommendations(
            self,
            obj: DexterityContent,
            num: int = None,
            max_distance: float = 1.0
    ) -> List[TRecommendation]:

        if not self.vectorizer or not self.model_knn:
            return list()

        if not num:
            num = self.get_setting('recommendation_max_elements')

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

    def get_last_refresh(self) -> str:
        last_refresh = self.get_setting('last_refresh')
        if not last_refresh:
            return str()

        portal = api.portal.get()
        return portal.toLocalizedTime(last_refresh)

    def get_recommender_info(self):
        data = {
            'error': ''
        }

        if not self.vectorizer:
            data['error'] = 'Vectorizer not initialized'
        else:
            data['dimensions'] = self.model_knn.n_features_in_
            data['vectors'] = self.model_knn.n_samples_fit_

        data['last_refresh'] = self.get_last_refresh()

        return data


InitializeClass(RecommenderTool)
registerToolInterface('portal_recommender', IRecommenderTool)
