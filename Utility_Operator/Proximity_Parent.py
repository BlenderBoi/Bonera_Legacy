
import bpy
from Bonera_Toolkit import Utility_Functions

import mathutils


ENUM_Distance_Check = [("TAIL", "Tail", "Tail"), ("HEAD", "Head", "Head"), ("CENTER", "Center", "Center")]


class BONERA_Proximity_Parent(bpy.types.Operator):
    """Parent Bone Base on Distance"""
    bl_idname = "bonera.proximity_parent"
    bl_label = "Proximity Parent"
    bl_options = {'UNDO', 'REGISTER'}

    max_distance: bpy.props.FloatProperty(default=0, min=0)
    connect_bone: bpy.props.BoolProperty(default=False)
    only_zero_distance: bpy.props.BoolProperty(default=False)

    child_distance_check: bpy.props.EnumProperty(items=ENUM_Distance_Check, default="HEAD")
    parent_distance_check: bpy.props.EnumProperty(items=ENUM_Distance_Check, default="TAIL")

    selected_as_child: bpy.props.BoolProperty(default=True)
    selected_as_parent: bpy.props.BoolProperty(default=True)



    def draw(self, context):
        layout = self.layout
        layout.prop(self, "child_distance_check", text="Child")
        layout.prop(self, "parent_distance_check", text="Parent")
        layout.prop(self, "max_distance", text="Max Distance")
        layout.prop(self, "connect_bone", text="Connect Bone")
        if self.connect_bone:
            layout.prop(self, "only_zero_distance", text="Only Connect Zero Distance")

        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            layout.prop(self, "selected_as_child",text="Selected As Child")
            layout.prop(self, "selected_as_parent",text="Selected As Parent")


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        active_object = context.object
        current_mode = active_object.mode
        Utility_Functions.object_switch_mode(active_object, "EDIT")

        for armature in context.selected_objects:

            if armature.type == "ARMATURE":

                if current_mode in ["EDIT", "POSE"]:
                    if self.selected_as_child:
                        child_edit_bones = [bone for bone in armature.data.edit_bones if bone.select]
                    else:
                        child_edit_bones = [bone for bone in armature.data.edit_bones]

                    if self.selected_as_parent:
                        parent_edit_bones = [bone for bone in armature.data.edit_bones if bone.select]
                    else:
                        parent_edit_bones = [bone for bone in armature.data.edit_bones]

                else:
                    parent_edit_bones = [bone for bone in armature.data.edit_bones]
                    child_edit_bones = [bone for bone in armature.data.edit_bones]


                for bone in child_edit_bones:

                    if bone.parent == None:

                        parents_candidate = {}

                        for check_bone in parent_edit_bones:

                            if not bone == check_bone:
                                child_source = bone.head
                                parent_source = check_bone.tail

                                if self.child_distance_check == "TAIL":
                                    child_source = bone.tail
                                if self.child_distance_check == "HEAD":
                                    child_source = bone.head
                                if self.child_distance_check == "CENTER":
                                    child_source = (bone.head + bone.tail)/2

                                if self.parent_distance_check == "TAIL":
                                    parent_source = check_bone.tail
                                if self.parent_distance_check == "HEAD":
                                    parent_source = check_bone.head
                                if self.parent_distance_check == "CENTER":
                                    parent_source = (check_bone.head + check_bone.tail)/2

                                distance = mathutils.Vector(child_source - parent_source).length


                                if self.max_distance >= distance:

                                    parents_candidate[check_bone] = distance

                        if len(parents_candidate) > 0:

                            closest_bone = min(parents_candidate, key=parents_candidate.get)

                            if closest_bone:
                                distance = parents_candidate.get(closest_bone)
                                bone.parent = closest_bone

                                if self.connect_bone:
                                    if self.only_zero_distance:
                                        if distance == 0:
                                            bone.use_connect = True
                                    else:
                                        bone.use_connect = True





        
        Utility_Functions.object_switch_mode(armature, current_mode)

        Utility_Functions.update_UI()
        return {'FINISHED'}


classes = [BONERA_Proximity_Parent]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
