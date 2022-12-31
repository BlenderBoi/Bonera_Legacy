import bpy
import math


class BONERA_OT_Create_Armature_From_Object_And_Bake_Object_Animation(bpy.types.Operator):
    """Generate Armature and Bake Object Animation"""
    bl_idname = "bonera.create_armature_from_object_and_bake_object_animation"
    bl_label = "Create Armature from Object and Bake Object Animation"
    bl_options = {'REGISTER', 'UNDO'}

    Bone_Base_Name: bpy.props.StringProperty(default="Bone")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Bone_Base_Name", text="Bone Base Name")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        if not context.object:
            if len(context.selected_objects) > 0:
                context.view_layer.objects.active = context.selected_objects[0]

        object = context.object
        if object:


            bpy.ops.bonera.create_bones_from_selected(Base_Name=self.Bone_Base_Name, SHOW_Weight_Option=False, BIND_Add_Armature_Modifier=True, BIND_Parent_Non_Mesh=False, BIND_Parent_To_Armature=False, SHOW_Tail=True, Tail_Mode='OFFSET_LOCAL', Tail_Offset_Amount=(0, 0.1, 0), SHOW_Armature=False, Use_Hierarchy=True)



            armature_object = None

            for object in context.view_layer.objects:
                if object.type == "ARMATURE":
                    armature_object = object
                    armature_object.select_set(True)
                    context.view_layer.objects.active = armature_object
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    for bone in object.data.edit_bones:
                        bone.roll = bone.roll + math.radians(180)
                        bone.length = 0.1
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    break

            selected_objects = [object for object in context.selected_objects if object.type == "MESH"]
            actions_range = []

            for object in selected_objects:
                if object.animation_data:
                    if object.animation_data.action:
                        actions_range.append(object.animation_data.action.frame_range[0])
                        actions_range.append(object.animation_data.action.frame_range[1])

            modifiers_toogle = []


            if armature_object:
                armature_action = bpy.data.actions.new("CopyAction")

                if not armature_object.animation_data:
                    armature_object.animation_data_create()

                armature_object.animation_data.action = armature_action

                if armature_object in selected_objects:
                    selected_objects.remove(armature_object)

                if armature_object.type == "ARMATURE":

                    for object in selected_objects:

                        for modifier in object.modifiers:

                            if modifier.type == "ARMATURE":

                                modifier.show_viewport = False
                                modifiers_toogle.append(modifier)

                    for bone in armature_object.pose.bones:
                        constraint = bone.constraints.new("COPY_TRANSFORMS")

#
                        for object in selected_objects:



                            if self.Bone_Base_Name + "_" + object.name == bone.name:
#                                bone.rotation_mode = object.rotation_mode
                                constraint.target = object

                        bone.bone.select = True


        bpy.ops.nla.bake(frame_start=min(actions_range), frame_end=max(actions_range), only_selected=False, visual_keying=True, clear_constraints=True, bake_types={'POSE'})
        context.view_layer.update()

#
        for object in selected_objects:
            if object.animation_data:
                if object.animation_data.action:
                    object.animation_data.action = None

        for obj in context.view_layer.objects:
            obj.select_set(False)


        copy_armature = armature_object.copy()
        copy_armature_data = armature_object.data.copy()
        bpy.context.collection.objects.link(copy_armature)

        copy_armature.animation_data.action = None

        copy_armature.select_set(True)

        for bone in copy_armature.pose.bones:
            constraint = bone.constraints.new("COPY_ROTATION")
            constraint.target = armature_object
            constraint.subtarget = bone.name
            constraint = bone.constraints.new("COPY_LOCATION")
            constraint.target = armature_object
            constraint.subtarget = bone.name
            bone.rotation_mode = "XYZ"
            bone.scale = (1, 1, 1)




        context.view_layer.objects.active = copy_armature

        bpy.ops.nla.bake(frame_start=min(actions_range), frame_end=max(actions_range), only_selected=False, visual_keying=True, clear_constraints=True, bake_types={'POSE'})

        for modifier in modifiers_toogle:
            modifier.object = copy_armature
            modifier.show_viewport = True


        bpy.data.objects.remove(armature_object)


        return {'FINISHED'}




def register():

    bpy.utils.register_class(BONERA_OT_Create_Armature_From_Object_And_Bake_Object_Animation)


def unregister():
    bpy.utils.unregister_class(BONERA_OT_Create_Armature_From_Object_And_Bake_Object_Animation)

if __name__ == "__main__":
    register()
