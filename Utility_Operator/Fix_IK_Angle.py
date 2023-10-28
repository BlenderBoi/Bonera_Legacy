import bpy
from .. import Utility_Functions
#Editing bone

ENUM_Fix_Mode = [("POLE_ANGLE", "Pole Angle", "Pole Angle"), ("ALIGN_BONE","Align Bone","Align Bone")]

class BONERA_Fix_IK_Angle(bpy.types.Operator):
    """Fix IK Angle
    Pose Mode Only"""
    bl_idname = "bonera.fix_ik_angle"
    bl_label = "Fix IK Angle"
    bl_options = {'REGISTER', 'UNDO'}

    Fix_Mode: bpy.props.EnumProperty(items=ENUM_Fix_Mode)
    Align_Whole_Chain: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Fix_Mode", expand=True)

        if self.Fix_Mode == "ALIGN_BONE":
            layout.prop(self, "Align_Whole_Chain", text="Align Whole Chain")


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    @classmethod
    def poll(cls, context):

        if context.mode in ["POSE"]:
            return True



    def execute(self, context):

        Active_Bone_Name = context.active_bone.name
        mode = context.mode
        object = context.object

        self.Pole_Bone_Name = None
        self.Pole_Target_Object = None
        self.Active_Bone_Name = None
        self.IK_Constraint = None

        if Active_Bone_Name:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            pose_bones = object.pose.bones
            Active_Bone = pose_bones.get(Active_Bone_Name)
            self.Active_Bone_Name = Active_Bone.name

            if Active_Bone:
                for constraint in Active_Bone.constraints:
                    if constraint.type == "IK":

                        self.IK_Constraint = constraint

                        pole_target_object = constraint.pole_target
                        if pole_target_object:
                            self.Pole_Target_Object = pole_target_object

                            if pole_target_object.type == "ARMATURE":
                                pole_bone_name = constraint.pole_subtarget
                                if pole_bone_name:
                                    pole_bone = pole_target_object.pose.bones.get(pole_bone_name)
                                    if pole_bone:
                                        self.Pole_Bone_Name = pole_bone.name

                        break

            if self.Pole_Target_Object:
                self.Pole_Target_Object.select_set(True)
                bpy.ops.object.mode_set(mode = 'EDIT')

                edit_bones = object.data.edit_bones

                if self.Active_Bone_Name:
                    Active_Bone = edit_bones.get(self.Active_Bone_Name)
                else:
                    Active_Bone = None

                target = None

                bone_chain = []

                if Active_Bone:
                    if self.IK_Constraint:
                        Chain_Length = self.IK_Constraint.chain_count

                        bone_chain = Utility_Functions.Find_Chain_Root(Chain_Length, Active_Bone)


                        if self.Pole_Target_Object:

                            target = self.Pole_Target_Object.matrix_world.to_translation()

                            if self.Pole_Bone_Name:

                                Pole_Bone = self.Pole_Target_Object.data.edit_bones.get(self.Pole_Bone_Name)
                                if Pole_Bone:
                                    target = self.Pole_Target_Object.matrix_world @ object.matrix_world.inverted() @ Pole_Bone.head


                                if target:
                                    if self.Fix_Mode == "ALIGN_BONE":
                                        bones = []

                                        if self.Align_Whole_Chain:
                                            bones = bone_chain
                                        else:
                                            if len(bone_chain) > 0:
                                                bones = [bone_chain[-1]]

                                        Utility_Functions.Align_Bones_Roll(object, bones, target)
                                        if self.IK_Constraint:
                                            self.IK_Constraint.pole_angle = 0
                                    if self.Fix_Mode == "POLE_ANGLE":

                                        if self.IK_Constraint:
                                            if len(bone_chain) > 0:
                                                bone = bone_chain[-1]
                                                self.IK_Constraint.pole_angle = Utility_Functions.Get_Pole_Angle(object, bone, target)

            if mode == "POSE":
                bpy.ops.object.mode_set(mode = 'POSE')

        return {'FINISHED'}




classes = [BONERA_Fix_IK_Angle]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
