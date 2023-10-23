import bpy
from .. import Utility_Functions


ENUM_Constraint = [("TRACK_TO","Track To","Track To"),("STRETCH_TO","Stretch To","Stretch To")]

class BONERA_Create_Empties_From_Selected_Bones_And_Follow_Path(bpy.types.Operator):
    """Create Empties From Selected Bones And Follow Path (Experimental)
    Edit Armature | Pose"""
    bl_idname = "bonera.create_empties_from_selected_bones_and_follow_path"
    bl_label = "Create Empties And Follow Curve From Selected Bones (Experimental)"
    bl_options = {'REGISTER', 'UNDO'}

    Curve_Object: bpy.props.StringProperty()
    Disconnect_Bone: bpy.props.BoolProperty(default=True)
    Constraint: bpy.props.EnumProperty(items=ENUM_Constraint)

    def draw(self, context):
        scn = context.scene
        scn_data = scn.Bonera_Scene_Data

        layout = self.layout
        layout.prop(scn_data, "Curve_Picker" ,text="Curve Object")
        layout.prop(self, "Disconnect_Bone", text="Disconnect Bone")
        layout.prop(self, "Constraint", text="Constraint")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    @classmethod
    def poll(cls, context):

        if context.mode in ["EDIT_ARMATURE", "POSE"]:

            return True

    def execute(self, context):

        scn = context.scene

        scn_data = scn.Bonera_Scene_Data

        if scn_data.Curve_Picker:

            counter = 0
            if len(scn_data.Curve_Picker.data.splines) > 0:
                total_length =scn_data.Curve_Picker.data.splines[0].calc_length()
            else:
                total_length = 0


            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            for bone in context.selected_bones:

                if self.Disconnect_Bone:
                    bone.use_connect = False


            bpy.ops.object.mode_set(mode='POSE', toggle=False)


            for bone in context.selected_pose_bones:


                if counter == 0:
                    empty = Utility_Functions.Create_Empty("Start_Empty")
                    constraint = empty.constraints.new("FOLLOW_PATH")
                    constraint.use_curve_follow = True

                    constraint.target = scn_data.Curve_Picker
                    constraint.offset = 0
                    track_constraint = bone.constraints.new("COPY_LOCATION")
                    track_constraint.target = empty

                counter += bone.length * 100 / total_length
                empty = Utility_Functions.Create_Empty(bone.name)

                constraint = empty.constraints.new("FOLLOW_PATH")
                constraint.target = scn_data.Curve_Picker
                constraint.offset = -1 * counter

                constraint.use_curve_follow = True

                if self.Constraint == "TRACK_TO":
                    track_constraint = bone.constraints.new("TRACK_TO")
                    track_constraint.track_axis = "TRACK_Y"
                    track_constraint.up_axis = "UP_X"
                    track_constraint.target = empty

                if self.Constraint == "STRETCH_TO":
                    track_constraint = bone.constraints.new("STRETCH_TO")
                    track_constraint.target = empty

        return {'FINISHED'}






classes = [BONERA_Create_Empties_From_Selected_Bones_And_Follow_Path]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
