import bpy


def smooth_all_weights(obj, normalize):

    vertex_groups = obj.vertex_groups

    mode = obj.mode
    initial_index  = vertex_groups.active_index

    bpy.ops.object.mode_set(mode='WEIGHT_PAINT', toggle=False)



    for index, vertexgroup in enumerate(vertex_groups):
        vertex_groups.active_index = index
        bpy.ops.object.vertex_group_smooth()




    if normalize:
        bpy.ops.object.vertex_group_normalize_all()

    bpy.ops.object.mode_set(mode=mode, toggle=False)
    vertex_groups.active_index = initial_index



#BONE

#Iteration

ENUM_Limit = [("ALL" ,"All", "All"), ("SELECTED", "Selected", "Selected")]

class BONERA_Smooth_All_Weights(bpy.types.Operator):
    """Smooth All Weight
    Object | Weight Paint | Edit Mesh"""
    bl_idname = "bonera.smooth_all_weights"
    bl_label = "Smooth All Weights"
    bl_options = {'UNDO', 'REGISTER'}

    Normalized: bpy.props.BoolProperty(default=False)
    Iteration: bpy.props.IntProperty(default=1)

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Normalized", text="Normalized")
        layout.prop(self, "Iteration", text="Iteration")

    def execute(self, context):


        object = context.object
        if object.type == "MESH":

            for a in range(self.Iteration):

                smooth_all_weights(object, self.Normalized)



        return {'FINISHED'}

classes = [BONERA_Smooth_All_Weights]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
