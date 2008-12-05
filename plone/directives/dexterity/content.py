import martian

from zope.component import queryUtility
from zope.component import provideUtility

from zope.component.interfaces import IFactory
from zope.component.factory import Factory

from plone.dexterity.content import DexterityContent

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

    martian.directive(add_permission)
    
    def execute(self, class_, config, add_permission, **kw):
        
        # 1. Register class if a meta type was specified. Most types
        # will probably not need this.
        
        meta_type = getattr(class_, 'meta_type', None)
        if add_permission is not None:
            registerClass(config, class_, meta_type, add_permission)
        
        config.action(
                discriminator=('plone.dexterity.content', class_,),
                callable=register_content,
                args=(class_,),
                order=9999,
                )
        
        return True
        
def register_content(class_):

    # Register factory if not already registered
    portal_type = getattr(class_, 'portal_type', None)
    if portal_type:
        factory = queryUtility(IFactory, name=portal_type)
        if factory is None:
            provideUtility(Factory(class_), IFactory, portal_type)
    
__all__ = ('portal_type', 'meta_type', 'add_permission',)