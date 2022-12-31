import bpy
from Bonera_Toolkit import Utility_Functions
#Editing bone


class BONERA_Constraint_Toogle(bpy.types.Operator):
    """Toogle Constraint"""
    bl_idname = "bonera.toogle_constraint"
    bl_label = "Toogle Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    mute : bpy.props.BoolProperty()
    use_selected: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        if context.mode in ["OBJECT", "POSE"]:
            return True
        else:
            return False

    def execute(self, context):


        for object in context.selected_objects:

            if object.type == "ARMATURE":
                # object = context.object
                Pose_Bone = object.pose.bones

                for bone in Pose_Bone:
                    if self.use_selected:

                        if bone.bone.select:
                            for constraint in bone.constraints:
                                constraint.mute = self.mute

                    else:

                        for constraint in bone.constraints:
                            constraint.mute = self.mute


        return {'FINISHED'}



def draw_item(self, context):

    layout = self.layout
    row = layout.row(align=True)

    addon_preferences = Utility_Functions.get_addon_preferences()

    if addon_preferences.header_toogle_constraints:
        if context.mode == "POSE":

            operator = row.operator("bonera.toogle_constraint", text="Mute")
            operator.mute = True
            operator.use_selected = addon_preferences.constraint_toogle_use_selected

            operator = row.operator("bonera.toogle_constraint", text="Unmute")
            operator.mute = False
            operator.use_selected = addon_preferences.constraint_toogle_use_selected

            row.prop(addon_preferences, "constraint_toogle_use_selected", text="", icon="RESTRICT_SELECT_OFF")



classes = [BONERA_Constraint_Toogle]

def register():

    bpy.types.VIEW3D_HT_header.append(draw_item)

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    bpy.types.VIEW3D_HT_header.remove(draw_item)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
