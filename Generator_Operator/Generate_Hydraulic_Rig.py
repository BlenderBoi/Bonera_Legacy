import bpy
from mathutils import Vector, Matrix
from .. import Utility_Functions
#Select Two bone

ENUM_Type = [("TRACK_TO","Track To","Track To"), ("DAMPED_TRACK","Damped Track","Damped Track"), ("LOCKED_TRACK","Locked Track","Locked Track")]
ENUM_Lock_Axis = [("LOCK_X","Lock X","Lock X"),("LOCKED_Y","Lock Y","Lock Y"),("LOCKED_Z","Lock Z","Lock Z")]

class BONERA_OT_Generate_Hydraulic_Rig(bpy.types.Operator):
    """Generate Hydraulic Bones
    Pose | Edit Armature"""
    bl_idname = "bonera.generate_hydraulic_rig"
    bl_label = "Generate Hydraulic Rig"
    bl_options = {'UNDO'}

    A_Target_Name: bpy.props.StringProperty()
    A_Bone: bpy.props.StringProperty()

    B_Target_Name: bpy.props.StringProperty()
    B_Bone: bpy.props.StringProperty()

    Type: bpy.props.EnumProperty(items=ENUM_Type)
    Lock_Axis: bpy.props.EnumProperty(items=ENUM_Lock_Axis)
    Tail_Offset: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            return True

    def invoke(self, context, event):

        object = context.object
        active = object.data.bones.active

        preferences = Utility_Functions.get_addon_preferences()
        bones = object.data.bones

        if context.mode == "POSE":
            bones = object.data.bones
            active = object.data.bones.active
        if context.mode == "EDIT_ARMATURE":
            bones = object.data.edit_bones
            active = object.data.edit_bones.active

        for bone in bones:
            if bone.select:
                if not bone == active:
                    selected = bone.name

                    self.A_Bone = active.name
                    self.B_Bone = selected

                    self.A_Target_Name = preferences.CTRL_Hydraulic_Prefix + self.A_Bone
                    self.B_Target_Name = preferences.CTRL_Hydraulic_Prefix + self.B_Bone

                    break

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        object = context.object

        col = layout.column(align=True)

        col.label(text="Bone A")
        row = col.row(align=True)
        row.prop_search(self, "A_Bone", object.data, "bones", text="")
        row.prop(self, "A_Target_Name", text="")

        col.separator()
        col.separator()
        col.separator()

        col.label(text="Bone B")
        row = col.row(align=True)
        row.prop_search(self, "B_Bone", object.data, "bones", text="")
        row.prop(self, "B_Target_Name", text="")

        layout.prop(self, "Tail_Offset", text="Target Tail Offset")

        layout.prop(self, "Type", text="Type")

        if self.Type == "LOCKED_TRACK":
            layout.prop(self, "Lock_Axis", text="Lock Axis", expand=True)



    def execute(self, context):

        object = context.object

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        edit_bones = object.data.edit_bones

        Bone_A = edit_bones.get(self.A_Bone)
        Bone_B = edit_bones.get(self.B_Bone)

        Target_A = edit_bones.new(self.A_Target_Name)
        Target_A.head = Bone_A.head
        Target_A.tail = Bone_A.head

        Offset_Head = Bone_A.matrix @ Vector(self.Tail_Offset)
        Offset_Vector = Bone_A.head - Offset_Head
        Offset_Matrix = Matrix.Translation(Vector(Offset_Vector))

        Target_A.tail = Offset_Matrix @ Target_A.head

        # Target_A.tail.z += 0.3

        Offset_Head = Bone_B.matrix @ Vector(self.Tail_Offset)
        Offset_Vector = Bone_B.head - Offset_Head
        Offset_Matrix = Matrix.Translation(Vector(Offset_Vector))



        Target_B = edit_bones.new(self.B_Target_Name)
        Target_B.head = Bone_B.head
        Target_B.tail = Bone_B.head
        # Target_B.tail.z += 0.3

        Target_B.tail = Offset_Matrix @ Target_B.head

        Bone_A_Name = Bone_A.name
        Bone_B_Name = Bone_B.name
        Target_A_Name = Target_A.name
        Target_B_Name = Target_B.name

        Bone_A.parent = Target_A
        Bone_B.parent = Target_B

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        pose_bones = object.pose.bones

        Bone_A = pose_bones.get(Bone_A_Name)
        Bone_B = pose_bones.get(Bone_B_Name)
        Target_A = pose_bones.get(Target_A_Name)
        Target_B = pose_bones.get(Target_B_Name)

        Constraint = Bone_A.constraints.new(self.Type)
        Constraint.target = object
        Constraint.subtarget = Target_B.name

        if self.Type == "TRACK_TO":
            Constraint.track_axis = "TRACK_Y"
            Constraint.up_axis = "UP_Z"

        if self.Type == "LOCKED_TRACK":
            Constraint.lock_axis = self.Lock_Axis


        Constraint = Bone_B.constraints.new(self.Type)
        Constraint.target = object
        Constraint.subtarget = Target_A.name

        if self.Type == "TRACK_TO":
            Constraint.track_axis = "TRACK_Y"
            Constraint.up_axis = "UP_Z"

        if self.Type == "LOCKED_TRACK":
            Constraint.lock_axis = self.Lock_Axis


        return {'FINISHED'}


classes = [BONERA_OT_Generate_Hydraulic_Rig]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
