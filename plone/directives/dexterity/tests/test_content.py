import unittest
import mocker
from plone.mocktestcase import MockTestCase

from zope.interface import implements, Interface
import zope.schema

from zope.configuration.interfaces import IConfigurationContext

from zope.component.interfaces import IFactory

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.interfaces import IAdding

from grokcore.component.testing import grok, grok_component

from plone.directives.dexterity.schema import Schema
from plone.directives.dexterity.content import add_permission
from plone.dexterity.content import Item

class DummyWidget(object):
    pass

class TestContentDirectives(MockTestCase):

    def setUp(self):
        super(TestContentDirectives, self).setUp()
        grok('plone.directives.dexterity.content')

    def test_register_class_with_meta_type_and_add_permission(self):
        class Content(Item):
            meta_type = "ContentMT"
            add_permission(u"mock.AddPermission")
        
        registerClass_mock = self.mocker.replace('Products.Five.fiveconfigure.registerClass')
        self.expect(registerClass_mock(self.match_provides(IConfigurationContext), 
                                        Content, "ContentMT", u"mock.AddPermission"))
    
        self.replay()
        
        grok_component('Content', Content)
        
    def test_no_register_class_without_add_permission(self):
        class Content(Item):
            meta_type = "ContentMT"
        
        registerClass_mock = self.mocker.replace('Products.Five.fiveconfigure.registerClass')
        self.expect(registerClass_mock(mocker.ANY, Content, mocker.ANY, mocker.ANY)).count(0)
    
        self.replay()
        
        grok_component('Content', Content)
    
    def test_schema_interface_initialisation_does_not_overwrite(self):
        
        class IContent(Schema):
            
            foo = zope.schema.TextLine(title=u"Foo", default=u"bar")
        
        class Content(Item):
            implements(IContent)
        
            foo = u"baz"
        
        self.replay()

        grok_component('Content', Content)
        self.assertEquals(u"baz", Content.foo)
    
    def test_non_schema_interfaces_not_initialised(self):
        
        class IContent(Interface):
            
            foo = zope.schema.TextLine(title=u"Foo", default=u"bar")
        
        class Content(Item):
            implements(IContent)
        
        self.replay()

        self.failIf(hasattr(Content, "foo"))
        grok_component('Content', Content)
        self.failIf(hasattr(Content, "foo"))
        
    def test_security_initialised(self):
        # TODO: Add tests here as part of security implementation
        pass
        
    def test_portal_type_registers_factory_and_addview(self):
        
        class Content(Item):
            portal_type = 'my.type'
        
        provideUtility_mock = self.mocker.replace('zope.component.provideUtility')
        self.expect(provideUtility_mock(self.match_provides(IFactory), IFactory, 'my.type'))

        self.replay()
        
        grok_component('Content', Content)
    
    def test_portal_type_does_not_overwrite_factory_and_addview(self):
        
        class Content(Item):
            portal_type = 'my.type'
        
        factory_dummy = self.create_dummy()
        self.mock_utility(factory_dummy, IFactory, 'my.type')
        
        addview_dummy = self.create_dummy()
        self.mock_adapter(addview_dummy, Interface, (IAdding, IBrowserRequest), 'my.type')
        
        provideUtility_mock = self.mocker.replace('zope.component.provideUtility')
        self.expect(provideUtility_mock(mocker.ANY, IFactory, 'my.type')).count(0)
    
        provideAdapter_mock = self.mocker.replace('zope.component.provideAdapter')
        self.expect(provideAdapter_mock(factory=mocker.ANY,
                                        adapts=(IAdding, IBrowserRequest),
                                        provides=mocker.ANY,
                                        name='my.type')).count(0)
    
        self.replay()
        
        grok_component('Content', Content)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentDirectives))
    return suite
