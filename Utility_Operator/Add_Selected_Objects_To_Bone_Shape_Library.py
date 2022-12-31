import bpy
from Bonera_Toolkit import Utility_Functions

import os
import pathlib


import mathutils
import math
import numpy


def midpoint(coordinates, mode):

    if len(coordinates) > 0:

        if mode == "BOUNDING_BOX":

            x= []
            y= []
            z= []

            for coordinate in coordinates:
                x.append(coordinate[0])
                y.append(coordinate[1])
                z.append(coordinate[2])

            range_x = (max(x), min(x))
            range_y = (max(y), min(y))
            range_z = (max(z), min(z))

            bounding_box_coordinate = []

            for a in range_x:
                for b in range_y:
                    for c in range_z:
                        bounding_box_coordinate.append((a, b, c))

            return mathutils.Vector(numpy.array(bounding_box_coordinate).mean(axis=0))

        if mode == "CENTER":
            return mathutils.Vector(numpy.array(coordinates).mean(axis=0))
    else:
        return None


class BONERA_Add_Selected_Objects_To_Bone_Shape_Library(bpy.types.Operator):
    """Add Selected Objects to Bone Shape Library"""
    bl_idname = "bonera.add_selected_objects_to_bone_shape_library"
    bl_label = "Add Selected Objects to Bone Shape Library"

    Catagory: bpy.props.StringProperty(default="Custom")

    @classmethod
    def poll(cls, context):
        if context.mode == "OBJECT":
            return True
        else:
            return False

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout
        layout.label(text="Make Sure to Save Your File First", icon="INFO")
        layout.label(text="Backup this File before Proceeding", icon="INFO")
        layout.prop(self, "Catagory")


    def execute(self, context):

        thickness = 0.01
        lens = 100
        standardize_thumbnail_size = True
        color = [0.000000, 1.000000, 0.000000]

        Bone_Shape_Directory = Utility_Functions.get_bone_shape_directory()
        Addon_Directory = Utility_Functions.get_addon_directory()
        current_file_path = str(bpy.data.filepath)


        bone_shape_save_path = pathlib.Path(os.path.join(Bone_Shape_Directory, self.Catagory))
        template_file = str(pathlib.Path(os.path.join(Addon_Directory, "Template_File.blend")))

        object_names = [object.name for object in context.selected_objects if object.type == "MESH"]

        if current_file_path:

            if os.path.isfile(template_file):

                bpy.ops.wm.open_mainfile(filepath=template_file)

                widget_display_node_group = bpy.data.node_groups.get("Widget_Display")


                if widget_display_node_group:

                    for object_name in object_names:


                        for obj in bpy.data.objects:
                            bpy.data.objects.remove(bpy.data.objects[0])



                        with bpy.data.libraries.load(str(current_file_path)) as (data_from, data_to):

                            for obj in data_from.objects:
                                if obj == object_name:
                                    data_to.objects = [obj]

                        object = bpy.data.objects.get(object_name)
                        if object:
                            bpy.context.collection.objects.link(object)


                            object.location.x = 0
                            object.location.y = 0
                            object.location.z = 0

                            object.name = "Widget"

                            solid = not len(object.data.polygons) == 0

                            if not solid:
                                thumb_object = object.copy()
                                thumb_data = object.data.copy()
                                thumb_object.data = thumb_data

                                bpy.context.collection.objects.link(thumb_object)
                                thumb_object.name = "Widget_Thumbnail_Mesh"
                                thumb_object.modifiers.clear()
                                modifier = thumb_object.modifiers.new("Widget_Display", type="NODES")
                                modifier.node_group = widget_display_node_group
                                modifier["Input_2"] = thickness

                            else:
                                thumb_object = object



                            camera_data  = bpy.data.cameras.new("Camera")
                            camera_object = bpy.data.objects.new("Camera", camera_data)
                            camera_object.matrix_world = thumb_object.matrix_world

                            coordinates = [vertex.co for vertex in thumb_object.data.vertices]
                            object_midpoint = midpoint(coordinates, "BOUNDING_BOX")
                            context.collection.objects.link(camera_object)
                            context.view_layer.update()

                            camera_object.location = thumb_object.matrix_world @ object_midpoint
                            camera_object.rotation_euler.x += math.radians(45)
                            camera_object.rotation_euler.z -= math.radians(180)
                            camera_object.rotation_euler.z += math.radians(45)

                            context.view_layer.update()
                            thumb_object.select_set(True)
                            context.view_layer.objects.active = thumb_object




                            if standardize_thumbnail_size:
                                dim = max(thumb_object.dimensions.x, thumb_object.dimensions.y, thumb_object.dimensions.z)
                                rate = 1/dim
                                resize_scale = (thumb_object.scale.x * rate, thumb_object.scale.y * rate, thumb_object.scale.z * rate)
                                thumb_object.scale = resize_scale
                                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                            camera_object.location = camera_object.matrix_world @ mathutils.Vector((0, 0, 0.5))
                            camera_object.data.lens=lens

                            # context.scene.camera = camera_object

                            for screen in bpy.data.screens:
                                for area in screen.areas:
                                    if area.type == "VIEW_3D":
                                        for space in area.spaces:

                                            if solid:
                                                space.shading.light = 'STUDIO'
                                                space.shading.single_color = (1, 1, 1)
                                            else:
                                                space.shading.light = 'FLAT'
                                                space.shading.single_color = color

                                            space.region_3d.view_perspective = "CAMERA"
                            #                 bpy.ops.view3d.camera_to_view_selected()
                            camera_object.location = camera_object.matrix_world @ mathutils.Vector((0, 0, 0.5))
                            context.scene.render.resolution_x = 1080
                            context.scene.render.resolution_y = 1080
                            # context.scene.camera = camera_object
                            bone_shape_save_path.mkdir(parents=True, exist_ok=True)

                            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(str(bone_shape_save_path), object_name +".blend"))
                            # bpy.ops.wm.open_mainfile(filepath=template_file)
                bpy.ops.wm.open_mainfile(filepath=current_file_path)

        else:
            self.report({"INFO"}, "Please Save Your File First!")


        #


        return {'FINISHED'}



classes = [BONERA_Add_Selected_Objects_To_Bone_Shape_Library]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
