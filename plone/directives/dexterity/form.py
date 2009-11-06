from inspect import ismethod

import zope.interface
import zope.component

import zope.interface.interface

from zope.component.zcml import handler

import martian
from martian.error import GrokError

import grokcore.security
import grokcore.view

import five.grok

from plone.z3cform import layout

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.browser import add, edit, view

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from App.class_init import InitializeClass

from Products.CMFCore.interfaces import IFolderish

from Products.Five.browser.metaconfigure import page
from Products.Five.metaclass import makeClass
from Products.Five.security import protectClass, protectName
from Products.Five.security import CheckerPrivateId

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

class DisplayForm(view.DefaultView, five.grok.View):
    """Base class for grokked display forms
    """
    martian.baseclass()
    
    def __init__(self, context, request):
        view.DefaultView.__init__(self, context, request)
        five.grok.View.__init__(self, context, request)
    
    def render(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self.template.render(self)
        return zope.publisher.publish.mapply(self.render, (), self.request)
    render.base_method = True

class AddFormGrokker(martian.ClassGrokker):
    martian.component(AddForm)
    
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, default=None)
    martian.directive(grokcore.security.require, name='permission', default='cmf.AddPortalContent')
    
    def execute(self, form, config, layer, name, permission):
        
        if not name:
            raise GrokError(u"No factory name specified for add form. Use grok.name('my.factory').", form)
        
        # Create a wrapper class that derives from the default add view
        # but sets the correct form

        cdict = {'__name__': name, 'form': form}
        bases = (add.DefaultAddView,)
        new_class = makeClass('%sWrapper' % form.__name__, bases, cdict)
        
        # Protect the class
        config.action(
            discriminator = ('five:protectClass', new_class),
            callable = protectClass,
            args = (new_class, permission)
            )
            
        # Protect the __call__ attribute
        config.action(
            discriminator = ('five:protectName', new_class, '__call__'),
            callable = protectName,
            args = (new_class, '__call__', permission)
            )
            
        # Make all other attributes private
        for attr in dir(new_class):
            if not attr.startswith('_') and attr != '__call__' and ismethod(getattr(new_class, attr)):
                config.action(
                    discriminator = ('five:protectName', new_class, attr),
                    callable = protectName,
                    args = (new_class, attr, CheckerPrivateId)
                    )
        
        # Initialise the class
        config.action(
            discriminator = ('five:initialize:class', new_class),
            callable = InitializeClass,
            args = (new_class,)
            )
        
        config.action(
            discriminator = ('dexterity:addView', IFolderish, name, IBrowserRequest, layer, IDexterityFTI),
            callable = handler,
            args = ('registerAdapter',
                    new_class, (IFolderish, layer, IDexterityFTI), zope.interface.Interface, name, config.info),
            )
        
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

__all__ = ('AddForm', 'EditForm', 'DisplayForm', )