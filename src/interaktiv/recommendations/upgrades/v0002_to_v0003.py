from typing import Optional, NoReturn

import plone.api as api
from Products.GenericSetup.tool import SetupTool


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> NoReturn:
    setup = api.portal.get_tool('portal_setup')

    # import registry.xml
    setup.runImportStepFromProfile(
        profile_id='interaktiv.recommendations:default',
        step_id='plone.app.registry'
    )
