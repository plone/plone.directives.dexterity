#
# Convenience API
#

import zope.deferredimport

# Base classes for custom content classes and directives for specifying
# the low-level add permission. This is used if also set a meta_type. If
# no meta_type is set, the type is not registered as a Zope 2 style class.
# If a portal_type is set, a factory utility will be registered (if one is
# not registered already).
#
# >>> class MyType(dexterity.Item):
# ...     implements(IMyType)
# ...     grok.name('my.type')
# ...     dexterity.add_permission('My add permission')
# ...     meta_type = 'my.type'
#
# In most cases, you can omit meta_type and add_permission(). These are only
# necessary if you want to register a Zope 2 style class that can be created
# using Zope 2's meta type factory support. This is equivalent to calling
# <five:registerClass /> in ZCML.

zope.deferredimport.defineFrom('plone.dexterity.content',
    'Item', 'Container',
)
zope.deferredimport.defineFrom('plone.directives.dexterity.content',
    'add_permission',
)

# Field permission hints. These are actually defined in plone.directives.form,
# but are imported here for convenience. Note that read_permission affects
# more than just the form: it will also affect attribute access to a content
# object using the default Dexterity base classes.
#
# >>> class ISchema(form.Schema):
# ...     dexterity.read_permission(field1='some.permission')
#
# Note that the permission name is the id of an IPermission utility.
zope.deferredimport.defineFrom('plone.directives.form',
    'read_permission', 'write_permission',
)

# Base classes for custom add-, edit- and display-forms, using z3c.form.
# For example:
#
# >>> class AddForm(dexterity.AddForm):
# ...     grok.context(IFolderType)
#
# >>> class EditForm(dexterity.EditForm):
# ...     grok.context(IFSPage)
#
# >>> class View(dexterity.DisplayForm):
# ...     grok.context(IFSPage)
#
# Note that if you want a generic form, not directly tied to a specific type's
# schema or behaviours, you should use the more general grokkers in
# plone.directives.form.
#
# See the z3c.form documentation for more details.
#
# Note that the add form created with this directive expect to be invoked
# using the ++add++<type-name> traverser. The add_view_expr property in the
# relevant type's FTI should be:
#
#  string:${folder_url}/++add++factory.name
#
# where factory.name is the name of the factory used to create an object of
# the type that the add form is form.
#
# For edit forms, the default name is 'edit', which can be overridden with
# grok.name().
#
# For display forms, you need to add a 'render' method, or use an associated
# page template in the same way that you would use grok.View.

zope.deferredimport.defineFrom('plone.directives.dexterity.form',
    'AddForm', 'EditForm', 'DisplayForm',
)
