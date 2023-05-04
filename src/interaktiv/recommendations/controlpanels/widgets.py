import plone.api as api
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField


class ITestDataImportWidget(IWidget):
    """ TestData Import Widget to Render Import Form """


@implementer_only(ITestDataImportWidget)
class TestDataImportWidget(Widget):
    """ TestData Import Widget to Render Import Form """

    error = None
    value = None

    def update(self):
        pass

    @staticmethod
    def get_portal_url():
        return api.portal.get().absolute_url()


# noinspection PyPep8Naming
@implementer(IFieldWidget)
@adapter(IField, IFormLayer)
def TestDataImportFieldWidget(field, request):
    return FieldWidget(field, TestDataImportWidget(request))


class IRefreshWidget(IWidget):
    """ Refresh Widget to Render Refresh Form """


@implementer_only(IRefreshWidget)
class RefreshWidget(Widget):
    """ Refresh Widget to Render Refresh Form """

    error = None
    value = None

    def update(self):
        pass

    @staticmethod
    def get_portal_url():
        return api.portal.get().absolute_url()


# noinspection PyPep8Naming
@implementer(IFieldWidget)
@adapter(IField, IFormLayer)
def RefreshFieldWidget(field, request):
    return FieldWidget(field, RefreshWidget(request))


class IInfoWidget(IWidget):
    """ Info Widget to Render Recommender Information """


@implementer_only(IInfoWidget)
class InfoWidget(Widget):
    """ Info Widget to Render Recommender Information """

    error = None
    value = None

    def update(self):
        pass

    @staticmethod
    def get_portal_url():
        return api.portal.get().absolute_url()

    @staticmethod
    def get_recommender_info():
        recommender = api.portal.get_tool('portal_recommender')
        return recommender.get_recommender_info()


# noinspection PyPep8Naming
@implementer(IFieldWidget)
@adapter(IField, IFormLayer)
def InfoFieldWidget(field, request):
    return FieldWidget(field, InfoWidget(request))
