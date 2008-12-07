import zope.interface
import zope.component

import zope.interface.interface

import martian
import grokcore.security
import grokcore.view

import plone.directives.dexterity.content
import plone.directives.dexterity.schema

from plone.z3cform import layout

from plone.dexterity.browser import add, edit

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish

from Products.Five.browser.metaconfigure import page

from plone.autoform.interfaces import FORMDATA_KEY

TEMP_KEY = '__form_directive_values__'

# Base classes

class AddForm(add.DefaultAddForm):
    """Base class for grokked add forms
    """
    martian.baseclass()

class EditForm(edit.DefaultEditForm):
    """Base class for grokked edit forms
    """
    martian.baseclass()

# Directives

class FormMetadataStorage(object):
    """Stores a value in the 'plone.formdata' metadata format.
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(zope.interface.interface.TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(TEMP_KEY, {}).get(directive.key, default)

    def setattr(self, context, directive, value):
        tags = context.queryTaggedValue(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

FORM_METADATA = FormMetadataStorage()        

class omitted(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA
    
    key = u"omitted"
    
    def factory(self, *args):
        return [(a, "true") for a in args]

class mode(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA
    
    key = u"modes"
    
    def factory(self, **kw):
        return kw.items()

class widget(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA
    
    key = u"widgets"
    
    def factory(self, **kw):
        items = []
        for field_name, widget in kw.items():
            if not isinstance(widget, basestring):
                widget = "%s.%s" % (widget.__module__, widget.__name__)
            items.append((field_name, widget))
        return items
        
class order_before(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA
    
    key = u"before"
    
    def factory(self, **kw):
        return kw.items()

class order_after(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA
    
    key = u"after"
    
    def factory(self, **kw):
        return kw.items()

# Grokkers

class FormSchemaGrokker(martian.InstanceGrokker):
    martian.component(plone.directives.dexterity.schema.Schema.__class__)
    
    martian.directive(omitted)
    martian.directive(mode)
    martian.directive(widget)
    martian.directive(order_before)
    martian.directive(order_after)
    
    def execute(self, interface, config, **kw):
        
        if not interface.extends(plone.directives.dexterity.schema.Schema):
            return False
            
        # Copy from temporary to real value
        directive_supplied = interface.queryTaggedValue(TEMP_KEY, None)
        if directive_supplied is None:
            return False
        
        real = interface.queryTaggedValue(FORMDATA_KEY, {})
        for k, v in directive_supplied.items():
            real.setdefault(k, []).extend(v)
        
        if not real:
            return False
            
        interface.setTaggedValue(FORMDATA_KEY, real)
        interface.setTaggedValue(TEMP_KEY, None)
        
        return True

class AddFormGrokker(martian.ClassGrokker):
    martian.component(AddForm)
    
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, default=None)
    martian.directive(grokcore.security.require, name='permission', default='cmf.AddPortalContent')
    
    def execute(self, form, config, layer, name, permission):
        
        if not getattr(form, 'portal_type', None):
            return False
        
        factory = layout.wrap_form(form)
        
        if not name:
            name = "add-%s" % form.portal_type
        
        factory.__name__ = name
        
        page(config,
             name=name,
             permission=permission,
             for_=IFolderish,
             layer=layer,
             class_=factory)

        return True
        
class EditFormGrokker(martian.ClassGrokker):
    martian.component(EditForm)
    
    martian.directive(grokcore.component.context, default=None)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, default='edit')
    martian.directive(grokcore.security.require, name='permission', default='cmf.ModifyPortalContent')
    
    def execute(self, form, config, context, layer, name, permission):
        
        # Only grok if the context is an interface. We demand this so that the
        # form is more re-usable in case of type customisation.
        if not isinstance(context, zope.interface.interface.InterfaceClass):
            return False
        
        factory = layout.wrap_form(form)
        factory.__name__ = name
        
        page(config,
             name=name,
             permission=permission,
             for_=context,
             layer=layer,
             class_=factory)

        return True

__all__ = ('AddForm', 'EditForm', 'omitted', 'mode', 'widget', 'order_before', 'order_after')