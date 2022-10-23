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
    """A widget TestData Import"""


@implementer_only(ITestDataImportWidget)
class TestDataImportWidget(Widget):
    """ TestData Import Widget to Render Import Form """

    error = None
    value = None

    def update(self):
        pass

    def get_portal_url(self):
        return api.portal.get().absolute_url()


@implementer(IFieldWidget)
@adapter(IField, IFormLayer)
def TestDataImportFieldWidget(field, request):
    return FieldWidget(field, TestDataImportWidget(request))


class IRefreshWidget(IWidget):
    """A widget Refresh"""


@implementer_only(IRefreshWidget)
class RefreshWidget(Widget):
    """ Refresh Widget to Render Refresh Form """

    error = None
    value = None

    def update(self):
        pass

    def get_portal_url(self):
        return api.portal.get().absolute_url()


@implementer(IFieldWidget)
@adapter(IField, IFormLayer)
def RefreshFieldWidget(field, request):
    return FieldWidget(field, RefreshWidget(request))
