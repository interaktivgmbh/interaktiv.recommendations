import plone.api as api
from typing import Optional
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.api.exc import InvalidParameterError
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings


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
