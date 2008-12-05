==========================
plone.directives.dexterity
==========================

This package provides optional, Grok-like directives for configuring
Dexterity content. It depends on five.grok, which in turn depends on
the various re-usable grokcore.* packages, but not Grok itself.

The basic usage pattern is as follows::

    from zope import schema
    from plone.directives import dexterity
    from five import grok
    
    class IMySchema(dexterity.Schema):
        
        
        title = schema.TextLine(
                title=u"Title"
            )
        
        hidden_field = schema.Text(
                title=u"Hidden details"
            )
        dexterity.omitted('hidden_field')
        
    class MyType(dexterity.Item):
        grok.implements(IMySchema)
    
    class View(grok.View):
        grok.context(IMySchema)
        grok.require('zope2.View')

Schemata loaded from XML
------------------------

If you want to create a concrete interface, with a real module path, from
a plone.supermodel XML file, you can do::

    from plone.directives import dexterity
    class IMySchema(dexterity.Schema):
        dexterity.model('myschema.xml')
        
The file will be loaded from the directory where the .py file for the
interface is located, unless an absolute path is given.

If the interface contains additional schema fields, they will add to and
override fields defined in the XML file.

See tests/schema.txt for more details.

Form widget hints
-----------------

Dexterity - via the plone.autoform package - has the ability to generate
a form from a schema, using hints stored in tagged values on that form to
control form layout and field widgets. Those hints can be set using directives
from this package.

Below is an example that exercises the various directives::

    from plone.directives import dexterity
    from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

    class IMySchema(dexterity.Schema):
    
        # Add a new fieldset and put the 'footer' and 'dummy' fields in it.
        # If the same fieldset is defined multiple times, the definitions
        # will be merged, with the label from the first fieldset taking
        # precedence.
        
        dexterity.fieldset('extra', 
                label=u"Extra info",
                fields=['footer', 'dummy']
            )

        title = schema.TextLine(
                title=u"Title"
            )
    
        summary = schema.Text(
                title=u"Summary",
                description=u"Summary of the body",
                readonly=True
            )
    
        body = schema.Text(
                title=u"Body text",
                required=False,
                default=u"Body text goes here"
            )
        dexterity.widget(body='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
                       
        footer = schema.Text(
                title=u"Footer text",
                required=False
            )
        dexterity.widget(footer=WysiwygFieldWidget)
    
        dummy = schema.Text(
                title=u"Dummy"
            )
        dexterity.omitted('dummy')
    
        secret = schema.TextLine(
                title=u"Secret",
                default=u"Secret stuff"
            )
        dexterity.mode(secret='hidden')

Here, we have placed the directives immediately after the fields they
affect, but they could be placed anywhere in the interface body. All the
directives can take multiple values, usually in the form fieldname='value'.
The 'omitted()' directive takes a list of omitted field names instead. The
'widget()' directive allows widgets to be set either as a dotted name, or
using an imported field widget factory.

Content classes
---------------

Content extending the Dexterity 'Item' and 'Container' base classes can be
grokked as well. For example::

    class IFSPage(dexterity.Schema):
    
        title = schema.TextLine(title=u"Title")
    
        description = schema.Text(title=u"Description",
                              description=u"Summary of the body")
    
        body = schema.Text(title=u"Body text",
                           required=False,
                           default=u"Body text goes here")

        details = schema.Text(title=u"Details",
                              required=False)

    class FSPage(dexterity.Item):
        grok.implements(IFSPage)
        portal_type = 'example.fspage'
    
        def __init__(self, id=None, title=None, description=None, body=None, details=None):
            self.id = id # required - or call super() with this argument
            self.title = title
            self.description = description
            self.body = body
            self.details = details
            
This will register a factory utility if one is not already present with
the same name as the portal_type.

You can also use the 'add_permission()' directive to cause the type to be
registered as a Zope 2 content class, in the same way that the 
<five:registerClass /> directive does::

    class ZopeTwoPage(dexterity.Item):
        grok.implements(IFSPage)
        dexterity.add_permission()
        portal_type = 'example.zopetwopage'