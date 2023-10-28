import bpy
from .. import Utility_Functions


ENUM_Find = [("EXACT","Exact","Exact"),("INCLUDE","Include", "Include")]

class BONERA_OT_Parent_Object_to_Bone_By_Name(bpy.types.Operator):
    """Parent Object to Bone by Name
    Object Mode Only"""
    bl_idname = "bonera.parent_object_to_bone_by_name"
    bl_label = "Parent Object to Bone By Name"
    bl_options = {'UNDO', 'REGISTER'}

    Find: bpy.props.EnumProperty(items=ENUM_Find)
    Armature_object: bpy.props.StringProperty()

    Use_Weight_For_Mesh: bpy.props.BoolProperty(default=True)
    Armature_Modifier_Mesh: bpy.props.BoolProperty(default=True)
    Reparent_Armature: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "Armature_object", context.view_layer, "objects", text="Armature Object")
        layout.prop(self, "Find", text="Find")
        layout.prop(self, "Use_Weight_For_Mesh", text="Use Weight For Mesh")

        if self.Use_Weight_For_Mesh:
            layout.prop(self, "Armature_Modifier_Mesh", text="Armature Modifier to Mesh Object")
            if self.Armature_Modifier_Mesh:
                layout.prop(self, "Reparent_Armature", text="Reparent Mesh Object to Armature")

    def invoke(self, context, event):

        selected_objects = context.selected_objects

        for object in selected_objects:
            if object.type == "ARMATURE":
                self.Armature_object = object.name
                break


        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        mode = context.mode
        armature_object = context.view_layer.objects.get(self.Armature_object)
        selected_objects = context.selected_objects

        if armature_object:

            if armature_object.type == "ARMATURE":

                bones = armature_object.data.bones

                if armature_object:
                    if armature_object.type == "ARMATURE":
                        for object in selected_objects:

                            if not object == armature_object:

                                for bone in bones:
                                    if self.Find == "EXACT":
                                        if bone.name == object.name:

                                            if object.type == "MESH":
                                                if self.Use_Weight_For_Mesh:

                                                    indices = [vert.index for vert in object.data.vertices]
                                                    group = object.vertex_groups.new(name = bone.name)
                                                    group.add( indices, 1.0, 'REPLACE' )

                                                    if self.Armature_Modifier_Mesh:
                                                        # modifier = object.modifiers.new(name="Armature", type="ARMATURE")
                                                        # modifier.object = armature_object
                                                        Utility_Functions.Add_Armature_Modifier(object, armature_object, name="Armature")

                                                        if self.Reparent_Armature:

                                                            mw = object.matrix_world.copy()
                                                            object.parent = armature_object
                                                            # object.matrix_parent_inverse = armature_object.matrix_world.inverted()
                                                            object.matrix_world = mw

                                                else:
                                                    mw = object.matrix_world.copy()

                                                    object.parent = armature_object
                                                    object.parent_type = "BONE"
                                                    object.parent_bone = bone.name
                                                    object.matrix_world = mw
                                                    break

                                            else:

                                                mw = object.matrix_world.copy()

                                                object.parent = armature_object
                                                object.parent_type = "BONE"
                                                object.parent_bone = bone.name
                                                object.matrix_world = mw
                                                break



                                    if self.Find == "INCLUDE":
                                        if object.name in bone.name:

                                            if object.type == "MESH":
                                                if self.Use_Weight_For_Mesh:

                                                    indices = [vert.index for vert in object.data.vertices]
                                                    group = object.vertex_groups.new(name = bone.name)
                                                    group.add( indices, 1.0, 'REPLACE' )

                                                    if self.Armature_Modifier_Mesh:
                                                        # modifier = object.modifiers.new(name="Armature", type="ARMATURE")
                                                        # modifier.object = armature_object
                                                        Utility_Functions.Add_Armature_Modifier(object, armature_object, name="Armature")

                                                        if self.Reparent_Armature:

                                                            mw = object.matrix_world.copy()
                                                            object.parent = armature_object
                                                            object.matrix_world = mw

                                                else:
                                                    mw = object.matrix_world.copy()

                                                    object.parent = armature_object
                                                    object.parent_type = "BONE"
                                                    object.parent_bone = bone.name
                                                    object.matrix_world = mw
                                                    break

                                            else:

                                                mw = object.matrix_world.copy()

                                                object.parent = armature_object
                                                object.parent_type = "BONE"
                                                object.parent_bone = bone.name
                                                object.matrix_world = mw
                                                break

        return {'FINISHED'}

classes = [BONERA_OT_Parent_Object_to_Bone_By_Name]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
