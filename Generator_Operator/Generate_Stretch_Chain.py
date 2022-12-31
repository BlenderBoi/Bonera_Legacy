import bpy
import mathutils
import numpy
from Bonera_Toolkit import Utility_Functions

import math


def get_center(points):
    if len(points) == 0:
        return [0,0,0]

    lp_x = []
    lp_y = []
    lp_z = []

    for point in points:
        lp_x.append(point[0])
        lp_y.append(point[1])
        lp_z.append(point[2])

    lp_x = sum(lp_x) / len(points)
    lp_y = sum(lp_y) / len(points)
    lp_z = sum(lp_z) / len(points)

    center = [lp_x, lp_y, lp_z]

    return mathutils.Vector(center)

def altitude(A, B, V):

    a = B-A
    b = B-B
    v = B-V

#    a = A
#    b = B
#    v = V

    x1 = a[0]
    y1 = a[1]
    z1 = a[2]

    x2 = b[0]
    y2 = b[1]
    z2 = b[2]

    x3 = v[0]
    y3 = v[1]
    z3 = v[2]

    w = (((x1 - x2) * (x3 - x2)) + ((y1 - y2) * (y3 - y2)) + ((z1 - z2) * (z3 - z2))) / (pow((x1-x2), 2) + pow((y1-y2), 2) + pow((z1-z2), 2))

    x = x2 + (w * (x2 - x1))
    y = y2 + (w * (y2 - y1))
    z = z2 + (w * (z2 - z1))

    a = mathutils.Vector((x, y, z))

    return a + B

def align_bone_roll(self, context, bone1, bone2, target):

    remember_cursor = context.scene.cursor.location.xyz

    bpy.ops.armature.select_all(action='DESELECT')

    bone1.select = True
    bone2.select = True

    context.scene.cursor.location = target
    bpy.ops.armature.calculate_roll(type='CURSOR')

    bone1.roll += math.radians(-90)
    bone2.roll += math.radians(-90)

    context.scene.cursor.location = remember_cursor

def create_empty(location, name="empty"):

    empty = bpy.data.objects.new(name, None)
    empty.show_in_front = True
    bpy.context.collection.objects.link(empty)
    empty.location = location
    bpy.context.view_layer.update()
    return empty

def signed_angle(vector_u, vector_v, normal):
    # Normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle
    return angle

def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)

def get_midpoint(points):

    return mathutils.Vector(numpy.sum(points, axis=0)/len(points))


ENUM_Pole_Mode = [("SIMPLE","Simple","Simple"),("ADVANCED","Advanced","Advanced"), ("NONE","None","None")]

#Generate New or Use Existing
#Controller Non Deform


def ENUM_Prefix(self, context):
    preferences = Utility_Functions.get_addon_preferences()
    items = preferences.Bone_Prefix_List
    ENUM_Items = []
    ENUM_Items.append(("NONE", "None", "None"))
    for item in items:
        ENUM_Items.append((item.name, item.name, item.name))
    return ENUM_Items

def ENUM_Suffix(self, context):
    preferences = Utility_Functions.get_addon_preferences()
    items = preferences.Bone_Suffix_List
    ENUM_Items = []
    ENUM_Items.append(("NONE", "None", "None"))
    for item in items:
        ENUM_Items.append((item.name, item.name, item.name))
    return ENUM_Items

def ENUM_Pole_Tail_Offset_Mode(self, context):
    items = [("GLOBAL","Global Offset", "Global")]

    if self.POLE_Mode == "BEND":
        items.append(("BEND","Bend Offset","Bend"))

    if self.POLE_Mode == "ROLL":
        items.append(("ROLL","Roll Offset","Roll"))

    return items

# ENUM_Pole_Setup = [("NONE", "None", "None"), ("PARENT", "Parent Pole to Controller", "Parent"), ("ADVANCED", "Advanced Setup", "Advanced Setup")]
# ENUM_Pole_Tail_Offset_Mode = [("ROLL_OFFSET","Bone Offset","Bone Offset"), ("GLOBAL", "Global Offset", "Global Offset")]

