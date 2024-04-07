import bpy
import pathlib
from .. import Utility_Functions
import mathutils
import bmesh
import pathlib
import math

import bpy.utils.previews


OPERATOR_POLL_CONTEXT = ["OBJECT", "POSE"]
widgets_lists = []



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



ENUM_Position = [("CURSOR","Cursor","Cursor"),("CENTER","Center","Center")]

Widget_Catagories = None

def reload_widget_categories():
    global Widget_Catagories

    Widget_Catagories = Utility_Functions.get_bone_shape_catagories()

def ENUM_Bone_Shape_Catagory(self, context):

    items = []

    for catagory in Widget_Catagories:
        item = (catagory, catagory, catagory)
        items.append(item)


    if len(items) == 0:
        item = ("NONE", "None", "None")
        items.append(item)

    return items

def ENUM_Bone_Shape_File(self, context):

    items = []

    catagory = Widget_Catagories[self.bone_shape_catagory]
    bone_shapes = catagory["bone_shapes"]

    for i, bone_shape in enumerate(bone_shapes):
        thumb = bone_shape["thumb"]
        item = (bone_shape["path"], pathlib.Path(bone_shape["name"]).stem, bone_shape["name"], thumb.icon_id, i)

        items.append(item)

    if len(items) == 0:
        item = ("NONE", "None", "None")
        items.append(item)

    return items



def reset_property(self, context):

    if self.reset_transform:
        self.offset = (0, 0, 0)
        self.rotate = (0, 0, 0)
        self.scale = (1, 1, 1)
        self.reset_transform = False


class BONERA_Reload_Widget_Categories(bpy.types.Operator):
    """Operator to reload widget categories"""
    bl_idname = "bonera.reload_bone_shapes"
    bl_label = "Reload Bone Shapes"

    def execute(self, context):
        # Call the function to reload widget categories
        reload_widget_categories()

        self.report({'INFO'}, "Bone shapes reloaded successfully")

        return {'FINISHED'}

# class BONAD_Add_Bone_Shapes(bpy.types.Operator):
class BONERA_Add_Bone_Shapes(bpy.types.Operator):
    """Add / Apply Bone Shapes
    Pose: Apply Bone Shape to Active Bone
    Object: Add Bone Shape to Scene"""
    bl_idname = "bonera.add_bone_shape"
    bl_label = "Add Bone Shape"
    bl_options = {'UNDO', 'REGISTER'}

    name: bpy.props.StringProperty(default="Widgets")

    bone_shape_catagory: bpy.props.EnumProperty(items = ENUM_Bone_Shape_Catagory)
    bone_shape_file: bpy.props.EnumProperty(items = ENUM_Bone_Shape_File)

    position: bpy.props.EnumProperty(items = ENUM_Position)

    use_custom_shape_bone_size: bpy.props.BoolProperty(default=True)
    unlink_from_scene: bpy.props.BoolProperty(default=False)
    offset: bpy.props.FloatVectorProperty(default=(0, 0, 0))
    rotate: bpy.props.FloatVectorProperty(default=(0, 0, 0), subtype="EULER")
    scale: bpy.props.FloatVectorProperty(default=(1, 1, 1))

    reset_transform: bpy.props.BoolProperty(default=False, update = reset_property)

    SHOW_Collection: bpy.props.BoolProperty(default=False)

    Use_Collection: bpy.props.BoolProperty(default=True)
    Collection_Name: bpy.props.StringProperty(default="WGT_Collection")
    show_wire: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):

        if context.mode in OPERATOR_POLL_CONTEXT:
            return True

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout
        if context.mode == "OBJECT":
            layout.prop(self, "name", text="Name")
        layout.prop(self, "bone_shape_catagory", text="Category")
        layout.template_icon_view(self, "bone_shape_file", show_labels=False, scale=4.0, scale_popup = 4.0)

        if context.mode == "OBJECT":
            layout.prop(self, "position", expand=True)

        if context.mode == "POSE":

            layout.prop(self, "use_custom_shape_bone_size", text="Scale to Bone Length")
            layout.prop(self, "show_wire", text="Wireframe")


            layout.prop(self, "offset", text="Offset")
            layout.prop(self, "rotate", text="Rotation")
            layout.prop(self, "scale", text="Scale")
            layout.prop(self, "reset_transform", text="Reset Transform", icon="FILE_REFRESH")

        if Utility_Functions.draw_subpanel(self, self.SHOW_Collection, "SHOW_Collection", "Collections", layout):

            layout.prop(self, "Use_Collection", text="Use Collection")

            if self.Use_Collection:
                layout.prop(self, "Collection_Name", text="Collection")


    def execute(self, context):

        mode = context.mode
        context.view_layer.update()

        if mode == "OBJECT":

            objects = Utility_Functions.append_bone_shape(self.bone_shape_file)

            for object in objects:

                object.name = self.name

                if self.Use_Collection:
                    WGT_Collection(object, collection_name = self.Collection_Name)

                if self.position == "CENTER":
                    object.location = (0, 0, 0)

                if self.position == "CURSOR":
                    object.location = context.scene.cursor.location.xyz

                context.view_layer.objects.active = object

        if mode == "POSE":

            armature_objects = [obj for obj in context.objects_in_mode if obj.type == "ARMATURE"]

            for armature_object in armature_objects:
                for pose_bone in armature_object.pose.bones:

                    if pose_bone.bone.select:
                        objects = Utility_Functions.append_bone_shape(self.bone_shape_file)

                        for object in objects:
                            if self.Use_Collection:
                                WGT_Collection(object, collection_name = self.Collection_Name)

                                object.matrix_world = pose_bone.matrix

                                object.name = "WGT_" + pose_bone.name

                                pose_bone.custom_shape = object
                                pose_bone.use_custom_shape_bone_size = self.use_custom_shape_bone_size
                                pose_bone.bone.show_wire = self.show_wire

                                pose_bone.custom_shape_scale_xyz = self.scale
                                pose_bone.custom_shape_translation = self.offset
                                pose_bone.custom_shape_rotation_euler = self.rotate




                                object.matrix_world = pose_bone.id_data.matrix_world @ object.matrix_world

                                if self.use_custom_shape_bone_size:
                                    Bone_Length = mathutils.Vector((pose_bone.length, pose_bone.length, pose_bone.length))
                                else:
                                    Bone_Length = mathutils.Vector((1, 1, 1))


                                context.view_layer.update()

                                object.matrix_world = object.matrix_world @ mathutils.Matrix.LocRotScale(self.offset, mathutils.Euler(self.rotate), Bone_Length*mathutils.Vector(self.scale))



        context.view_layer.update()


        return {'FINISHED'}


classes = [BONERA_Add_Bone_Shapes, BONERA_Reload_Widget_Categories]

def register():

    reload_widget_categories()

    for cls in classes:
        bpy.utils.register_class(cls)



def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
