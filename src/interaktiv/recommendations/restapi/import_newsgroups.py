from typing import TypedDict

from interaktiv.recommendations.utilities.datasets import get_datasets_utility
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class TRecommendationImportNewsgroupsReply(TypedDict):
    imported: bool


@implementer(IPublishTraverse)
class ImportNewsgroups(Service):

    def reply(self) -> TRecommendationImportNewsgroupsReply:
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        datasets_utility = get_datasets_utility()
        result = datasets_utility.import_20newsgroups_dataset(document_type='block')

        return {'imported': result}
