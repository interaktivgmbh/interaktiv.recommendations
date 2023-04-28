from typing import Optional, NoReturn

from Products.GenericSetup.tool import SetupTool
from interaktiv.recommendations import _
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from plone.registry import Record
from plone.registry import field as registry_field
from plone.registry.field import Datetime
from plone.registry.interfaces import IRegistry
from plone.registry.registry import Registry
from zope.component import getUtility


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> NoReturn:

    field_class = getattr(registry_field, 'Datetime', None)
    last_refresh: Datetime = field_class(
        title=_('trans_recommendations_last_refresh'),
        description='',
        required=False
    )

    registry: Registry = getUtility(IRegistry)
    registry.records[f'{IRecommendationSettings.__identifier__}.last_refresh'] = Record(last_refresh)
