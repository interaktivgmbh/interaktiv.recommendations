from typing import Optional

import plone.api as api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets.common import ViewletBase


class RecommendationsViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/recommendations.pt')

    def get_recommendations(self):
        recommender = api.portal.get_tool('portal_recommender')

        return recommender.get_recommendations(obj=self.context)

    @staticmethod
    def debug_mode() -> Optional[bool]:
        try:
            return api.portal.get_registry_record('recommendation_debug_mode', interface=IRecommendationSettings)

        except InvalidParameterError:
            return None