# ENUM_Bone_Roll_Settings = [("NONE","None","None"),("ALIGN_BONE","Align Bone Roll","Align Bone Roll"),("POLE_ANGLE","Calculate Pole Angle (Broken)","Calculate Poll Angle"), ("BOTH", "Both", "Both")]
ENUM_Bone_Roll_Settings = [("NONE","None","None"),("ALIGN_BONE","Align Bone Roll","Align Bone Roll")]

ENUM_IK_Control_Bone_Mode = [("GENERATE","Generate Bone","Generate Bone"),("EXISTING","Use Existing Bone","Use Existing Bone"), ("CHILD_COPY", "Copy Child", "Copy of First Child as IK Control bone")]

ENUM_Pole_Mode = [("BEND","Bone Bending","Bone Bending"), ("ROLL","Bone Roll","Bone Roll")]


#Use Roll as Fallback

class BONERA_OT_Generate_Stretch_Chain(bpy.types.Operator):
    """Generate Stretch Chain
    Pose | Edit Armature"""
    bl_idname = "bonera.generate_stretch_chain"
    bl_label = "Generate Stretch Chain"
    bl_options = {'UNDO', "REGISTER"}

    TGT_Bone_Layer: bpy.props.IntProperty(default=2, max=32, min=1)
    Lock_Location: bpy.props.BoolProperty(default=True)
    Pre_Clear_Constraint: bpy.props.BoolProperty(default=False)
    TGT_Tail_Offset: bpy.props.FloatVectorProperty(default=(0,0,0.5))
    TGT_Prefix_Name: bpy.props.StringProperty(default="TGT_")

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            return True

    def draw(self, context):

        layout = self.layout
        layout.prop(self, "TGT_Prefix_Name", text="Target Bone Prefix")
        layout.prop(self, "TGT_Bone_Layer", text="Target Bone Layer")
        layout.prop(self, "Lock_Location", text="Lock Location")
        layout.prop(self, "Pre_Clear_Constraint", text="Pre Clear Constraint")
        layout.prop(self, "TGT_Tail_Offset", text="Tail Offset")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        mode = context.mode

        object = context.object

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = object.data.edit_bones


        selected_bones = [bone for bone in bones if bone.select]

        stretch_targets = []
        stretch_bones = []

        object.data.layers[self.TGT_Bone_Layer-1] = True

        for bone in selected_bones:

            stretch_target_name = self.TGT_Prefix_Name + bone.name
            stretch_target = bones.new(stretch_target_name)
            stretch_target.head = bone.head
            stretch_target.tail = bone.head


            stretch_target.tail = mathutils.Vector(stretch_target.tail) + mathutils.Vector(self.TGT_Tail_Offset)
            #
            bone.use_connect = False
            bone.parent = stretch_target

            stretch_target.layers = Utility_Functions.get_bone_layers(self.TGT_Bone_Layer-1)

            stretch_targets.append(stretch_target)
            stretch_bones.append(bone)

        constraint_pairs = []

        for stretch_bone in stretch_bones:

            for stretch_target in stretch_targets:

                if stretch_bone.tail == stretch_target.head:
                    constraint_pair = {"stretch_bone": stretch_bone.name, "stretch_target": stretch_target.name}
                    constraint_pairs.append(constraint_pair)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)


        for constraint_pair in constraint_pairs:

            stretch_bone = object.pose.bones.get(constraint_pair["stretch_bone"])
            stretch_target = object.pose.bones.get(constraint_pair["stretch_target"])

            if stretch_bone:
                if self.Lock_Location:
                    stretch_bone.lock_location[0] = True
                    stretch_bone.lock_location[1] = True
                    stretch_bone.lock_location[2] = True

                if self.Pre_Clear_Constraint:

                    for c in stretch_bone.constraints:
                        for constraint in stretch_bone.constraints:
                            stretch_bone.constraints.remove(constraint)
                            break

            if stretch_bone and stretch_target:

                constraint = stretch_bone.constraints.new("STRETCH_TO")
                constraint.target = object
                constraint.subtarget = stretch_target.name


        if mode == "POSE":
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        return {'FINISHED'}

classes = [BONERA_OT_Generate_Stretch_Chain]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
