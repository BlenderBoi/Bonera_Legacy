import bpy
from Bonera_Toolkit import Utility_Functions


class BONERA_Convert_Curve_To_Bone(bpy.types.Operator):
    """Convert Curve to Bone
    Object Mode Only"""
    bl_idname = "bonera.convert_curve_to_bone"
    bl_label = "Convert Curve To Bone (Experimental)"
    bl_options = {'REGISTER', 'UNDO'}

    set_resolution: bpy.props.BoolProperty(default=False)
    resolution: bpy.props.IntProperty(default=3, min=0, soft_max=15)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "set_resolution", text="Set Resolution")
        if self.set_resolution:
            layout.prop(self, "resolution", text="Resolution")


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    @classmethod
    def poll(cls, context):

        selected_objects = []

        if context.mode in ["OBJECT"]:
            selected_objects = [object for object in context.selected_objects if object.type == "CURVE"]


        if len(selected_objects) > 0:
            return True

    def execute(self, context):

        selected_objects = []
        mode = context.mode

        if context.mode in ["OBJECT"]:
            selected_objects = [object for object in context.selected_objects if object.type == "CURVE"]

        for object in selected_objects:

            bpy.ops.object.select_all(action='DESELECT')

            resolution = None

            if self.set_resolution:
                resolution = self.resolution
            else:
                resolution = None

            MESH_object = Utility_Functions.curve_to_mesh(object, resolution)

            MESH_object.modifiers.new(type="SKIN", name="Skin")

            MESH_object.select_set(True)
            context.view_layer.objects.active = MESH_object

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.skin_root_mark()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            bpy.ops.object.skin_armature_create(modifier="Skin")

            bpy.data.objects.remove(MESH_object)

            armature = context.view_layer.objects[-1]
            armature.data.display_type = "OCTAHEDRAL"
        return {'FINISHED'}






classes = [BONERA_Convert_Curve_To_Bone]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
