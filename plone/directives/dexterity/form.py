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

try:
    from AccessControl.security import protectClass, protectName
    from AccessControl.security import CheckerPrivateId
    protectClass, protectName, CheckerPrivateId  # pyflakes
except ImportError:
    from Products.Five.security import protectClass, protectName
    from Products.Five.security import CheckerPrivateId

TEMP_KEY = '__form_directive_values__'

# Find out if we want to wrap forms
from plone.directives.form.meta import DEFAULT_WRAP
from plone.directives.form.form import wrap


# Base classes

class GrokkedDexterityForm(object):

    # Emulate grokcore.view.View

    def __init__(self, context, request):
        super(GrokkedDexterityForm, self).__init__(context, request)

        # Set the view __name__
        self.__name__ = getattr(self, '__view_name__', None)

        # Set up the view.static resource directory reference
        if getattr(self, 'module_info', None) is not None:
            self.static = zope.component.queryAdapter(
                self.request,
                zope.interface.Interface,
                name=self.module_info.package_dotted_name
                )
        else:
            self.static = None

    def render(self):
        # Render a grok-style template if we have one
        if (
            getattr(self, 'template') and
            grokcore.view.interfaces.ITemplate.providedBy(self.template)
        ):
            return self._render_template()
        else:
            return super(GrokkedDexterityForm, self).render()
    render.base_method = True

    @property
    def response(self):
        return self.request.response

    def _render_template(self):
        return self.template.render(self)

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def namespace(self):
        return {}

    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name. The data
        argument is used to form a CGI query string.
        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context

        if data is None:
            data = {}
        else:
            if not isinstance(data, dict):
                raise TypeError('url() data argument must be a dict.')

        return grokcore.view.util.url(self.request, obj, name, data=data)

    def redirect(self, url):
        return self.request.response.redirect(url)

    # BBB: makes the form have the most important properties that were
    # exposed by the wrapper view

    @property
    def form_instance(self):
        return self

    @property
    def form(self):
        return self.__class__


class AddForm(GrokkedDexterityForm, add.DefaultAddForm):
    """Base class for grokked add forms
    """
    martian.baseclass()

    def __init__(self, context, request, ti=None):
        super(GrokkedDexterityForm, self).__init__(context, request)
        if ti is not None:
            self.ti = ti
            self.portal_type = ti.getId()
    
    def __of__(self, context):
        # compatibility with CMFCore which tries to wrap the add view
        return self

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(AddForm, self).render()
    render.base_method = True


class EditForm(GrokkedDexterityForm, edit.DefaultEditForm):
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
    martian.directive(grokcore.security.require, name='permission',
                      default='cmf.AddPortalContent')
    martian.directive(wrap, default=None)

    def grok(self, name, form, module_info, **kw):
        # save the module info so that we can look for templates later
        form.module_info = module_info
        return super(AddFormGrokker, self).grok(name, form, module_info, **kw)

    def execute(self, form, config, layer, name, permission, wrap):

        if not name:
            raise GrokError(u"No factory name specified for add form. "
                            u"Use grok.name('my.factory').", form)

        templates = form.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, form.module_info, form)
                )

        form.__view_name__ = name

        # Unlike the other forms, we default to wrapping for backwards-
        # compatibility with custom templates that assume wrapping.
        if wrap is None:
            wrap = True

        if wrap:
            new_class = layout.wrap_form(form, __wrapper_class=add.DefaultAddView)
            new_class.__view_name__ = new_class.__name__ = name
        else:
            new_class = form

        # Protect the class
        config.action(
            discriminator=('five:protectClass', new_class),
            callable=protectClass,
            args=(new_class, permission)
            )

        # Protect the __call__ attribute
        config.action(
            discriminator=('five:protectName', new_class, '__call__'),
            callable=protectName,
            args=(new_class, '__call__', permission)
            )

        # Make all other attributes private
        for attr in dir(new_class):
            if (not attr.startswith('_') and attr != '__call__'
                and ismethod(getattr(new_class, attr))):
                config.action(
                    discriminator=('five:protectName', new_class, attr),
                    callable=protectName,
                    args=(new_class, attr, CheckerPrivateId)
                    )

        # Initialise the class
        config.action(
            discriminator=('five:initialize:class', new_class),
            callable=InitializeClass,
            args=(new_class,)
            )

        config.action(
            discriminator=('dexterity:addView', IFolderish, name,
                           IBrowserRequest, layer, IDexterityFTI),
            callable=handler,
            args=('registerAdapter',
                  new_class, (IFolderish, layer, IDexterityFTI),
                  zope.interface.Interface, name, config.info),
            )

        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            # Unlike the view grokker, we are happy with the base class
            # version
            return getattr(factory, 'render', None) is None

        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)


class EditFormGrokker(martian.ClassGrokker):
    martian.component(EditForm)

    martian.directive(grokcore.component.context, default=None)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, default='edit')
    martian.directive(grokcore.security.require, name='permission',
                      default='cmf.ModifyPortalContent')
    martian.directive(wrap, default=None)

    def grok(self, name, form, module_info, **kw):
        # save the module info so that we can look for templates later
        form.module_info = module_info
        return super(EditFormGrokker, self).grok(name, form, module_info, **kw)

    def execute(self, form, config, context, layer, name, permission, wrap):

        # Only grok if the context is an interface. We demand this so that the
        # form is more re-usable in case of type customisation.
        if not isinstance(context, zope.interface.interface.InterfaceClass):
            return False

        templates = form.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, form.module_info, form)
                )

        form.__view_name__ = name

        if wrap is None:
            wrap = DEFAULT_WRAP

        # Only use the wrapper view if we are on Zope < 2.12
        if wrap:
            factory = layout.wrap_form(form)
            factory.__view_name__ = name
        else:
            factory = form

        page(
                config,
                name=name,
                permission=permission,
                for_=context,
                layer=layer,
                class_=factory
            )

        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            # Unlike the view grokker, we are happy with the base class
            # version
            return getattr(factory, 'render', None) is None

        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)

__all__ = ('AddForm', 'EditForm', 'DisplayForm', )
