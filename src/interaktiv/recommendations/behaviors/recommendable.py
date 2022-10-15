import zope.schema as schema

from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import provider, implementer


@provider(IFormFieldProvider)
class IRecommendableBehavior(model.Schema):

    directives.mode(recommendation_matrix_index='hidden')
    recommendation_matrix_index = schema.Int(
        title='Recommendation-Matrix Index',
        description='',
        required=False
    )


@implementer(IRecommendableBehavior)
@adapter(IDexterityContent)
class RecommendableBehavior(object):

    def __init__(self, context):
        self.context = context
