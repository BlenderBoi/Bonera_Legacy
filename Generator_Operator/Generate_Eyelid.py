import bpy
from .. import Utility_Functions
import math

ENUM_Joint_Type = [("HINGE","Hinge","Hinge"),("PIVOT","Pivot / Twist","Pivot / Twist")]
ENUM_Hinge_Axis = [("X","X","X"),("Z","Z","Z")]
ENUM_Space = [("LOCAL","Local","Local"),("WORLD","World","World")]

def limit_hinge_max(self, context):
    if self.limit_hinge_max <= self.limit_hinge_min:
        self.limit_hinge_max = self.limit_hinge_minx
        self.limit_hinge_max += 1
def limit_hinge_min(self, context):
    if self.limit_hinge_max <= self.limit_hinge_min:
        self.limit_hinge_min = self.limit_hinge_max
        self.limit_hinge_max -= 1

ENUM_Parent_Mode = [("NONE","None","None"),("EYE_PARENT","Eye Parent","Eye Parent"), ("BONE","Bone","Bone")]

class BONERA_OT_Generate_Eyelid(bpy.types.Operator):
    """Generate Eyelid
    Pose | Edit Armature"""
    bl_idname = "bonera.generate_eyelid"
    bl_label = "Generate Eyelid"
    bl_options = {'UNDO'}

    Control_Bone_Prefix: bpy.props.StringProperty(default="CTRL_")
    Control_Bone_Layer: bpy.props.IntProperty(min=1, max=32, default=1)

    Track_Bone_Prefix: bpy.props.StringProperty(default="TRACK_")
    Track_Bone_Layer: bpy.props.IntProperty(min=1, max=32, default=29)

    MCH_Bone_Prefix: bpy.props.StringProperty(default="MCH_")
    MCH_Bone_Layer: bpy.props.IntProperty(min=1, max=32, default=30)

    TGT_Bone_Prefix: bpy.props.StringProperty(default="TGT_")
    TGT_Bone_Layer: bpy.props.IntProperty(min=1, max=32, default=30)

    MCH_INT_Bone_Prefix: bpy.props.StringProperty(default="MCH_INT_")
    MCH_INT_Bone_Layer: bpy.props.IntProperty(min=1, max=32, default=30)

    Parent_Mode: bpy.props.EnumProperty(items=ENUM_Parent_Mode, default="EYE_PARENT")
    Parent_Bone: bpy.props.StringProperty()

    Influence: bpy.props.FloatProperty(default=0.15)

    SHOW_Name_And_Layers: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Influence", text="Influence")
        # layout.prop(self, "Advanced", text="Advanced")

        layout.prop(self, "Parent_Mode", text="Parent Mode")
        if self.Parent_Mode == "BONE":
            object = context.object
            if object:
                if object.type == "ARMATURE":
                    layout.prop_search(self, "Parent_Bone", object.data, "bones", text="Parent Bone")


        if Utility_Functions.draw_subpanel(self, self.SHOW_Name_And_Layers, "SHOW_Name_And_Layers", "Names And Layers Settings", layout):
            layout.label(text="Control Bone")
            layout.prop(self, "Control_Bone_Prefix", text="Prefix")
            layout.prop(self, "Control_Bone_Layer", text="Layer")
            layout.label(text="Track Bone")
            layout.prop(self, "Track_Bone_Prefix", text="Prefix")
            layout.prop(self, "Track_Bone_Layer", text="Layer")
            layout.label(text="MCH Bone")
            layout.prop(self, "MCH_Bone_Prefix", text="Prefix")
            layout.prop(self, "MCH_Bone_Layer", text="Layer")
            layout.label(text="TGT Bone")
            layout.prop(self, "TGT_Bone_Prefix", text="Prefix")
            layout.prop(self, "TGT_Bone_Layer", text="Layer")
            layout.label(text="MCH INT Bone")
            layout.prop(self, "MCH_INT_Bone_Prefix", text="Prefix")
            layout.prop(self, "MCH_INT_Bone_Layer", text="Layer")


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        mode = context.mode

        if mode == "POSE":
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        object = context.object

        object.data.layers[self.Control_Bone_Layer-1] = True
        object.data.layers[self.Track_Bone_Layer-1] = True
        object.data.layers[self.MCH_Bone_Layer-1] = True
        object.data.layers[self.TGT_Bone_Layer-1] = True
        object.data.layers[self.MCH_INT_Bone_Layer-1] = True

        bones = object.data.edit_bones

        selected_bones = [bone for bone in object.data.edit_bones if bone.select]

        active_bone = context.active_bone

        bone_sets = []

        if active_bone in selected_bones:
            selected_bones.remove(active_bone)

        Eyeball_Bone = object.data.edit_bones.get(active_bone.name)

        for bone in selected_bones:



            DEF_Bone = bone.name
            DEF_Bone = bone

            Control_Bone_Name = self.Control_Bone_Prefix + bone.name
            Control_Bone = bones.new(Control_Bone_Name)

            Control_Bone.head = bone.head
            Control_Bone.tail = bone.tail
            Control_Bone.roll = bone.roll
            Control_Bone.matrix = bone.matrix
            Control_Bone.length = Control_Bone.length * 1.25
            Control_Bone.use_deform = False

            Control_Bone.layers = Utility_Functions.get_bone_layers(self.Control_Bone_Layer-1)

            TRACK_Bone_Name = self.Track_Bone_Prefix + bone.name
            TRACK_Bone = bones.new(TRACK_Bone_Name)
            TRACK_Bone.head = active_bone.head
            TRACK_Bone.tail = bone.head
            TRACK_Bone.use_deform = False
            TRACK_Bone.parent = Eyeball_Bone

            TRACK_Bone.layers = Utility_Functions.get_bone_layers(self.Track_Bone_Layer-1)


            MCH_Bone_Name = self.MCH_Bone_Prefix + bone.name
            MCH_Bone = bones.new(MCH_Bone_Name)
            MCH_Bone.head = bone.head
            MCH_Bone.tail = bone.tail
            MCH_Bone.length = MCH_Bone.length / 3
            MCH_Bone.parent = Eyeball_Bone
            MCH_Bone.use_deform = False

            MCH_Bone.layers = Utility_Functions.get_bone_layers(self.MCH_Bone_Layer-1)


            TGT_Bone_Name = self.TGT_Bone_Prefix + bone.name
            TGT_Bone = bones.new(TGT_Bone_Name)
            TGT_Bone.head = bone.head
            TGT_Bone.tail = bone.tail
            TGT_Bone.length = TGT_Bone.length * 0.75
            TGT_Bone.parent = TRACK_Bone
            TGT_Bone.use_deform = False

            TGT_Bone.layers = Utility_Functions.get_bone_layers(self.TGT_Bone_Layer-1)



            MCH_Int_Bone_Name = self.MCH_INT_Bone_Prefix + bone.name
            MCH_Int_Bone = bones.new(MCH_Int_Bone_Name)
            MCH_Int_Bone.head = bone.head
            MCH_Int_Bone.tail = bone.tail
            MCH_Int_Bone.length = MCH_Int_Bone.length / 2
            MCH_Int_Bone.use_deform = False

            MCH_Int_Bone.layers = Utility_Functions.get_bone_layers(self.MCH_INT_Bone_Layer-1)


            if self.Parent_Mode == "BONE":
                if self.Parent_Bone:
                    parent_bone = bones.get(self.Parent_Bone)
                    if parent_bone:
                        MCH_Int_Bone.parent = parent_bone

            if self.Parent_Mode == "EYE_PARENT":
                MCH_Int_Bone.parent = Eyeball_Bone.parent




            Control_Bone.parent = MCH_Int_Bone


            bone_set = {"MCH": MCH_Bone.name, "MCH_Int": MCH_Int_Bone.name,"DEF": DEF_Bone.name, "CTRL": Control_Bone.name, "TGT": TGT_Bone.name, "TRACK": TRACK_Bone.name}
            bone_sets.append(bone_set)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        pose_bones = object.pose.bones

        for bone_set in bone_sets:
            CTRL_Bone = pose_bones.get(bone_set["CTRL"])
            MCH_Bone = pose_bones.get(bone_set["MCH"])
            MCH_Int_Bone = pose_bones.get(bone_set["MCH_Int"])
            DEF_Bone = pose_bones.get(bone_set["DEF"])
            TGT_Bone = pose_bones.get(bone_set["TGT"])
            TRACK_Bone = pose_bones.get(bone_set["TRACK"])

            if CTRL_Bone and MCH_Bone and DEF_Bone and TGT_Bone and MCH_Int_Bone and TRACK_Bone:

                Contraint = MCH_Int_Bone.constraints.new("COPY_TRANSFORMS")
                Contraint.target = object
                Contraint.subtarget = MCH_Bone.name
                Contraint.influence = self.Influence

                Contraint = TGT_Bone.constraints.new("COPY_ROTATION")
                Contraint.target = object
                Contraint.subtarget = CTRL_Bone.name

                Contraint = TGT_Bone.constraints.new("COPY_SCALE")
                Contraint.target = object
                Contraint.subtarget = CTRL_Bone.name

                Contraint = DEF_Bone.constraints.new("COPY_TRANSFORMS")
                Contraint.target = object
                Contraint.subtarget = TGT_Bone.name

                Contraint = TRACK_Bone.constraints.new("DAMPED_TRACK")
                Contraint.target = object
                Contraint.subtarget = CTRL_Bone.name




                # Contraint = DEF_Bone.constraints.new("COPY_LOCATION")
                # Contraint.target = object
                # Contraint.subtarget = CTRL_Bone.name



        return {'FINISHED'}


classes = [BONERA_OT_Generate_Eyelid]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
