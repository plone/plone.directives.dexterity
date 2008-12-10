import unittest
import mocker
from plone.mocktestcase import MockTestCase

from zope.configuration.interfaces import IConfigurationContext

from zope.component.interfaces import IFactory

import five.grok
from grokcore.component.testing import grok, grok_component

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
    
        initializeClass_mock = self.mocker.replace('Products.Five.security.initializeClass')
        self.expect(initializeClass_mock(Content))
    
        self.replay()
        
        grok_component('Content', Content)
        
    def test_no_register_class_without_add_permission(self):
        class Content(Item):
            meta_type = "ContentMT"
        
        registerClass_mock = self.mocker.replace('Products.Five.fiveconfigure.registerClass')
        self.expect(registerClass_mock(mocker.ANY, Content, mocker.ANY, mocker.ANY)).count(0)
    
        initializeClass_mock = self.mocker.replace('Products.Five.security.initializeClass')
        self.expect(initializeClass_mock(Content))
    
        self.replay()
        
        grok_component('Content', Content)
    
    def test_class_security_initialised(self):
        
        class Content(Item):
            pass
        
        initializeClass_mock = self.mocker.replace('Products.Five.security.initializeClass')
        self.expect(initializeClass_mock(Content))
    
        self.replay()
        
        grok_component('Content', Content)
        
        
    def test_name_registers_factory(self):
        
        class Content(Item):
            five.grok.name('my.type')
        
        provideUtility_mock = self.mocker.replace('zope.component.provideUtility')
        self.expect(provideUtility_mock(self.match_provides(IFactory), IFactory, 'my.type'))

        initializeClass_mock = self.mocker.replace('Products.Five.security.initializeClass')
        self.expect(initializeClass_mock(Content))
        
        self.replay()
        
        grok_component('Content', Content)
    
    def test_name_does_not_overwrite_factory(self):
        
        class Content(Item):
            five.grok.name('my.type')
        
        factory_dummy = self.create_dummy()
        self.mock_utility(factory_dummy, IFactory, 'my.type')
        
        provideUtility_mock = self.mocker.replace('zope.component.provideUtility')
        self.expect(provideUtility_mock(mocker.ANY, IFactory, 'my.type')).count(0)
    
        initializeClass_mock = self.mocker.replace('Products.Five.security.initializeClass')
        self.expect(initializeClass_mock(Content))
    
        self.replay()
        
        grok_component('Content', Content)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentDirectives))
    return suite
