bl_info = {
    "name": "Bonera",
    "author": "BlenderBoi",
    "version": (1, 3, 1),
    "blender": (3, 4, 0),
    "description": "",
    "doc_url": "https://blenderboi.github.io/Bonera1.1_Addon_Documentation/",
    "category": "Rigging Utilities",
}

import bpy
from . import Bonera_Toolkit_Operators
from . import Bonera_Toolkit_Menu


from . import Bonera_Datas


from . import Generator_Operator

from . import Utility_Operator

from . import Pair_List_Renamer
from . import Pseudo_Bone_Layer
from . import Bone_Slider_Generator

from . import Hierarchy_Template

from . import Bonera_Preferences


modules = [
    Bonera_Datas,
    Bonera_Toolkit_Operators,
    Bonera_Toolkit_Menu,
    Generator_Operator,
    Utility_Operator,
    Pair_List_Renamer,
    Pseudo_Bone_Layer,
    Bone_Slider_Generator,
    Bonera_Preferences,
    Hierarchy_Template,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
