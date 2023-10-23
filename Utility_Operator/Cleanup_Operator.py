import bpy
from bpy_extras import anim_utils
import os
from Bonera_Toolkit import Utility_Functions



class BONERA_Remove_Custom_Property(bpy.types.Operator):
    """Remove Custom Property"""
    bl_idname = "bonera.cleanup_remove_custom_property"
    bl_label = "Remove Custom Property"
    bl_options = {'UNDO', 'REGISTER'}

    armature: bpy.props.BoolProperty(default=True, name="Armature")
    object: bpy.props.BoolProperty(default=True, name="Object")
    posebone: bpy.props.BoolProperty(default=True, name="Pose Bone")
    editbone: bpy.props.BoolProperty(default=True, name="Edit Bone")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        object = context.object

        if object:

            if self.object:
                # if object.get("_RNA_UI"):
                #     for property in object["_RNA_UI"]:
                #         del object[property]

                object.id_properties_clear()







            if object.type == "ARMATURE":

                if self.armature:
                    object.data.id_properties_clear()
                    # if object.data.get("_RNA_UI"):
                    #     for property in object.data["_RNA_UI"]:
                    #         del object.data[property]

                if self.posebone:
                    Pose_Bones = object.pose.bones
                    for bone in Pose_Bones:
                        bone.id_properties_clear()
                        # if bone.get("_RNA_UI"):
                        #     for property in bone["_RNA_UI"]:
                        #         del bone[property]

                if self.editbone:
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    object.select_set(True)
                    context.view_layer.objects.active = object

                    bpy.ops.object.mode_set(mode = 'EDIT')
                    Edit_Bones = object.data.edit_bones
                    for bone in Edit_Bones:
                        bone.id_properties_clear()
                        # if bone.get("_RNA_UI"):
                        #     for property in bone["_RNA_UI"]:
                        #         del bone[property]
                    bpy.ops.object.mode_set(mode = 'OBJECT')

        context.view_layer.update()
        Utility_Functions.update_UI()
        return {'FINISHED'}

class BONERA_Remove_Animation_Data(bpy.types.Operator):
    """Remove Animation Data"""
    bl_idname = "bonera.cleanup_remove_animation_data"
    bl_label = "Remove Animation Data and Drivers"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        object = context.object

        if object:
            object.animation_data_clear()
            object.data.animation_data_clear()


        return {'FINISHED'}

class BONERA_Remove_Non_Deform_Bone(bpy.types.Operator):
    """Remove Non Deform Bone"""
    bl_idname = "bonera.cleanup_remove_non_deform_bone"
    bl_label = "Remove Non Deform Bone"
    bl_options = {'UNDO', 'REGISTER'}

    move_bone_to_layer_1: bpy.props.BoolProperty(default=False)
    remove_constraints: bpy.props.BoolProperty(default=True)
    unlock_transform: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "move_bone_to_layer_1", text="Move Bones to Layer 1")
        layout.prop(self, "remove_constraints", text="Clear Constraints")
        layout.prop(self, "unlock_transform", text="Unlock Transform")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):





        if context.object:
            if context.object.type == "ARMATURE":
                object = context.object

                bpy.ops.object.select_all(action='DESELECT')
                object.select_set(True)
                context.view_layer.objects.active = object


                bpy.ops.object.mode_set(mode = 'EDIT')
                Edit_Bones = object.data.edit_bones
                for bone in Edit_Bones:

                    if self.move_bone_to_layer_1:
                        for i, layer in enumerate(bone.layers):
                            if i == 0:
                                bone.layers[i] = True
                            else:
                                bone.layers[i] = False

                    if not bone.use_deform:
                        Edit_Bones.remove(bone)







                bpy.ops.object.mode_set(mode = 'OBJECT')

                # Pose_Bones = object.pose.bones
                #
                # for bone in Pose_Bones:
                #     if self.move_bone_to_layer_1:
                #         for i, layer in enumerate(bone.layers):
                #             if i == 0:
                #                 bone.layers[i] = True
                #             else:
                #                 bone.layers[i] = False


                if self.move_bone_to_layer_1:
                    for i, layer in enumerate(object.data.layers):
                        if i == 0:
                            object.data.layers[i] = True
                        else:
                            object.data.layers[i] = False






                Pose_Bones = object.pose.bones

                for bone in Pose_Bones:

                    if self.unlock_transform:
                        bone.lock_location[0] = False
                        bone.lock_location[1] = False
                        bone.lock_location[2] = False

                        bone.lock_scale[0] = False
                        bone.lock_scale[1] = False
                        bone.lock_scale[2] = False

                        bone.lock_rotation_w = False
                        bone.lock_rotation[0] = False
                        bone.lock_rotation[1] = False
                        bone.lock_rotation[2] = False

                    if self.remove_constraints:
                        for constraint in bone.constraints:
                            bone.constraints.remove(constraint)


        return {'FINISHED'}

class BONERA_Remove_Bone_Shape(bpy.types.Operator):
    """Remove Bone Shape"""
    bl_idname = "bonera.cleanup_remove_bone_shape"
    bl_label = "Remove Bone Shape"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        if context.object:
            if context.object.type == "ARMATURE":
                Pose_Bones = context.object.pose.bones
                for bone in Pose_Bones:
                    bone.custom_shape = None


        return {'FINISHED'}


classes = [BONERA_Remove_Non_Deform_Bone, BONERA_Remove_Custom_Property, BONERA_Remove_Animation_Data, BONERA_Remove_Bone_Shape]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
