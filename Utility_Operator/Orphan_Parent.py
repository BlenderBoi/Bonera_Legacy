import bpy

OPERATOR_POLL_CONTEXT = ["OBJECT", "EDIT_ARMATURE"]
#BONE

ENUM_Limit = [("ALL" ,"All", "All"), ("SELECTED", "Selected", "Selected")]

class BONERA_Orphan_Parent(bpy.types.Operator):
    """Orphan Parent
    Object: Parent Selected / All Object with no parent to Active Object
    Edit Armature: Parent Selected / All Bone with no parent to Active Bone """
    bl_idname = "bonera.orphan_parent"
    bl_label = "Orphan Parent"
    bl_options = {'UNDO', 'REGISTER'}

    limit: bpy.props.EnumProperty(items=ENUM_Limit)

    @classmethod
    def poll(cls, context):
        if context.mode in OPERATOR_POLL_CONTEXT:
            return True


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "limit", text="Limit")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        mode = context.mode
        parent = context.object

        if mode == "OBJECT":

            if self.limit == "ALL":
                objects = context.view_layer.objects

            if self.limit == "SELECTED":
                objects = context.selected_objects

            for object in objects:
                if not object.parent:

                    if not object == parent:
                        mw = object.matrix_world.copy()
                        object.parent = parent
                        object.matrix_world = mw

        if mode == "EDIT_ARMATURE":

            object = context.object

            bones = object.data.edit_bones
            active_bone = object.data.edit_bones.active

            for bone in bones:
                if not bone == active_bone:
                    if not bone.parent:

                        if self.limit == "SELECTED":
                            if bone.select:
                                bone.parent = active_bone
                        if self.limit == "ALL":
                            bone.parent = active_bone



        return {'FINISHED'}

classes = [BONERA_Orphan_Parent]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
