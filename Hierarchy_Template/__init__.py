import bpy

from . import Hierarchy_Template_Panel

from . import Export_Hierarchy_Template
from . import Import_Hierarchy_Template

modules = [
    Export_Hierarchy_Template,
    Import_Hierarchy_Template,
    Hierarchy_Template_Panel,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
