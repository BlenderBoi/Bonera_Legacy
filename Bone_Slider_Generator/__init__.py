import bpy

from . import Bone_Slider_Generator_Panel


modules = [
    Bone_Slider_Generator_Panel,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
