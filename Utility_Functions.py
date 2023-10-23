import bpy
import os
import pathlib
import numpy

import mathutils
import platform
import subprocess

import math

script_file = os.path.realpath(__file__)
addon_directory = os.path.dirname(script_file)
addon_name = os.path.basename(addon_directory)

SEPARATOR_List = [".", "_", "-"]
Side_List = {"l": "r", "L":"R", "left": "right", "Left":"Right", "LEFT": "RIGHT"}

FRONT_Side_Separator_List = {}
BACK_Side_Separator_List = {}

for key, value in Side_List.items():

    for separator in SEPARATOR_List:
        FRONT_Side_Separator_List[key+separator] = value+separator
        BACK_Side_Separator_List[separator+key] = separator+value





def Parent_Counter(self, Bone):

    Checker = Bone.parent
    if Checker:
        self.Counter += 1
        Parent_Counter(self, Checker)



def Find_Chain_Root(Chain_Length, Bone):

    bone_chain = []

    bone_chain.append(Bone)

    parent_finder = Bone.parent

    if parent_finder:
        bone_chain.append(parent_finder)
        Loop_Amount = Chain_Length-2

        if Loop_Amount > 0:
            for count in range(Loop_Amount):
                if parent_finder:
                    parent_finder = parent_finder.parent
                    if parent_finder:
                        bone_chain.append(parent_finder)
    else:
        bone_chain.append(None)

    return bone_chain



def Align_Bone_Roll(object, bone, target):


    bone = object.data.edit_bones.get(bone.name)

    bpy.ops.armature.select_all(action='DESELECT')

    cursor_location = bpy.context.scene.cursor.location.copy()

    bpy.context.scene.cursor.location = object.matrix_world @ target

    bone.select = True
    bpy.ops.armature.calculate_roll(type='CURSOR')
    bone.roll -= math.radians(90)

    bpy.context.scene.cursor.location = cursor_location

    bpy.ops.armature.select_all(action='DESELECT')


def Align_Bones_Roll(object, bones, target):

    bone_selection = [select_bone for select_bone in object.data.edit_bones if select_bone.select]

    for bone in bones:
        Align_Bone_Roll(object, bone, target)
        bpy.ops.armature.select_all(action='DESELECT')

    for select_bone in bone_selection:
        select_bone.select = True

def Get_Pole_Angle(object, bone, target):

    original_roll = bone.roll

    Align_Bone_Roll(object, bone, target)
    bpy.ops.armature.select_all(action='DESELECT')

    adjusted_roll = bone.roll

    bone.roll = original_roll

    pole_angle = original_roll - adjusted_roll

    if pole_angle > math.radians(180):
        pole_angle = pole_angle - math.radians(360)

    return pole_angle



def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

class Side_Flipper:

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def flip_name(self, name):

        flipped_name = None

        if self.left in name:
            flipped_name = name.replace(self.left, self.right)
        elif self.right in name:
            flipped_name = name.replace(self.right, self.left)

        return flipped_name

    def get_flipped_bone(self, bones, bone):

        flipped_bone = None
        if bones:
            if bone:
                flipped_bone_name = self.flip_name(bone.name)
                if flipped_bone_name:
                    flipped_bone = bones.get(flipped_bone_name)

        return flipped_bone



def curve_to_mesh(object, resolution=None):

    offset = object.data.offset
    extrude = object.data.extrude
    taper_object = object.data.taper_object
    taper_radius_mode = object.data.taper_radius_mode
    bevel_mode = object.data.bevel_mode
    bevel_depth = object.data.bevel_depth
    use_fill_caps = object.data.use_fill_caps
    resolution_u = object.data.resolution_u

    object.data.offset = 0
    object.data.extrude = 0
    object.data.taper_object = None
    object.data.taper_radius_mode = "OVERRIDE"
    object.data.bevel_mode = "ROUND"
    object.data.bevel_depth = 0
    object.data.use_fill_caps = False

    if resolution:
        object.data.resolution_u = resolution

    deg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(object.evaluated_get(deg), depsgraph=deg)

    object.data.offset = offset
    object.data.extrude = extrude
    object.data.taper_object = taper_object
    object.data.taper_radius_mode = taper_radius_mode
    object.data.bevel_mode = bevel_mode
    object.data.bevel_depth = bevel_depth
    object.data.use_fill_caps = use_fill_caps
    object.data.resolution_u = resolution_u





    new_obj = bpy.data.objects.new(object.name + "_mesh", me)
    bpy.context.collection.objects.link(new_obj)

    new_obj.matrix_world = object.matrix_world

    return new_obj

