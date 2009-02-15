import unittest
import mocker
from plone.mocktestcase import MockTestCase

from zope.interface import Interface, alsoProvides
from zope.component import getMultiAdapter

from grokcore.component.testing import grok, grok_component
import five.grok

from plone.directives.dexterity import form

from plone.dexterity.fti import DexterityFTI
from plone.dexterity.browser import add

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish

class TestContext(object):
    five.grok.implements(IFolderish)

class TestRequest(object):

    def __init__(self, layer=IDefaultBrowserLayer):
        alsoProvides(self, layer)

    def __setitem__(self, name, value):
        pass

class TestFormDirectives(MockTestCase):

    def setUp(self):
        super(TestFormDirectives, self).setUp()
        grok('plone.directives.dexterity.form')
        
    def test_addform_grokker_bails_without_factory(self):
        
        class AddForm(form.AddForm):
            pass
        
        self.replay()
        
        self.assertEquals(False, grok_component('AddForm', AddForm))

    def test_addform_registered_with_factory(self):
        
        class AddForm(form.AddForm):
            five.grok.name('my.type')
        
        def match_addview():
            return mocker.MATCH(lambda x: issubclass(x, add.DefaultAddView))
        
        protectClass_mock = self.mocker.replace('Products.Five.security.protectClass')
        self.expect(protectClass_mock(match_addview(), "cmf.AddPortalContent"))
        
        protectName_mock = self.mocker.replace('Products.Five.security.protectName')
        self.expect(protectName_mock(match_addview(), '__call__', "cmf.AddPortalContent"))
        
        self.expect(protectName_mock(match_addview(), self.match_type(basestring), 'zope2.Private')).count(1,None)
        
        self.replay()
        
        self.assertEquals(True, grok_component('AddForm', AddForm))
        
        # Find the adapter that was registered
        
        view = getMultiAdapter((TestContext(), TestRequest(), DexterityFTI(u"my.type")), name=u"my.type")
        self.failUnless(isinstance(view, add.DefaultAddView))
        self.assertEquals(AddForm, view.form)

    def test_addform_registered_with_factory_layer_and_permission(self):
        
        class ITestLayer(Interface):
            pass
        
        class AddForm(form.AddForm):
            five.grok.name('my.type')
            five.grok.layer(ITestLayer)
            five.grok.require('my.permission')
        
        def match_addview():
            return mocker.MATCH(lambda x: issubclass(x, add.DefaultAddView))
        
        protectClass_mock = self.mocker.replace('Products.Five.security.protectClass')
        self.expect(protectClass_mock(match_addview(), "my.permission"))
        
        protectName_mock = self.mocker.replace('Products.Five.security.protectName')
        self.expect(protectName_mock(match_addview(), '__call__', "my.permission"))
        
        self.expect(protectName_mock(match_addview(), self.match_type(basestring), 'zope2.Private')).count(1,None)
        
        self.replay()
        
        self.assertEquals(True, grok_component('AddForm', AddForm))
        
        # Find the adapter that was registered
        
        view = getMultiAdapter((TestContext(), TestRequest(ITestLayer), DexterityFTI(u"my.type")), name=u"my.type")
        self.failUnless(isinstance(view, add.DefaultAddView))
        self.assertEquals(AddForm, view.form)

    def test_edit_form_bails_without_context(self):
        
        class EditForm(form.AddForm):
            pass
        
        self.replay()
        
        self.assertEquals(False, grok_component('EditForm', EditForm))

    def test_edit_form_bails_without_interface_as_context(self):
        
        class Foo(object):
            pass
        
        class EditForm(form.AddForm):
            five.grok.context(Foo)
        
        self.replay()
        
        self.assertEquals(False, grok_component('EditForm', EditForm))

    def test_editform_with_defaults(self):
        
        class IDummyContent(Interface):
            pass
        
        class EditForm(form.EditForm):
            five.grok.context(IDummyContent)
        
        wrapped = self.create_dummy()
        
        wrap_form_mock = self.mocker.replace('plone.z3cform.layout.wrap_form')
        self.expect(wrap_form_mock(EditForm)).result(wrapped)
        
        page_mock = self.mocker.replace('Products.Five.browser.metaconfigure.page')
        self.expect(page_mock(mocker.ANY, 
                              name='edit',
                              permission='cmf.ModifyPortalContent',
                              for_=IDummyContent,
                              layer=IDefaultBrowserLayer,
                              class_=wrapped))
        
        self.replay()
        
        self.assertEquals(True, grok_component('EditForm', EditForm))
        
    def test_editform_with_custom_layer_name_permission(self):
        
        class IDummyContent(Interface):
            pass
        
        class ILayer(IDefaultBrowserLayer):
            pass
        
        class EditForm(form.EditForm):
            five.grok.context(IDummyContent)
            five.grok.name('edith')
            five.grok.require('my.permission')
            five.grok.layer(ILayer)
        
        wrapped = self.create_dummy()
        
        wrap_form_mock = self.mocker.replace('plone.z3cform.layout.wrap_form')
        self.expect(wrap_form_mock(EditForm)).result(wrapped)
        
        page_mock = self.mocker.replace('Products.Five.browser.metaconfigure.page')
        self.expect(page_mock(mocker.ANY, 
                              name='edith',
                              permission='my.permission',
                              for_=IDummyContent,
                              layer=ILayer,
                              class_=wrapped))
        
        self.replay()
        
        self.assertEquals(True, grok_component('EditForm', EditForm))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFormDirectives))
    return suite