import unittest
import mocker
from plone.mocktestcase import MockTestCase

from zope.interface import Interface
import zope.schema

from grokcore.component.testing import grok, grok_component
import five.grok

from plone.directives.dexterity import schema, form

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish

from plone.autoform.interfaces import FORMDATA_KEY

class DummyWidget(object):
    pass

class TestSchemaDirectives(MockTestCase):

    def setUp(self):
        super(TestSchemaDirectives, self).setUp()
        grok('plone.directives.dexterity.form')

    def test_schema_directives_store_tagged_values(self):
        
        class IDummy(schema.Schema):
            
            form.omitted('foo', 'bar')
            form.widget(foo='some.dummy.Widget', baz='other.Widget')
            form.mode(bar='hidden')
            form.order_before(baz='title')
            
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('foo', 'some.dummy.Widget'), ('baz', 'other.Widget')],
                           u'omitted': [('foo', 'true'), ('bar', 'true')],
                           u'moves': [('baz', 'title')],
                           u'modes': [('bar', 'hidden')]},
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        
    def test_widget_supports_instances_and_strings(self):
        
        class IDummy(schema.Schema):
            
            form.widget(foo=DummyWidget)
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('foo', 'plone.directives.dexterity.tests.test_form.DummyWidget')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        
    def test_schema_directives_extend_existing_tagged_values(self):
        
        class IDummy(schema.Schema):
            form.widget(foo='some.dummy.Widget')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        IDummy.setTaggedValue(FORMDATA_KEY, {u'widgets': [('alpha', 'some.Widget')]})
            
        self.replay()
        
        self.assertEquals({u'widgets': [('alpha', 'some.Widget')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('alpha', 'some.Widget'), ('foo', 'some.dummy.Widget')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        
    def test_multiple_invocations(self):
        
        class IDummy(schema.Schema):
            
            form.omitted('foo')
            form.omitted('bar')
            form.widget(foo='some.dummy.Widget')
            form.widget(baz='other.Widget')
            form.mode(bar='hidden')
            form.mode(foo='display')
            form.order_before(baz='title')
            form.order_before(foo='body')
            
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('foo', 'some.dummy.Widget'), ('baz', 'other.Widget')],
                           u'omitted': [('foo', 'true'), ('bar', 'true')],
                           u'moves': [('baz', 'title'), ('foo', 'body')],
                           u'modes': [('bar', 'hidden'), ('foo', 'display')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))

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
    suite.addTest(unittest.makeSuite(TestSchemaDirectives))
    suite.addTest(unittest.makeSuite(TestFormDirectives))
    return suite
