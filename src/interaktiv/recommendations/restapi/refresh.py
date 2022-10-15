from typing import TypedDict

from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class TRecommendationRefreshReply(TypedDict):
    refreshed: bool


@implementer(IPublishTraverse)
class RecommendationsRefresh(Service):

    def reply(self) -> TRecommendationRefreshReply:
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        recommender = api.portal.get_tool('portal_recommender')
        result = recommender.refresh()

        return {'refreshed': result}
