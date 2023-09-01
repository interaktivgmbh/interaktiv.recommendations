import json
from typing import NoReturn

import plone.api as api
import zope.schema as schema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interaktiv.recommendations import _
from interaktiv.recommendations.interfaces import IInteraktivRecommendationsLayer
from interaktiv.recommendations.utilities.datasets import get_datasets_utility
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.supermodel.directives import fieldset
from plone.z3cform import layout
from z3c.form import button
from zope.component import adapter
from zope.interface import Interface
from zope.schema import SourceText


class IRecommendationSettings(Interface):

    fieldset('info',
             label=_('trans_recommendations_tab_info', default='Info'),
             fields=['dummy_info']
             )

    fieldset('advanced',
             label=_('trans_recommendations_tab_advanced_settings', default='Advanced Settings'),
             fields=[
                 'recommendation_debug_mode',
                 'recommendation_svd_usage',
                 'recommendation_svd_dimensions'
             ]
             )

    fieldset('import',
             label=_('trans_recommendations_tab_import', default='Import Testdata'),
             fields=['dummy_import_testdata']
             )

    directives.widget(dummy_refresh='interaktiv.recommendations.controlpanels.widgets.RefreshFieldWidget')
    dummy_refresh = SourceText(
        title='Refresh',
        description='',
        required=False,
        default=json.dumps([{'somekey': 'somevalue'}]),
    )

    recommendation_only_published = schema.Bool(
        title=_('trans_recommendations_only_published', default='Recommend only Published Content'),
        description=_(
            'trans_recommendations_only_published_desc',
            default='Only Recommend Content that have the review_state "published".'
        ),
        required=False,
        default=True
    )

    recommendation_max_elements = schema.Int(
        title=_('trans_recommendation_max_elements', default='Recommendations Item Count'),
        description=_(
            'trans_recommendations_max_elements_desc',
            default='Number of recommendations displayed in the viewlet.'
        ),
        required=False,
        default=3
    )

    directives.widget(dummy_info='interaktiv.recommendations.controlpanels.widgets.InfoFieldWidget')
    dummy_info = SourceText(
        title='Info',
        description='',
        required=False,
        default=json.dumps([{'somekey': 'somevalue'}]),
    )

    recommendation_debug_mode = schema.Bool(
        title=_('trans_recommendations_debug_mode', default='Recommendations Debug Mode'),
        description=_(
            'trans_recommendations_debug_mode_desc',
            default='Debug mode to show more details in the recommendations viewlet and tile.'
        ),
        required=False,
        default=False
    )

    recommendation_svd_usage = schema.Bool(
        title=_('trans_recommendations_svd_usage', default='Use Truncated SVD for Dimensionality Reduction'),
        description=_(
            'trans_recommendations_svd_usage_desc',
            default='Use Truncated SingularValueDecomposition for Dimensionality Reduction.'
        ),
        required=False,
        default=False
    )

    recommendation_svd_dimensions = schema.Int(
        title=_('trans_recommendations_svd_dimensions', default='Number of Truncated SVD Dimensions'),
        description=_(
            'trans_recommendations_svd_dimensions_desc',
            default='Set the number of Dimensions returned by SVD Truncation.'
        ),
        required=False,
        default=200
    )

    directives.widget(
        dummy_import_testdata='interaktiv.recommendations.controlpanels.widgets.TestDataImportFieldWidget')
    dummy_import_testdata = SourceText(
        title='Import TestData',
        description='',
        required=False,
        default=json.dumps([{'somekey': 'somevalue'}]),
    )

    directives.mode(last_refresh='hidden')
    last_refresh = schema.Datetime(
        title=_('trans_recommendations_last_refresh', default='Last Refresh Date'),
        description='',
        required=False
    )


class RecommendationsSettingsForm(RegistryEditForm):
    schema = IRecommendationSettings
    label = _('trans_recommendations_settings', default='Interaktiv Recommendations Settings')
    description = _('trans_recommendations_settings_desc', default='Settings to configure Recommendations')

    # noinspection PyUnreachableCode
    @staticmethod
    def import_20newsgroups_dataset() -> NoReturn:
        datasets_utility = get_datasets_utility()
        datasets_utility.import_20newsgroups_dataset()

    @staticmethod
    def refresh() -> NoReturn:
        recommender = api.portal.get_tool('portal_recommender')
        catalog = api.portal.get_tool('portal_catalog')

        catalog.manage_reindexIndex(ids=['object_provides'])
        recommender.refresh()

    # noinspection PyUnusedLocal,PyPep8Naming
    @button.buttonAndHandler(_('label_import'), name='import')
    def handleImport(self, action):
        self.import_20newsgroups_dataset()

    # noinspection PyUnusedLocal,PyPep8Naming
    @button.buttonAndHandler(_('label_refresh'), name='refresh')
    def handleRefresh(self, action):
        self.refresh()

    @button.buttonAndHandler(_('trans_recommendations_button_save'), name='save')
    def handleSave(self, action):
        super().handleSave(self, action)

    @button.buttonAndHandler(_('trans_recommendations_button_cancel'), name='cancel')
    def handleCancel(self, action):
        super().handleCancel(self, action)


class RecommendationsControlPanelFormWrapper(ControlPanelFormWrapper):
    """ ovverride default ControlPanelForm template """

    index = ViewPageTemplateFile('templates/recommendations_controlpanel_layout.pt')


RecommendationsSettingsView = layout.wrap_form(RecommendationsSettingsForm, RecommendationsControlPanelFormWrapper)


@adapter(Interface, IInteraktivRecommendationsLayer)
class RecommendationsControlpanel(RegistryConfigletPanel):
    schema = IRecommendationSettings
    schema_prefix = None
    configlet_id = "recommendations_settings"  # needs to be equal to action_id in controlpanel.xml configlet
    configlet_category_id = "Products"
    title = "Recommendation Settings"
    group = "Products"
