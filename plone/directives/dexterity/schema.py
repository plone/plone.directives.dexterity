import sys
import os.path

import martian
from martian.error import GrokImportError

from zope.interface import Interface
from zope.interface.interface import TAGGED_DATA

from plone.supermodel.interfaces import FILENAME_KEY
from plone.supermodel.interfaces import SCHEMA_NAME_KEY
from plone.supermodel.interfaces import FIELDSETS_KEY

from plone.supermodel.model import Fieldset

from plone.supermodel import load_file
from plone.supermodel import utils

class Schema(Interface):
    """Base class for schema interfaces that can be grokked using the
    model() directive.
    """

class FilenameStorage(object):
    """Stores the model() directive value in a schema tagged value.
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {})
        tags[FILENAME_KEY] = value["filename"]
        tags[SCHEMA_NAME_KEY] = value["schema"]

    def get(self, directive, component, default):
        return dict(filename=component.queryTaggedValue(FILENAME_KEY, default),
                    schema=component.queryTaggedValue(SCHEMA_NAME_KEY, default))

    def setattr(self, context, directive, value):
        context.setTaggedValue(FILENAME_KEY, value["filename"])
        context.setTaggedValue(SCHEMA_NAME_KEY, value["schema"])

class FieldsetStorage(object):
    """Stores the fieldset() directive value in a schema tagged value.
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {})
        tags.setdefault(FIELDSETS_KEY, []).append(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(FIELDSETS_KEY, [])

    def setattr(self, context, directive, value):
        context.setTaggedValue(FIELDSETS_KEY, value)

class model(martian.Directive):
    """Directive used to specify the XML model file
    """
    scope = martian.CLASS
    store = FilenameStorage()
    
    def factory(self, filename, schema=u""):
        return dict(filename=filename, schema=schema)

class fieldset(martian.Directive):
    """Directive used to create fieldsets
    """
    scope = martian.CLASS
    store = FieldsetStorage()
    
    def factory(self, name, label=None, description=None, fields=None):
        return Fieldset(name, label=label, description=description, fields=fields)

class SchemaGrokker(martian.InstanceGrokker):
    martian.component(Schema.__class__)
    martian.directive(model)
    martian.directive(fieldset)
    
    def execute(self, interface, config, **kw):
        
        if not interface.extends(Schema):
           return False
        
        filename = interface.queryTaggedValue(FILENAME_KEY, None)
        
        if filename is not None:
            
            schema = interface.queryTaggedValue(SCHEMA_NAME_KEY, u"")
            
            module_name = interface.__module__
            module = sys.modules[module_name]
        
            directory = module_name
        
            if hasattr(module, '__path__'):
                directory = module.__path__[0]
            elif "." in module_name:
                parent_module_name = module_name[:module_name.rfind('.')]
                directory = sys.modules[parent_module_name].__path__[0]
        
            directory = os.path.abspath(directory)
            filename = os.path.abspath(os.path.join(directory, filename))
            
            # Let / act as path separator on all platforms
            filename = filename.replace('/', os.path.sep)
        
            interface.setTaggedValue(FILENAME_KEY, filename)
        
            config.action(
                discriminator=('plone.supermodel.schema', interface, filename, schema),
                callable=scribble_schema,
                args=(interface,),
                order=9999,
                )
        
        return True

def scribble_schema(interface):
    
    filename = interface.getTaggedValue(FILENAME_KEY)
    schema = interface.queryTaggedValue(SCHEMA_NAME_KEY, u"")
    
    model = load_file(filename)
    
    if schema not in model.schemata:
        raise GrokImportError(u"Schema '%s' specified for interface %s does not exist in %s." % 
                                (schema, interface.__identifier__, filename,)) 
    
    utils.sync_schema(model.schemata[schema], interface, overwrite=False)
    
__all__ = ('Schema', 'model', 'fieldset',)