
import bpy
from bpy_extras import anim_utils
import os
from Bonera_Toolkit import Utility_Functions





class BONERA_Join_And_Parent_Selected_To_Bone_By_Armature_Name(bpy.types.Operator):
    """Join Selected Armature And Parent To Bone By Armature Name"""
    bl_idname = "bonera.join_and_parent_selected_bone_by_armature_name"
    bl_label = "Join And Parent Selected Bone By Armature Name"
    bl_options = {'UNDO', 'REGISTER'}


    def execute(self, context):

        master_armature = context.object

        if master_armature:
            if master_armature.type == "ARMATURE":

                for bone in master_armature.data.bones:
                    bone.Bonera_Util_Property.parent_target = ""


                objects = [obj for obj in context.selected_objects if not obj == master_armature and obj.type == "ARMATURE"]

                for object in objects:
                    for bone in object.data.bones:
                        bone.Bonera_Util_Property.parent_target = object.name

                bpy.ops.object.join()

                Utility_Functions.object_switch_mode(master_armature, "EDIT")

                for edit_bone in master_armature.data.edit_bones:

                    bone = master_armature.data.bones.get(edit_bone.name)

                    if bone.parent == None:

                        if not bone.Bonera_Util_Property.parent_target == "" or bone.Bonera_Util_Property is not None:
                            parent_bone = master_armature.data.edit_bones.get(bone.Bonera_Util_Property.parent_target)
                            if parent_bone:

                                edit_bone.parent = parent_bone


                for bone in master_armature.data.bones:
                    bone.Bonera_Util_Property.parent_target = ""


                Utility_Functions.object_switch_mode(master_armature, "OBJECT")

                # for object in objects:

                #     override = context.copy()
                #     override["object"] = master_armature
                #     override["active_object"] = master_armature
                #     override["selected_objects"] = [object, master_armature]
                #     with context.temp_override(**override):
                #         bpy.ops.object.join()



        Utility_Functions.update_UI()
        return {'FINISHED'}


classes = [BONERA_Join_And_Parent_Selected_To_Bone_By_Armature_Name]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
