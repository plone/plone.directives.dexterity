import martian
import grokcore.component

from zope.component import queryUtility
from zope.component import provideUtility

from zope.component.interfaces import IFactory
from zope.component.factory import Factory

from plone.dexterity.content import DexterityContent

from App.class_init import InitializeClass
from Products.Five.fiveconfigure import registerClass

class add_permission(martian.Directive):
    """Directive used to specify the add permission of an object
    """
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    validate = martian.validateText
    
    def factory(self, permission):
        return permission

class ContentGrokker(martian.ClassGrokker):
    martian.component(DexterityContent)

    martian.directive(add_permission, default=None)
    martian.directive(grokcore.component.name, default=None)
    
    def execute(self, class_, config, add_permission, name, **kw):
        
        # Register class if a meta type was specified. 
        # (most types will probably not need this.)
        
        if add_permission:
            meta_type = getattr(class_, 'meta_type', None)
            registerClass(config, class_, meta_type, add_permission)
        
        # Register a factory utility - defer this to the end of ZCML
        # processing, since there may have been another utility manually
        # registered
        
        if name:        
            config.action(
                    discriminator=('dexterity:registerFactory', class_, name),
                    callable=register_factory,
                    args=(class_, name),
                    order=9999,
                    )
        
        # Initialise class security
        
        config.action(
            discriminator=('dexterity:registerClass', class_),
            callable=InitializeClass,
            args=(class_,)
            )
        
        return True
        
def register_factory(class_, name):

    # Register factory if not already registered
    factory = queryUtility(IFactory, name=name)
    if factory is None:
        provideUtility(Factory(class_), IFactory, name)
    
__all__ = ('portal_type', 'meta_type', 'add_permission',)