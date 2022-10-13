from typing import TypedDict, List

from plone import api
from plone.api.exc import InvalidParameterError
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from interaktiv.recommendations.tools.recommender import TRecommendation
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class TRecommendationGetReply(TypedDict):
    recommendations: List[TRecommendation]
    debug: bool


@implementer(IPublishTraverse)
class RecommendationsGet(Service):

    @staticmethod
    def _is_debug_mode() -> bool:
        try:
            return api.portal.get_registry_record('recommendation_debug_mode', interface=IRecommendationSettings)
        except InvalidParameterError:
            return False

    def reply(self) -> TRecommendationGetReply:
        data = json_body(self.request)
        num = data.get('num')

        recommender = api.portal.get_tool('portal_recommender')
        return {
            'recommendations': recommender.get_recommendations(obj=self.context, num=num),
            'debug': self._is_debug_mode()
        }
