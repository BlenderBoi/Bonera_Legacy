import bpy

class BONERA_OT_Create_Empty_And_Copy_Transform_Bone(bpy.types.Operator):
    """Create Empty and Copy Transform At Bone"""
    bl_idname = "bonera.create_empty_and_copy_transform_at_bone"
    bl_label = "Create Empty and Copy Transform Bone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == "POSE"

    def execute(self, context):

        selected_pose_bones = context.selected_pose_bones

        for pose_bone in selected_pose_bones:

            Empty = bpy.data.objects.new(pose_bone.name + "_empty", None)
            bpy.context.collection.objects.link(Empty)
            Empty.matrix_world = pose_bone.matrix @ pose_bone.id_data.matrix_world

            constraint = pose_bone.constraints.new("COPY_TRANSFORMS")
            constraint.target = Empty

        return {'FINISHED'}



classes = [BONERA_OT_Create_Empty_And_Copy_Transform_Bone]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
