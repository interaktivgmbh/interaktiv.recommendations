import plone.api as api
from plone.dexterity.interfaces import IDexterityFTI
# noinspection PyUnresolvedReferences
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import queryUtility
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'interaktiv.recommendations:uninstall',
        ]


# noinspection PyUnusedLocal
def pre_install(context):
    """Pre install script"""


# noinspection PyUnusedLocal
def post_install(context):
    """Post install script"""


# noinspection PyUnusedLocal
def uninstall(context):
    """Uninstall script"""

    # remove IRecommendableBehavior
    recommendable_behavior = 'interaktiv.recommendations.behaviors.recommendable.IRecommendableBehavior'
    types_tool = api.portal.get_tool('portal_types')
    portal_types = types_tool.listContentTypes()

    for portal_type in portal_types:
        fti = queryUtility(IDexterityFTI, name=portal_type)

        if fti and recommendable_behavior in fti.behaviors:
            fti.behaviors = tuple([behavior for behavior in fti.behaviors if behavior != recommendable_behavior])

    # Keep this list in sync with 'metadata.xml'
    uninstall_products = []
    uninstall_products = list(set(uninstall_products) - {'interaktiv.recommendations'})
