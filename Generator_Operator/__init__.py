

import bpy

from . import Generate_IK
from . import Generate_Driver_Bone
from . import Generate_Hydraulic_Rig
from . import Generate_Basic_Joint
from . import Generate_Eyelid
from . import Generate_Stretch_Chain
from . import Generate_Twist_Bone

modules = [
    Generate_IK,
    Generate_Driver_Bone,
    Generate_Hydraulic_Rig,
    Generate_Basic_Joint,
    Generate_Eyelid,
    Generate_Stretch_Chain,
    Generate_Twist_Bone
    ]

def register():


    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
