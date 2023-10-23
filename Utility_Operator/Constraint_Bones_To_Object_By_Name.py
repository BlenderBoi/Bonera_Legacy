
import bpy
from .. import Utility_Functions
import mathutils

ENUM_Check_Mode = [("EXACT","Exact","Exact"), ("INCLUDE","Include","Include")]

class BONERA_OP_Constraint_Bones_To_Object_By_Name(bpy.types.Operator):
    """Constraint Bones To Object By Name
    Object Only"""
    bl_idname = "bonera.constraint_bones_to_object_by_name"
    bl_label = "Constraint Bones To Object By Name"
    bl_options = {'REGISTER', 'UNDO'}

    check_mode: bpy.props.EnumProperty(items=ENUM_Check_Mode)
    disable_armature_modifier: bpy.props.BoolProperty(default=True)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "check_mode", expand=True)
        layout.prop(self, "disable_armature_modifier", text="Disable Armature Modifier")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):



        armature = context.object
        selected_objects = context.selected_objects
        mode = context.mode

        if armature is not None:

            if armature.type == "ARMATURE":

                bones = armature.pose.bones

                if self.check_mode == "EXACT":

                    for obj in selected_objects:

                        bone = bones.get(obj.name)

                        if bone is not None:

                            constraint = bone.constraints.new("COPY_TRANSFORMS")
                            constraint.target = obj

                            for modifier in obj.modifiers:
                                if modifier.type == "ARMATURE":
                                    modifier.show_viewport = False

                if self.check_mode == "INCLUDE":
                    for bone in bones:

                        for obj in selected_objects:
                            if obj.name in bone.name or bone.name in obj.name:

                                constraint = bone.constraints.new("COPY_TRANSFORMS")
                                constraint.target = obj

                                for modifier in obj.modifiers:
                                    if modifier.type == "ARMATURE":
                                        modifier.show_viewport = False
            else:
                self.report({"INFO"}, "Active Object Must Be Armature Object")



        return {'FINISHED'}






classes = [BONERA_OP_Constraint_Bones_To_Object_By_Name]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
