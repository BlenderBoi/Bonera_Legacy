import bpy
import pathlib
from .. import Utility_Functions
import mathutils
import bmesh

import re

import math
OPERATOR_POLL_CONTEXT = ["POSE"]
widgets_lists = []

Widget_Filepath = Utility_Functions.get_widgets_filepath()


#Move to Collection
#Already in Collection Error

def WGT_Collection(object, collection_name = "WGT_Collection"):

    for col in object.users_collection:
        col.objects.unlink(object)

    if bpy.data.collections.get(collection_name):
        tiles_collection =  bpy.data.collections[collection_name]
    else:
        tiles_collection =  bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(tiles_collection)

    if tiles_collection:
        if not tiles_collection.objects.get(object.name):
            tiles_collection.objects.link(object)

    # tiles_collection.hide_viewport = True
    tiles_collection.hide_render = True

    return tiles_collection


def load_widgets():

    with bpy.data.libraries.load(str(Widget_Filepath)) as (data_from, data_to):
        for object in data_from.objects:
            widgets_lists.append(object)


def ENUM_Widgets(self, context):

    items = []

    for widget in widgets_lists:
        item = (widget, widget.replace("WGT-", ""), widget)
        items.append(item)

    if len(items) == 0:
        item = ("None", "None", "None")
        items.append(item)


    return items


#Rename Widgets
#Front

# for key, value in FRONT_Side_Separator_List.items():
#     print(key + " | " + value)
#
# for key, value in BACK_Side_Separator_List.items():
#     print(key + " | " + value)

Side_List = [["l", "r"], ["L","R"], ["left", "right"], ["Left","Right"], ["LEFT", "RIGHT"]]
Separator_List = [".", "_", "-"]

ENUM_Position = [("CURSOR","Cursor","Cursor"),("CENTER","Center","Center")]
ENUM_Direction = [("LEFT_TO_RIGHT","Left To Right","Left To Right"),("RIGHT_TO_LEFT","Right To Left","Right to Left")]

# class BONAD_Add_Bone_Shapes(bpy.types.Operator):
class BONERA_Mirror_Bone_Shapes(bpy.types.Operator):
    """Mirror Bone Shapes
    Pose Mode Only"""
    bl_idname = "bonera.mirror_bone_shape"
    bl_label = "Mirror Bone Shape"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):

        if context.mode in OPERATOR_POLL_CONTEXT:
            return True

    def execute(self, context):

        mode = context.mode
        context.view_layer.update()

        objects = []

        if mode in ["POSE"]:
            objects = [object for object in context.objects_in_mode if object.type == "ARMATURE"]


        for object in objects:

            bones = object.pose.bones


            for bone in bones:
                bone_name = bone.name

                if bone.bone.select:



                    flipped_bone = None

                    for side_item in Side_List:

                        for separator in Separator_List:

                            left = side_item[0]
                            right = side_item[1]

                            append_left =  left + separator
                            append_right = right + separator

                            prepend_left = separator + left
                            prepend_right = separator + right



                            if bone_name.startswith(append_left):
                                expression = '^' + append_left
                                pattern = re.compile(expression)
                                matches = pattern.sub(append_right, bone_name)
                                flipped_bone_name = matches

                                flipped_bone = bones.get(flipped_bone_name)
                                break



                            elif bone_name.endswith(prepend_left):
                                expression = prepend_left+'$'
                                pattern = re.compile(expression)
                                matches = pattern.sub(prepend_right, bone_name)
                                flipped_bone_name = matches

                                flipped_bone = bones.get(flipped_bone_name)
                                break


                            if bone_name.startswith(append_right):
                                expression = '^' + append_right
                                pattern = re.compile(expression)
                                matches = pattern.sub(append_left, bone_name)
                                flipped_bone_name = matches

                                flipped_bone = bones.get(flipped_bone_name)
                                break

                            elif bone_name.endswith(prepend_right):
                                expression = prepend_right+'$'
                                pattern = re.compile(expression)
                                matches = pattern.sub(prepend_left, bone_name)
                                flipped_bone_name = matches

                                flipped_bone = bones.get(flipped_bone_name)
                                break


                        if flipped_bone:

                            flipped_bone.custom_shape = bone.custom_shape
                            flipped_bone.custom_shape_scale_xyz = bone.custom_shape_scale_xyz
                            flipped_bone.custom_shape_translation = bone.custom_shape_translation
                            flipped_bone.custom_shape_rotation_euler = bone.custom_shape_rotation_euler
                            flipped_bone.use_custom_shape_bone_size = bone.use_custom_shape_bone_size

                            flipped_bone.custom_shape_translation[0] = -bone.custom_shape_translation[0]
                            flipped_bone.custom_shape_rotation_euler[1] = -bone.custom_shape_rotation_euler[1]
                            flipped_bone.custom_shape_rotation_euler[2] = -bone.custom_shape_rotation_euler[2]

                            # if bone.custom_shape:
                            #     flipped_bone.custom_shape = bone.custom_shape
                            # elif flipped_bone.custom_shape:
                            #     bone.custom_shape = flipped_bone.custom_shape
                            # else:
                            #     flipped_bone.custom_shape = bone.custom_shape

                            break


        context.view_layer.update()
        if mode == "POSE":
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        if mode == "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


classes = [BONERA_Mirror_Bone_Shapes]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)



def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
