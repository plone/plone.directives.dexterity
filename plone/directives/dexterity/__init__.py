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

# Base classes for custom add- and edit-forms, using z3c.form. For example:
# 
# >>> class AddForm(dexterity.AddForm):
# ...     portal_type = 'my.type'
# ...     fields = field.Fields(IMyType, omitReadOnly=True)
# 
# >>> class EditForm(dexterity.EditForm):
# ...     grok.context(IFSPage)
# ...     fields = fields
# 
# See the z3c.form documentation for more details. Note that for add forms,
# we have to specify the portal type to be added. The FTI should then be
# configured (with GenericSetup) to use an add_view_expr like:
# 
#  string:${folder_url}/@@add-dexterity-content/my.type
# 
# @@add-dexterity-content is a publish traverse view that will ensure the
# add form is correctly rendered.
# 
# For edit forms, the default name is 'edit', which can be overridden with
# grok.name().

zope.deferredimport.defineFrom('plone.directives.dexterity.form',
    'AddForm', 'EditForm',
)