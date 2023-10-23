import bpy
from .. import Utility_Functions


class BONERA_Open_Bone_Shape_Folder(bpy.types.Operator):
    """Open Bone Shape Folder"""
    bl_idname = "bonera.open_bone_shape_folder"
    bl_label = "Open Bone Shape Folder"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        Utility_Functions.open_file(Utility_Functions.get_bone_shape_directory())

        return {'FINISHED'}






classes = [BONERA_Open_Bone_Shape_Folder]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
