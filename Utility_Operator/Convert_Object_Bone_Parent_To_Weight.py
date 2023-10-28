import bpy
from .. import Utility_Functions

def Add_Weight_Object(object, bone_name):

    vertex_indices = [vertex.index for vertex in object.data.vertices]

    group = object.vertex_groups.new( name = bone_name )
    group.add( vertex_indices, 1.0, 'REPLACE' )

    return group

def create_armature_modifier(object, armature_object):

    if object.type == "MESH":
        create_armature = True

        for modifier in object.modifiers:
            if modifier.type == "ARMATURE":
                if modifier.object == armature_object:
                    create_armature = False
                    break

        if create_armature:
             modifier = object.modifiers.new(type="ARMATURE", name="Armature")
             modifier.object = armature_object

class BONERA_OT_Convert_Object_Bone_Parent_To_Weight(bpy.types.Operator):
    """Convert Object Bone Parent To Weight
    Object Only"""
    bl_idname = "bonera.convert_object_bone_parent_to_weight"
    bl_label = "Convert Object Bone Parent To Weight"
    bl_options = {'UNDO'}

    Add_Modifier: bpy.props.BoolProperty(default=True)
    # Generate_Bone: bpy.props.BoolProperty(default=True)
    Parent_To_Armature: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if context.mode == "OBJECT":
            return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Add_Modifier", text="Add Armature Modifier")
        layout.prop(self, "Parent_To_Armature", text="Parent To Armature")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        selected_objects = context.selected_objects


        for object in selected_objects:

            if object.type == "MESH":

                if object.parent:

                    if object.parent_type == "BONE":

                        mw = object.matrix_world.copy()

                        Parent = object.parent

                        object.matrix_world = mw

                        Bone = None

                        if object.parent_bone:

                            Bone = object.parent_bone

                            Group = Add_Weight_Object(object, Bone)

                            if self.Parent_To_Armature:
                                object.parent_type = "OBJECT"

                            if self.Add_Modifier:
                                # create_armature_modifier(object, object.parent)
                                Utility_Functions.Add_Armature_Modifier(object, object.parent, name="Armature")

        return {'FINISHED'}


classes = [BONERA_OT_Convert_Object_Bone_Parent_To_Weight]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
