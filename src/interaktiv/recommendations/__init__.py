import logging

from zope.i18nmessageid import MessageFactory
from Products.CMFCore.utils import ToolInit

logger = logging.getLogger('interaktiv.recommendations')
_ = MessageFactory("interaktiv.recommendations")


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope product."""

    from interaktiv.recommendations.tools.recommender import RecommenderTool
    tools = (RecommenderTool ,)
    ToolInit('InteraktivRecommendations', tools=tools, icon='tool.gif').initialize(context)
