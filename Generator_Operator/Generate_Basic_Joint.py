import bpy
from Bonera_Toolkit import Utility_Functions
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

class BONERA_OT_Generate_Basic_Joint_Rig(bpy.types.Operator):
    """Generate Basic Joint
    Pose | Edit Armature"""
    bl_idname = "bonera.generate_basic_joint"
    bl_label = "Generate Hinge Joint"
    bl_options = {'UNDO'}

    Joint_Type: bpy.props.EnumProperty(items=ENUM_Joint_Type)
    Use_Transform_Limit: bpy.props.BoolProperty(default=True)

    Hinge_Axis: bpy.props.EnumProperty(items=ENUM_Hinge_Axis)

    Hinge_Max: bpy.props.FloatProperty(subtype="ANGLE", default=math.radians(90), update=limit_hinge_max)
    Hinge_Min: bpy.props.FloatProperty(subtype="ANGLE", default=0, update=limit_hinge_min)
    Use_Limit_Angle: bpy.props.BoolProperty(default=False)

    Lock_Location: bpy.props.BoolProperty(default=False)
    Lock_Scale: bpy.props.BoolProperty(default=False)

    Space: bpy.props.EnumProperty(items=ENUM_Space)

    def draw(self, context):
        layout = self.layout

        object = context.object

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "Joint_Type", text="Joint Type")
        row = col.row(align=True)
        row.prop(self, "Space", text="Space")

        if self.Joint_Type == "HINGE":
            row = col.row()
            row.prop(self, "Hinge_Axis",expand=True)




            if self.Use_Limit_Angle:
                row = col.row(align=True)
                row.prop(self, "Hinge_Min", text="Limit Min")
                row.prop(self, "Hinge_Max", text="Limit Max")

            row = col.row(align=True)
            row.prop(self, "Use_Limit_Angle", text="Limit Angle")

        row = col.row(align=True)
        col.prop(self, "Use_Transform_Limit", text="Affect Transform")
        row = col.row(align=True)
        row.prop(self, "Lock_Location", text="Lock Location")
        row.prop(self, "Lock_Scale", text="Lock Scale")

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            return True

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)





    def execute(self, context):


        objects = [object for object in context.view_layer.objects if object.type == "ARMATURE" and object.mode in ["EDIT", "POSE"]]

        mode = context.mode

        for object in objects:

            if object.type == "ARMATURE":

                bpy.ops.object.mode_set(mode='POSE', toggle=False)

                preferences = Utility_Functions.get_addon_preferences()
                bones = object.data.bones


                for active_bone in object.pose.bones:
                    if active_bone.bone.select:
                        # active_bone = context.active_pose_bone
                        constraint = active_bone.constraints.new("LIMIT_ROTATION")
                        constraint.owner_space = self.Space
                        constraint.use_transform_limit = self.Use_Transform_Limit

                        if self.Joint_Type == "HINGE":

                            if self.Hinge_Axis == "X":
                                constraint.use_limit_x =False
                                constraint.use_limit_y =True
                                constraint.use_limit_z =True

                                if self.Use_Limit_Angle:
                                    constraint.use_limit_x = True
                                    constraint.max_x = self.Hinge_Max
                                    constraint.min_x = self.Hinge_Min

                            if self.Hinge_Axis == "Z":
                                constraint.use_limit_x =True
                                constraint.use_limit_y =True
                                constraint.use_limit_z =False

                                if self.Use_Limit_Angle:
                                    constraint.use_limit_z = True
                                    constraint.max_z = self.Hinge_Max
                                    constraint.min_z = self.Hinge_Min

                        if self.Joint_Type == "PIVOT":
                            constraint.use_limit_x =True
                            constraint.use_limit_y =False
                            constraint.use_limit_z =True

                            # if self.Use_Limit_Angle:
                            #     constraint.use_limit_y = True
                            #     constraint.max_y = self.Hinge_Max
                            #     constraint.min_y = self.Hinge_Min



                        if self.Lock_Location:
                            active_bone.lock_location[0] = True
                            active_bone.lock_location[1] = True
                            active_bone.lock_location[2] = True

                        if self.Lock_Scale:
                            active_bone.lock_scale[0] = True
                            active_bone.lock_scale[1] = True
                            active_bone.lock_scale[2] = True

        if mode == "POSE":
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        return {'FINISHED'}


classes = [BONERA_OT_Generate_Basic_Joint_Rig]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
