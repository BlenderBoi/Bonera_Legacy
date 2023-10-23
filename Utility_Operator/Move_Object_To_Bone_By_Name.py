
import bpy
from bpy_extras import anim_utils
import os
from .. import Utility_Functions





class BONERA_Move_Object_To_Bone_By_Name(bpy.types.Operator):
    """Move Object To Bone By Name"""
    bl_idname = "bonera.move_object_to_bone_by_name"
    bl_label = "Move Object to Bone By Name"
    bl_options = {'UNDO', 'REGISTER'}

    only_location: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "only_location", text="Only Location")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        master_armature = context.object

        if master_armature:
            if master_armature.type == "ARMATURE":


                objects = [obj for obj in context.selected_objects if not obj == master_armature]

                for object in objects:

                    bone = master_armature.pose.bones.get(object.name)

                    if bone:
                        if self.only_location:
                            object.location = master_armature.matrix_world @ bone.head
                        else:
                            object.matrix_world = master_armature.matrix_world @ bone.matrix

        Utility_Functions.update_UI()
        return {'FINISHED'}


classes = [BONERA_Move_Object_To_Bone_By_Name]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