def get_addon_preferences():
    addon_preferences = bpy.context.preferences.addons[addon_name].preferences
    return addon_preferences

def get_addon_name():
    return addon_name

def get_addon_directory():
    return addon_directory

def update_UI():
    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()

def draw_subpanel(self, boolean, property, label, layout):

    if boolean:
        ICON = "TRIA_DOWN"
    else:
        ICON = "TRIA_RIGHT"

    row = layout.row(align=True)
    row.alignment = "LEFT"
    row.prop(self, property, text=label, emboss=False, icon=ICON)

    return boolean


def draw_subpanel_bool(source, boolean, property, bool_source, bool_prop, label, layout):

    if boolean:
        ICON = "TRIA_DOWN"
    else:
        ICON = "TRIA_RIGHT"

    row = layout.row(align=True)
    row.alignment = "LEFT"

    row.prop(source, property, text="", emboss=False, icon=ICON)
    row.prop(bool_source, bool_prop, text="")
    row.prop(source, property, text=label, emboss=False, icon=ICON)

    return boolean



def get_bounding_box(object):

    bbox_corners = [object.matrix_world * mathutils.Vector(corner) for corner in object.bound_box]

    return bbox_corners


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





def object_switch_mode(object, mode):

    bpy.context.view_layer.update()

    Previous_Mode = object.mode

    if not object.visible_get():

        if not bpy.context.collection.objects.get(object.name):

            bpy.context.collection.objects.link(object)



    object.hide_viewport = False
    object.hide_set(False)

    object.hide_select = False

    if object.visible_get():

        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.mode_set(mode=mode, toggle=False)

        return Previous_Mode



def create_bone(armature, name, head, tail, deform, Flip_Bone = False):

    bone = armature.data.edit_bones.new(name)

    if Flip_Bone:
        bone.head = tail
        bone.tail = head
    else:
        bone.head = head
        bone.tail = tail

    bone.use_deform = deform

    return bone

def get_object_center(object, mode):

    if mode == "ORIGIN":
        # return object.matrix_world.inverted() @ object.location
        return object.matrix_world.inverted() @ object.matrix_world.to_translation()

    if mode in ["CENTER", "BOUNDING_BOX"]:

        if not object.type in ["MESH","CURVE" , "ARMATURE"]:
            # return object.matrix_world.inverted() @ object.location
            return object.matrix_world.inverted() @ object.matrix_world.to_translation()

        if object.type == "MESH":
            # create_lists = [object.matrix_world @ vert.co for vert in object.data.vertices]
            create_lists = [vert.co for vert in object.data.vertices]

        if object.type == "CURVE":

            create_lists = []

            for spline in object.data.splines:

                for point in spline.points:
                    # create_lists.append(object.matrix_world @ point.co)
                    create_lists.append(point.co.xyz)

                for bezier_point in spline.bezier_points:
                    # create_lists.append(object.matrix_world @ bezier_point.co)
                    create_lists.append(bezier_point.co.xyz)

        if object.type == "ARMATURE":

            create_lists = []

            for bone in object.data.bones:
                # create_lists.append(object.matrix_world @ bone.head)
                # create_lists.append(object.matrix_world @ bone.tail)

                create_lists.append(bone.head)
                create_lists.append(bone.tail)

        if mode == "CENTER":
            return midpoint(create_lists, "CENTER")

        if mode == "BOUNDING_BOX":
            return midpoint(create_lists, "BOUNDING_BOX")


def Normal_To_Offset(object, location, normal, offset):

    mw = object.matrix_world.copy()

    o = location
    axis_src = normal
    axis_dst = mathutils.Vector((0, 0, 1))

    matrix_rotate = mw.to_3x3()
    matrix_rotate = matrix_rotate @ axis_src.rotation_difference(axis_dst).to_matrix().inverted()
    matrix_translation = mathutils.Matrix.Translation(mw @ o)

    Normal_Matrix = matrix_translation @ matrix_rotate.to_4x4() @ mathutils.Vector(offset)
    Normal_Offset = object.matrix_world.inverted() @ Normal_Matrix

    return Normal_Offset

def Average_Normals(Normals):
    average_normals = mathutils.Vector(numpy.sum(Normals, axis=0) / len(Normals))
    return average_normals

def Add_Weight(object, bone_name, indices):

    Vertex_Group = object.vertex_groups.get(bone_name)

    if Vertex_Group == None:
        Vertex_Group = object.vertex_groups.new( name = bone_name )



    Vertex_Group.add(indices, 1.0, 'REPLACE' )

    return Vertex_Group

