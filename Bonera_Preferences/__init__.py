import bpy

from . import Affixes_Preset_List
from . import Preferences
from . import Open_Bone_Shape_Folder

modules = [
    Affixes_Preset_List,
    Preferences,
    Open_Bone_Shape_Folder,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
