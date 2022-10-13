import importlib
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.protect import auto as protect_auto
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


INTERAKTIV_RECOMMENDATIONS_FIXTURE = InteraktivRecommendationsLayer()
INTERAKTIV_RECOMMENDATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(INTERAKTIV_RECOMMENDATIONS_FIXTURE,),
    name="InteraktivRecommendationsLayer:Integration"
)
INTERAKTIV_RECOMMENDATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(INTERAKTIV_RECOMMENDATIONS_FIXTURE, WSGI_SERVER_FIXTURE),
    name="InteraktivRecommendationsLayer:Functional"
)
