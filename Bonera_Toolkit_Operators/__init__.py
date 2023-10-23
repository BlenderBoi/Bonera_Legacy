import bpy

from . import Create_Bones_From_Selected
from . import Create_Empties_From_Selected

from . import Add_Bone_Shape
from . import Create_Bone_Chain_From_Object_Hierarchy
from . import Create_Bone_From_Vertex_Group
from . import Create_Bone_Chain_From_Curve
from . import Bonadd
from . import Bonera_Toolkit_Panel

from . import Mirror_Bone_Shapes
from . import Convert_Curve_To_Bone

from . import Create_Spline_Bone_From_Curve
from . import Create_Empties_From_Selected_Bones_And_Follow_Path
from . import Create_Bone_Chain_From_Select_Order

modules = [
    Convert_Curve_To_Bone,
    Create_Bones_From_Selected,
    Create_Empties_From_Selected,
    Mirror_Bone_Shapes,
    Add_Bone_Shape,
    Create_Bone_Chain_From_Object_Hierarchy,
    Create_Bone_From_Vertex_Group,
    Create_Bone_Chain_From_Curve,
    Create_Spline_Bone_From_Curve,
    Create_Empties_From_Selected_Bones_And_Follow_Path,
    Create_Bone_Chain_From_Select_Order,
    Bonadd,
    Bonera_Toolkit_Panel
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
