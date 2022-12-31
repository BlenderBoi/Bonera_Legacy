import bpy

constraint_type = [("TRANSFORM","Copy Transform","Copy Transform"),("LOTROT","Copy Location & Copy Rotation","Lot Rot"),("CHILD_OF","Child Of","Child Of")]

class BONERA_Constraint_To_Armature(bpy.types.Operator):
    """Constraint to Armature"""
    bl_idname = "bonera.cleanup_constraint_to_armature_name"
    bl_label = "Constraint to Armature (Name Based)"
    bl_options = {'UNDO', 'REGISTER'}

    Armature01: bpy.props.StringProperty()
    Armature02: bpy.props.StringProperty()

    Constraint_Type: bpy.props.EnumProperty(items=constraint_type)

    def invoke(self, context, event):

        if context.object.type == "ARMATURE":
            self.Armature01 = context.object.name

        for object in context.selected_objects:
            if object.type == "ARMATURE":
                if not object == context.object:
                    self.Armature02 = object.name
                    break

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout
        layout.prop_search(self, "Armature02", bpy.data, "objects", text="Armature From")
        layout.prop_search(self, "Armature01", bpy.data, "objects", text="Armature To")


        layout.prop(self, "Constraint_Type", text="Constraint Type")

    def execute(self, context):


        control_rig = bpy.data.objects.get(self.Armature01)
        deform_rig = bpy.data.objects.get(self.Armature02)

        if control_rig and deform_rig:
            if control_rig.type == "ARMATURE" and deform_rig.type == "ARMATURE":

                for bone in deform_rig.pose.bones:

                    if control_rig.data.bones.get(bone.name):

                        if self.Constraint_Type == "TRANSFORM":

                            constraint = bone.constraints.new("COPY_TRANSFORMS")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                        if self.Constraint_Type == "LOTROT":
                            constraint = bone.constraints.new("COPY_LOCATION")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                            constraint = bone.constraints.new("COPY_ROTATION")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                        if self.Constraint_Type == "CHILD_OF":
                            constraint = bone.constraints.new("CHILD_OF")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                    else:
                        self.report({"INFO"}, "Bone Not Found, Skipped " + bone.name)


        return {'FINISHED'}

class BONERA_Constraint_Selected_Bone_To_Armature(bpy.types.Operator):
    """Constraint Selected Bone to Armature
    Pose Only"""
    bl_idname = "bonera.cleanup_constraint_selected_bone_to_armature_name"
    bl_label = "Constraint Selected Bone to Armature (Name Based)"
    bl_options = {'UNDO', 'REGISTER'}

    Armature01: bpy.props.StringProperty()
    Constraint_Type: bpy.props.EnumProperty(items=constraint_type)
    Clear_Constraint: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if context.mode == "POSE":
            return True
        else:
            return False

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout

        layout.prop_search(self, "Armature01", bpy.data, "objects", text="Rig To")
        layout.prop(self, "Constraint_Type", text="Constraint Type")
        layout.prop(self, "Clear_Constraint", text="Clear Constraints")


    def execute(self, context):


        control_rig = bpy.data.objects.get(self.Armature01)
        deform_rig = bpy.context.object

        if control_rig and deform_rig:
            if control_rig.type == "ARMATURE" and deform_rig.type == "ARMATURE":


                Selected_Pose_Bone = context.selected_pose_bones

                for bone in Selected_Pose_Bone:

                    if self.Clear_Constraint:
                        for constraint in bone.constraints:
                            bone.constraints.remove(constraint)

                    if control_rig.data.bones.get(bone.name):

                        if self.Constraint_Type == "TRANSFORM":
                            constraint = bone.constraints.new("COPY_TRANSFORMS")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                        if self.Constraint_Type == "LOTROT":
                            constraint = bone.constraints.new("COPY_LOCATION")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                            constraint = bone.constraints.new("COPY_ROTATION")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name

                        if self.Constraint_Type == "CHILD_OF":
                            constraint = bone.constraints.new("CHILD_OF")
                            constraint.target = control_rig
                            constraint.subtarget = control_rig.data.bones.get(bone.name).name
                            
                    else:
                        self.report({"INFO"}, "Bone Not Found, Skipped " + bone.name)





        return {'FINISHED'}



classes = [BONERA_Constraint_To_Armature, BONERA_Constraint_Selected_Bone_To_Armature]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
