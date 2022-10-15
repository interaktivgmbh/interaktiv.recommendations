import json
from typing import Union, Optional, NoReturn, Dict, Any

import plone.api as api
import zope.schema as schema
from interaktiv.recommendations.behaviors.recommendable import IRecommendableBehavior
from interaktiv.recommendations.interfaces import IInteraktivRecommendationsLayer
from interaktiv.recommendations.utilities.datasets import get_datasets_utility
from plone.api.exc import InvalidParameterError
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.controlpanels import RegistryConfigletPanel
from Products.CMFPlone.Portal import PloneSite
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapter
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.schema import SourceText
from ZPublisher.HTTPRequest import HTTPRequest


class RecommendationsSettingsView(BrowserView):
    template: ViewPageTemplateFile = ViewPageTemplateFile('templates/recommendations_settings.pt')
    info = dict()

    def __init__(self, context: PloneSite, request: HTTPRequest) -> NoReturn:
        super(RecommendationsSettingsView, self).__init__(context, request)
        alsoProvides(request, IDisableCSRFProtection)
        self.messages = IStatusMessage(self.request)

    def __call__(self) -> str:
        self.info = dict()
        form = self.request.form

        if 'refresh' in self.request.form:
            self.refresh()

        if 'import_20newsgroups' in self.request.form:
            self.import_20newsgroups_dataset()

        if 'submit' in form:
            form_data = self.request.form.copy()
            self.set_settings(form_data)

        return self.template(self)

    @staticmethod
    def refresh() -> NoReturn:
        recommender = api.portal.get_tool('portal_recommender')
        catalog = api.portal.get_tool('portal_catalog')

        catalog.manage_reindexIndex(ids=['object_provides'])
        recommender.refresh()

    @staticmethod
    def import_20newsgroups_dataset() -> NoReturn:
        datasets_utility = get_datasets_utility()
        datasets_utility.import_20newsgroups_dataset()

    @staticmethod
    def get_info() -> Dict[str, Dict[Any, Dict[str, int]]]:
        catalog = api.portal.get_tool('portal_catalog')

        query = {
            'object_provides': IRecommendableBehavior.__identifier__
        }

        brains = catalog(query)

        count = dict()

        for brain in brains:
            if brain.portal_type not in count:
                count[brain.portal_type] = {
                    'count_all': 0,
                    'count_new': 0
                }

            count[brain.portal_type]['count_all'] += 1
            if brain.recommendation_matrix_index != 0 and not brain.recommendation_matrix_index:
                count[brain.portal_type]['count_new'] += 1

        return {
            'count': count
        }

    @staticmethod
    def set_settings(form_data: Dict[str, str]) -> NoReturn:
        max_elements = form_data.get('recommendation_max_elements', 3)
        debug_mode = form_data.get('recommendation_debug_mode', False)

        if debug_mode == 'on':
            debug_mode = True

        api.portal.set_registry_record(
            name='recommendation_max_elements',
            value=int(max_elements),
            interface=IRecommendationSettings
        )

        api.portal.set_registry_record(
            name='recommendation_debug_mode',
            value=debug_mode,
            interface=IRecommendationSettings
        )

    @staticmethod
    def get_setting(name: str) -> Optional[Union[str, Any]]:
        try:
            return api.portal.get_registry_record(name, interface=IRecommendationSettings)
        except InvalidParameterError:
            return None


# backend/eggs/collective.volto.subfooter-1.1.0-py3.8-linux-x86_64.egg/collective/volto/subfooter/interfaces.py
class IRecommendationSettings(Interface):
    """ Empty Schema ? need field for custom volto widget component """

    recommendation_configuration = SourceText(
        title='Recommendation Configuration',
        description='',
        required=False,
        default=json.dumps([{'somekey': 'somevalue'}]),
    )

    recommendation_max_elements = schema.Int(
        title='Recommendations Item Count',
        description='Number of recommendations displayed in the viewlet.',
        required=False,
        default=3
    )

    recommendation_debug_mode = schema.Bool(
        title='Recommendations Debug Mode',
        description='Debug mode to show more details in the recommendations viewlet and tile.',
        required=False,
        default=False
    )


@adapter(Interface, IInteraktivRecommendationsLayer)
class RecommendationsControlpanel(RegistryConfigletPanel):
    schema = IRecommendationSettings
    schema_prefix = None
    configlet_id = "recommendations_settings"  # needs to be equal to action_id in controlpanel.xml configlet
    configlet_category_id = "Products"
    title = "Recommendation Settings"
    group = "Products"
