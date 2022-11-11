import importlib

import plone.api as api
from Products.CMFCore.WorkflowTool import WorkflowTool
from interaktiv.recommendations.controlpanels.recommendations_settings import IRecommendationSettings
from plone.app.testing import FunctionalTesting, IntegrationTesting, PloneSandboxLayer, applyProfile
from plone.protect import auto as protect_auto
# noinspection PyUnresolvedReferences
from plone.testing.zope import WSGI_SERVER_FIXTURE
from zope.configuration import xmlconfig


class InteraktivRecommendationsLayer(PloneSandboxLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'plone.restapi',
            'interaktiv.recommendations',
        ]
        self.product_to_install = 'interaktiv.recommendations'

    def setUpZope(self, app, configuration_context):
        for product_name in self.products_to_import:
            module = importlib.import_module(product_name)
            xmlconfig.file(
                'configure.zcml',
                module,
                context=configuration_context
            )

    def setUpPloneSite(self, portal):
        applyProfile(portal, self.product_to_install + ':default')

        # Disable CSRF system-wide
        protect_auto.CSRF_DISABLED = True

        portal_workflow: WorkflowTool = api.portal.get_tool('portal_workflow')
        portal_workflow.setChainForPortalTypes(['Document'], 'simple_publication_workflow')

        # set default value for recommendation_only_published to False
        api.portal.set_registry_record('recommendation_only_published', interface=IRecommendationSettings, value=False)


INTERAKTIV_RECOMMENDATIONS_FIXTURE = InteraktivRecommendationsLayer()
INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(INTERAKTIV_RECOMMENDATIONS_FIXTURE,),
    name="InteraktivRecommendationsLayer:Integration"
)
INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(INTERAKTIV_RECOMMENDATIONS_FIXTURE, WSGI_SERVER_FIXTURE),
    name="InteraktivRecommendationsLayer:Functional"
)
