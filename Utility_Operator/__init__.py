
from . import Cleanup_Operator
from . import Orphan_Parent
from . import Smooth_All_Weights
# from . import Object_Vertex_Group
from . import Parent_Object_to_Bone_By_Name
from . import Convert_Object_Bone_Parent_To_Weight
from . import Constraint_To_Armature

from . import Constraint_Toogle
from . import Duplicate_And_Constraint
from . import Fix_IK_Angle
from . import Create_Empty_And_Copy_Transform_Bone
from . import Convert_Bendy_Bones_To_Bones
# from . import Add_Selected_Objects_To_Bone_Shape_Library

from . import Weight_Object
from . import Constraint_Bones_To_Object_By_Name
from . import Move_Object_To_Bone_By_Name
from . import Join_And_Parent_Selected_To_Bone_By_Armature_Name

from . import Proximity_Parent 

modules = [
    Convert_Bendy_Bones_To_Bones, 
    Create_Empty_And_Copy_Transform_Bone,
    Constraint_Toogle,
    Cleanup_Operator,
    Orphan_Parent,
    Smooth_All_Weights,
    # Object_Vertex_Group,
    Parent_Object_to_Bone_By_Name,
    Convert_Object_Bone_Parent_To_Weight,
    Constraint_To_Armature,
    Duplicate_And_Constraint,
    Fix_IK_Angle,
    Weight_Object, 
    Constraint_Bones_To_Object_By_Name,
    Move_Object_To_Bone_By_Name,
    Join_And_Parent_Selected_To_Bone_By_Armature_Name,
    Proximity_Parent
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