def Add_Armature_Modifier(object, Armature, name="Armature"):

    for modifier in object.modifiers:
        if modifier.type == "ARMATURE":
            if modifier.object == Armature:
                return modifier

    modifier = object.modifiers.new(type="ARMATURE", name=name)
    modifier.object = Armature

    return modifier

def Hook_Vertex_Bone(object, armature, vertex_indices, bone_name, name="Hook"):

    modifier = object.modifiers.new(type="HOOK", name=name)
    modifier.object = armature
    modifier.subtarget = bone_name
    modifier.vertex_indices_set(vertex_indices)

    return modifier

def get_object_indices(object):

    if object.type == "MESH":
        indices = [vertex.index for vertex in object.data.vertices]
        return indices

    else:
        return None

def check_bone_select(bone, mode):

    if mode == "EDIT_ARMATURE":
        return bone.select

    if mode == "POSE":
        return bone.bone.select


def Create_Armature(name):

    armature = bpy.data.armatures.new(name)
    object = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(object)

    return object

def Create_Empty(name):

    object = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(object)

    return object

def Hook_Vertex_Empty(object, empty, vertex_indices, name="Hook"):

    modifier = object.modifiers.new(type="HOOK", name=name)
    modifier.object = empty
    modifier.vertex_indices_set(vertex_indices)

    return modifier

def Normal_To_Orientation(object, location, normal):

    mw = object.matrix_world.copy()

    o = location
    axis_src = normal
    axis_dst = mathutils.Vector((0, 0, 1))

    matrix_rotate = mw.to_3x3()
    matrix_rotate = matrix_rotate @ axis_src.rotation_difference(axis_dst).to_matrix().inverted()
    matrix_translation = mathutils.Matrix.Translation(mw @ o)

    Normal_Matrix = matrix_translation @ matrix_rotate.to_4x4()

    return Normal_Matrix

def append_bone_shape(path):

    objects = []

    if path != "None":
        path = path
        section = "/Object/"
        directory = path + section
        filename = "Widget"

        bpy.ops.wm.append(filename=filename, directory=directory)

        objects = [object for object in bpy.context.selected_objects]

    return objects


def get_widgets_filepath():
    addon_dir = pathlib.Path(addon_directory)
    widget_file = pathlib.Path("{}/Widgets/Widget.blend".format(addon_dir))

    return widget_file

def get_bone_shape_directory():
    addon_dir = addon_directory
    bone_shapes_directory = os.path.join(addon_dir, "Widgets")
    return bone_shapes_directory


preview_collections = {}

def get_bone_shape_catagories():


    pcoll = bpy.utils.previews.new()
    pcoll.my_previews = ()
    preview_collections["main"] = pcoll


    bone_shapes_directory = get_bone_shape_directory()
    bone_shapes_catagories = {}

    for dir in os.listdir(bone_shapes_directory):
        catagory_path = os.path.join(bone_shapes_directory, dir)

        if os.path.isdir(catagory_path):
            bone_shapes = []

            for bone_shape_name in os.listdir(catagory_path):

                bone_shape_path = os.path.join(catagory_path, bone_shape_name)

                if os.path.isfile(bone_shape_path) and bone_shape_path.endswith(".blend"):

                    thumb = pcoll.load(bone_shape_path, bone_shape_path, "BLEND")

                    bone_shape = {"name": bone_shape_name, "path": bone_shape_path, "thumb": thumb}
                    bone_shapes.append(bone_shape)

            bone_shapes_catagory = {"name": dir, "path": catagory_path, "bone_shapes": bone_shapes}
            bone_shapes_catagories[dir] = bone_shapes_catagory

    return bone_shapes_catagories

def Format_String(Format, Dictionary):

    for key, item in Dictionary.items():
        Format = Format.replace(key, item)

    return Format



def subdivide_bone(object, bone, amount):

    edit_bones = object.data.edit_bones

    twist_bones = []

    for a in range(amount):
        newbone_name = "TWIST_" + str(a) + "_" + bone.name
        newbone = create_bone(object, newbone_name, bone.head, bone.tail, bone.use_deform, Flip_Bone = False)
        newbone.roll = bone.roll

        vector = bone.vector

        newbone.length = newbone.length / amount
        newbone.head += bone.vector/amount * a
        newbone.tail += bone.vector/amount * a

        if len(twist_bones) > 0:
            newbone.parent = twist_bones[-1]

        twist_bones.append(newbone)

    return twist_bones

def get_bone_layers(layer):
    layers = [False for layer in range(32)]
    layers[layer] = True
    return layers
