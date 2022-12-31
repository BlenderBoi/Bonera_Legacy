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

# ENUM_Pole_Tail_Offset_Mode = [("ROLL_OFFSET","Bone Offset","Bone Offset"), ("GLOBAL", "Global Offset", "Global Offset")]

ENUM_Bone_Roll_Settings = [("NONE","None","None"),("ALIGN_BONE","Align Bone Roll","Align Bone Roll"),("POLE_ANGLE","Calculate Pole Angle","Calculate Poll Angle")]

ENUM_IK_Control_Bone_Mode = [("GENERATE","Generate Bone","Generate Bone"),("EXISTING","Use Existing Bone","Use Existing Bone"), ("CHILD_COPY", "Copy Child", "Copy of First Child as IK Control bone")]

ENUM_Pole_Mode = [("BEND","Bone Bending","Bone Bending"), ("ROLL","Bone Roll","Bone Roll")]


#Use Roll as Fallback

#Double Check Calculate Poll Angle

class BONERA_OT_Generate_IK(bpy.types.Operator):
    """Generate IK
    Pose | Edit Armature"""
    bl_idname = "bonera.generate_ik"
    bl_label = "Generate IK"
    bl_options = {'UNDO', "REGISTER"}

    Chain_Length: bpy.props.IntProperty(default=2, min=1, max=255)
    Pre_Clear_Constraint: bpy.props.BoolProperty(default=False)

    SHOW_Pole_Settings: bpy.props.BoolProperty(default=False)
    POLE_Generate: bpy.props.BoolProperty(default=True)
    # POLE_Setup: bpy.props.EnumProperty(items=ENUM_Pole_Setup)
    POLE_Parent: bpy.props.BoolProperty(default=False)
    POLE_Mode: bpy.props.EnumProperty(items=ENUM_Pole_Mode, default="BEND")

    POLE_Bone_Roll_Settings: bpy.props.EnumProperty(items=ENUM_Bone_Roll_Settings, default="ALIGN_BONE")
    POLE_Bone_Roll_Align_Chain: bpy.props.BoolProperty(default=True)

    POLE_Offset_Distance: bpy.props.FloatProperty(default=1, min=0.1)

    POLE_Tail_Offset_Mode: bpy.props.EnumProperty(items=ENUM_Pole_Tail_Offset_Mode)

    POLE_Global_Tail_Offset: bpy.props.FloatVectorProperty(default=(0, -0.1, 0))
    POLE_Roll_Tail_Offset: bpy.props.FloatVectorProperty(default=(0.1, 0, 0))
    POLE_Bend_Tail_Offset: bpy.props.FloatVectorProperty(default=(0, 0, 0.1))

    SHOW_IKCTRL_Settings: bpy.props.BoolProperty(default=False)
    IKCTRL_Bone_Mode: bpy.props.EnumProperty(items=ENUM_IK_Control_Bone_Mode)
    IKCTRL_Constraint_Child_Copy: bpy.props.BoolProperty(default=True)
    IKCTRL_Bone: bpy.props.StringProperty()
    IKCTRL_Tail_Offset: bpy.props.FloatVectorProperty(default=(0, 0.1, 0))



    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            return True

    def draw(self, context):

        layout = self.layout
        layout.prop(self, "Chain_Length", text="Chain Length")

        row = layout.row(align=True)

        row.prop(self, "POLE_Generate", text="Generate Pole")
        row.prop(self, "Pre_Clear_Constraint", text="Pre Clear Constraint")

        object = context.object



        if self.SHOW_IKCTRL_Settings:
            ICON_ARROW = "TRIA_DOWN"
        else:
            ICON_ARROW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_IKCTRL_Settings", text="Ik Controller Options", emboss=False, icon = ICON_ARROW)

        if self.SHOW_IKCTRL_Settings:

            col = layout.column(align=True)

            col.label(text="IK Controller")

            col.prop(self, "IKCTRL_Bone_Mode", text="")

            if self.IKCTRL_Bone_Mode == "CHILD_COPY":
                col.prop(self, "IKCTRL_Constraint_Child_Copy", text="Constraint Child Copy")

            if self.IKCTRL_Bone_Mode == "EXISTING":
                col.prop_search(self, "IKCTRL_Bone", object.data, "bones", text="")

            if self.IKCTRL_Bone_Mode == "GENERATE":
                row = col.row(align=True)
                row.prop(self, "IKCTRL_Tail_Offset", text="")

        if self.POLE_Generate:

            if self.SHOW_Pole_Settings:
                ICON_ARROW = "TRIA_DOWN"
            else:
                ICON_ARROW = "TRIA_RIGHT"

            row = layout.row(align=True)
            row.alignment = "LEFT"
            row.prop(self, "SHOW_Pole_Settings", text="Pole Controller Options", emboss=False, icon = ICON_ARROW)

            if self.SHOW_Pole_Settings:

                col = layout.column(align=True)

                row = col.row(align=True)
                row.prop(self, "POLE_Mode", expand=True)
                col.prop(self, "POLE_Offset_Distance", text="Offset Distance")

                # col = layout.column(align=True)
                # col.prop(self, "POLE_Parent", text="Parent Pole to IK Controller")

                layout.separator()

                if self.POLE_Mode == "BEND":
                    layout.label(text="Bone Roll and Orientation")
                    layout.prop(self, "POLE_Bone_Roll_Settings", text="")
                    if self.POLE_Bone_Roll_Settings == "ALIGN_BONE":
                        layout.prop(self, "POLE_Bone_Roll_Align_Chain", text="Align Whole Chain")
                layout.separator()

                col = layout.column(align=True)
                col.label(text="Pole Tail Offset")
                # col.prop(self, "POLE_Tail_Offset_Mode", text="")
                row = col.row(align=True)


                if self.POLE_Tail_Offset_Mode == "GLOBAL":
                    row.prop(self, "POLE_Global_Tail_Offset", text="")

                if self.POLE_Tail_Offset_Mode == "ROLL":
                    row.prop(self, "POLE_Roll_Tail_Offset", text="")

                if self.POLE_Tail_Offset_Mode == "BEND":
                    row.prop(self, "POLE_Bend_Tail_Offset", text="")



    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def set_ik_controller(self, context, object, active_bone):


        edit_bones = object.data.edit_bones

        preferences = Utility_Functions.get_addon_preferences()

        IK_Controller_Prefix = preferences.CTRL_IK_Suffix
        IK_Pole_Prefix = preferences.CTRL_Pole_Suffix

        IK_Controller_Bone = None

        if self.IKCTRL_Bone_Mode == "CHILD_COPY":

            if len(active_bone.children) > 0:

                IK_Controller_name = IK_Controller_Prefix + active_bone.name

                child = active_bone.children[0]

                IK_Controller_Bone = edit_bones.new(name=IK_Controller_name)
                IK_Controller_Bone.head = child.head
                IK_Controller_Bone.tail = child.tail
                IK_Controller_Bone.roll = child.roll
                IK_Controller_Bone.use_deform = False

                self.IK_Controller_Name = IK_Controller_Bone.name

            else:
                self.IKCTRL_Bone_Mode = "GENERATE"

        if self.IKCTRL_Bone_Mode == "EXISTING":

            IK_Controller_Bone = edit_bones.get(self.IKCTRL_Bone)

            if IK_Controller_Bone:
                self.IK_Controller_Name = IK_Controller_Bone.name
            else:
                self.IKCTRL_Bone_Mode = "GENERATE"

        if self.IKCTRL_Bone_Mode == "GENERATE":

            IK_Controller_name = IK_Controller_Prefix + active_bone.name

            IK_Controller_Bone = edit_bones.new(name=IK_Controller_name)
            IK_Controller_Bone.head = active_bone.tail
            IK_Controller_Bone.tail = IK_Controller_Bone.head + mathutils.Vector(self.IKCTRL_Tail_Offset)
            IK_Controller_Bone.use_deform = False


            self.IK_Controller_Name = IK_Controller_Bone.name

        return IK_Controller_Bone

    def execute(self, context):

        self.bone_chain = []
        self.Pole_Angle = None

        object = context.object
        mode = context.mode
        active_bone = context.active_bone




        preferences = Utility_Functions.get_addon_preferences()

        IK_Controller_Prefix = preferences.CTRL_IK_Suffix
        IK_Pole_Prefix = preferences.CTRL_Pole_Suffix

        cursor_location = bpy.context.scene.cursor.location.copy()

        if active_bone:

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            edit_bones = object.data.edit_bones

            active_bone = edit_bones.get(active_bone.name)

            IK_Controller_Bone = None
            IK_Pole_Bone = None

            self.IK_Controller_Name = None
            self.IK_Pole_Name = None
            self.IK_Name = active_bone.name


            IK_Controller_Bone = self.set_ik_controller(context, object, active_bone)

            if self.POLE_Generate:

                IK_Pole_Name = IK_Pole_Prefix + active_bone.name
                IK_Pole_Bone = edit_bones.new(name=IK_Pole_Name)
                self.IK_Pole_Name = IK_Pole_Bone.name

                bone_chain = Utility_Functions.Find_Chain_Root(self.Chain_Length, active_bone)

                Bone_Root = bone_chain[-1]
                Bone_Mid = bone_chain[-2]

                if Bone_Root and Bone_Mid:

                    up = Bone_Root.head
                    mid = Bone_Mid.head
                    down = Bone_Mid.tail

                    if self.POLE_Mode == "BEND" or self.Chain_Length != 1:

                        Altitude_Co = -altitude(up, down, mid)

                        Vec = mathutils.Vector(mid) + Altitude_Co
                        Mat = mathutils.Matrix.Translation(mid)

                        Vec.length = self.POLE_Offset_Distance

                        pole_head = Mat @ Vec
                        pole_tail = pole_head + mathutils.Vector(self.POLE_Global_Tail_Offset)

                    if self.POLE_Mode == "ROLL" or self.Chain_Length == 1:


                        Pole_Offset = mathutils.Vector((-self.POLE_Offset_Distance , 0, 0))

                        pole_offset_position_head = Bone_Root.matrix @ Pole_Offset
                        pole_vector_head = up - pole_offset_position_head
                        pole_matrix_head = mathutils.Matrix.Translation(pole_vector_head)

                        pole_head = pole_matrix_head @ up
                        pole_tail = pole_head + mathutils.Vector(self.POLE_Global_Tail_Offset)

                else:


                    Pole_Offset = mathutils.Vector((-self.POLE_Offset_Distance , 0, 0))
                    Pole_Offset_2 = mathutils.Vector((2 * -self.POLE_Offset_Distance , 0, 0))

                    pole_head_position = active_bone.matrix.to_translation()
                    pole_offset_position_head = active_bone.matrix @ Pole_Offset
                    pole_vector_head =   pole_head_position - pole_offset_position_head
                    pole_matrix_head = mathutils.Matrix.Translation(pole_vector_head)

                    pole_offset_position_tail = active_bone.matrix @ Pole_Offset_2
                    pole_vector_tail =   pole_head_position - pole_offset_position_tail
                    pole_matrix_tail = mathutils.Matrix.Translation(pole_vector_tail)

                    pole_head = pole_matrix_head @ active_bone.head
                    pole_tail = pole_head + mathutils.Vector(self.POLE_Global_Tail_Offset)

                IK_Pole_Bone.head = pole_head
                IK_Pole_Bone.tail = pole_tail
                IK_Pole_Bone.use_deform = False
                self.IK_Pole_Name = IK_Pole_Bone.name


                if self.POLE_Mode == "BEND":
                    if self.POLE_Generate:

                        if self.POLE_Bone_Roll_Settings == "POLE_ANGLE":
                                self.Pole_Angle = Utility_Functions.Get_Pole_Angle(object, Bone_Root, IK_Pole_Bone.head)


                        if self.POLE_Bone_Roll_Settings == "ALIGN_BONE":
                            if Bone_Root and Bone_Mid:

                                if self.POLE_Bone_Roll_Align_Chain:
                                    Utility_Functions.Align_Bones_Roll(object, bone_chain, IK_Pole_Bone.head)

                                else:
                                    Utility_Functions.Align_Bones_Roll(object, [Bone_Root], IK_Pole_Bone.head)

            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            pose_bones = object.pose.bones

            if self.IK_Controller_Name:

                IK_Controller_Bone = pose_bones.get(self.IK_Controller_Name)

                if self.IK_Pole_Name:
                    IK_Pole_Bone = pose_bones.get(self.IK_Pole_Name)
                else:
                    IK_Pole_Bone = None

                IK_Bone = pose_bones.get(self.IK_Name)


                if self.Pre_Clear_Constraint:

                    for c in IK_Bone.constraints:
                        for constraint in IK_Bone.constraints:
                            IK_Bone.constraints.remove(constraint)

                if self.IKCTRL_Bone_Mode == "CHILD_COPY":
                    if self.IKCTRL_Constraint_Child_Copy:

                        if len(IK_Bone.children) > 0:

                            child = IK_Bone.children[0]

                            constraint = child.constraints.new("COPY_TRANSFORMS")
                            constraint.target = object
                            constraint.subtarget = IK_Controller_Bone.name

                constraint = IK_Bone.constraints.new("IK")
                constraint.chain_count = self.Chain_Length
                constraint.target = object
                constraint.subtarget = IK_Controller_Bone.name

                if self.IK_Pole_Name:
                    constraint.pole_target = object
                    constraint.pole_subtarget = self.IK_Pole_Name

                if self.POLE_Bone_Roll_Settings == "POLE_ANGLE":

                    if self.Pole_Angle:
                        constraint.pole_angle = self.Pole_Angle
                        # Utility_Functions.Get_Pole_Angle(object, up_bone, pose_ik_pole_bone.head)
        bpy.context.scene.cursor.location = cursor_location

        return {'FINISHED'}

classes = [BONERA_OT_Generate_IK]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
