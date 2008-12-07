import unittest
import mocker
from plone.mocktestcase import MockTestCase

from zope.interface import Interface
import zope.schema

from grokcore.component.testing import grok, grok_component
import five.grok

from plone.directives.dexterity import form

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish

from plone.autoform.interfaces import FORMDATA_KEY

class TestFormDirectives(MockTestCase):

    def setUp(self):
        super(TestFormDirectives, self).setUp()
        grok('plone.directives.dexterity.form')
        
    def test_addform_grokker_bails_without_portal_type(self):
        
        class AddForm(form.AddForm):
            pass
        
        self.replay()
        
        self.assertEquals(False, grok_component('AddForm', AddForm))

    def test_addform_registers_page_with_portal_type(self):
        
        class AddForm(form.AddForm):
            portal_type = 'my.type'
        
        wrapped = self.create_dummy()
        
        wrap_form_mock = self.mocker.replace('plone.z3cform.layout.wrap_form')
        self.expect(wrap_form_mock(AddForm)).result(wrapped)
        
        page_mock = self.mocker.replace('Products.Five.browser.metaconfigure.page')
        self.expect(page_mock(mocker.ANY, 
                              name='add-my.type',
                              permission='cmf.AddPortalContent',
                              for_=IFolderish,
                              layer=IDefaultBrowserLayer,
                              class_=wrapped))
        
        self.replay()
        
        self.assertEquals(True, grok_component('AddForm', AddForm))

    def test_addform_registers_page_with_custom_name_and_layer(self):
        
        class ILayer(IDefaultBrowserLayer):
            pass
        
        class AddForm(form.AddForm):
            portal_type = 'my.type'
            five.grok.name('add-foo')
            five.grok.layer(ILayer)
            five.grok.require('my.permission')
        
        wrapped = self.create_dummy()
        
        wrap_form_mock = self.mocker.replace('plone.z3cform.layout.wrap_form')
        self.expect(wrap_form_mock(AddForm)).result(wrapped)
        
        page_mock = self.mocker.replace('Products.Five.browser.metaconfigure.page')
        self.expect(page_mock(mocker.ANY, 
                              name='add-foo',
                              permission='my.permission',
                              for_=IFolderish,
                              layer=ILayer,
                              class_=wrapped))
        
        self.replay()
        
        self.assertEquals(True, grok_component('AddForm', AddForm))

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
