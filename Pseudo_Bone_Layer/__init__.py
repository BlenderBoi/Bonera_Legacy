

import bpy

from . import Pseudo_Bone_Layer
from . import Extras_Menu

modules = [
    Pseudo_Bone_Layer,
    Extras_Menu,
    ]

def register():


    for module in modules:
        module.register()





def unregister():

    for module in modules:
        module.unregister()





if __name__ == "__main__":
    register()
