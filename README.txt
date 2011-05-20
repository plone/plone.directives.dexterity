==========================
plone.directives.dexterity
==========================

This package provides optional, Grok-like directives for configuring
Dexterity content. It depends on five.grok, which in turn depends on
the various re-usable grokcore.* packages, but not Grok itself.

See also plone.directives.form, which provides directives for configuring
schema interfaces with form hints.

Content classes
---------------

Content extending the Dexterity 'Item' and 'Container' base classes can be
grokked in order to register a factory and/or ZMI add permission.

For example::

    from plone.directives import dexterity
    from plone.directives import form
    from five import grok
    from zope import schema

    class IPage(form.Schema):
    
        title = schema.TextLine(title=u"Title")
    
        description = schema.Text(title=u"Description",
                              description=u"Summary of the body")
    
        body = schema.Text(title=u"Body text",
                           required=False,
                           default=u"Body text goes here")

        details = schema.Text(title=u"Details",
                              required=False)

    class FSPage(dexterity.Item):
        grok.implements(IPage)
        grok.name('example.page')
    
        def __init__(self, id=None, title=None, description=None, body=None, details=None):
            self.id = id # required - or call super() with this argument
            self.title = title
            self.description = description
            self.body = body
            self.details = details
            
This will register a factory utility if one is not already present with
the name 'example.fspage'.

You can also use the 'add_permission()' directive to cause the type to be
registered as a Zope 2 content class, in the same way that the 
<five:registerClass /> directive does::

    class ZopeTwoItem(dexterity.Item):
        grok.implements(IPage)
        dexterity.add_permission('cmf.AddPortalContent')
        portal_type = 'example.zopetwopage'

However, for most content types, this will be unnecessary.

Forms
-----

To create a Dexterity add-, edit- or display form for your type, use the
AddForm, EditForm or DisplayForm base classes. For example::

    from plone.directives import dexterity
    from plone.directives import form
    from five import grok
    from zope import schema

    class IPage(form.Schema):
    
        title = schema.TextLine(title=u"Title")
    
        description = schema.Text(title=u"Description",
                              description=u"Summary of the body")
    
        body = schema.Text(title=u"Body text",
                           required=False,
                           default=u"Body text goes here")

        details = schema.Text(title=u"Details",
                              required=False)

    class View(dexterity.DisplayForm):
        """The view. May will a template from <modulename>_templates/view.pt,
        and will be called 'view' unless otherwise stated.
        """
        grok.require('zope2.View')
        grok.context(IPage)
        
    class Edit(dexterity.EditForm):
        """A standard edit form.
        """
        grok.context(IPage)
        
        def updateWidgets(self):
            super(Edit, self).updateWidgets()
            self.widgets['title'].mode = 'hidden'

These forms are grokked in a manner that is similar to
`plone.directives.form`_, and support custom template associations. Please
note, however:

* When using ``dexterity.AddForm`` as a base, you must use the ``grok.name()``
  directive to give the name of the add view. Usually, this is the same as
  the name of the Factory Type Information object.
* When using ``dexterity.EditForm`` as a base, you must use ``grok.context()``
  and supply a Dexterity content type interface as an argument. This is to
  allow proper re-use of types.

.. _plone.directives.form: http://pypi.python.org/pypi/plone.directives.form
