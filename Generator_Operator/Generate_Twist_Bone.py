import bpy
from Bonera_Toolkit import Utility_Functions
#Editing bone

ENUM_Influence_Falloff = [("SUB","Subtraction","Subtraction"),("RD","Recursive Divide","Divide"),("DBC","Divide By Count","Divide By Count")]

class BONERA_Generate_Twist_Bone(bpy.types.Operator):
    """Generate Twist Bone
    Pose | Edit Armature"""
    bl_idname = "bonera.generate_twist_bone"
    bl_label = "Generate Twist Bone"
    bl_options = {'REGISTER', 'UNDO'}

    subdivide: bpy.props.IntProperty(default=3, min=2)

    influence_falloff: bpy.props.EnumProperty(items=ENUM_Influence_Falloff)

    ignore_last: bpy.props.BoolProperty(default=True)

    twist_ctrl_layer: bpy.props.IntProperty(min=1, max=32, default=1)
    deform_bone_layer: bpy.props.IntProperty(min=1, max=32, default=2)

    @classmethod
    def poll(cls, context):
        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "subdivide", text="Subdivide")
        layout.label(text="Influence Falloff")
        layout.prop(self, "influence_falloff", text="")
        layout.prop(self, "ignore_last", text="Set Last Twist Bone Influence to 0")
        layout.prop(self, "twist_ctrl_layer", text="Twist Control Layer")
        layout.prop(self, "deform_bone_layer", text="Deform Bone Layer")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        objects = [object for object in context.objects_in_mode]
        mode = context.mode

        for object in objects:

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            if object.type == "ARMATURE":

                edit_bones = object.data.edit_bones
                object.data.layers[self.twist_ctrl_layer-1] = True
                object.data.layers[self.deform_bone_layer-1] = True

                bone_sets = []

                for bone in edit_bones:
                    if bone.select:


                        child_target = None

                        if len(bone.children) > 0:

                            for child_bone in bone.children:
                                # if child_bone.use_connect:
                                child_target = child_bone
                                break

                        if child_target:

                            bone.use_deform = False

                            twist_bones = Utility_Functions.subdivide_bone(object, bone, self.subdivide)

                            for twist_bone in twist_bones:
                                twist_bone.parent = bone
                                twist_bone.use_deform = True
                                twist_bone.layers = Utility_Functions.get_bone_layers(self.deform_bone_layer-1)


                            master_twist_name = bone.name + "_Twist_Ctrl"
                            master_twist = edit_bones.new(master_twist_name)
                            master_twist.parent = bone
                            master_twist.head = bone.head
                            master_twist.tail = bone.tail
                            master_twist.roll = bone.roll
                            master_twist.length = bone.length / 2
                            master_twist.bbone_x = bone.bbone_x * 2
                            master_twist.bbone_z = bone.bbone_z * 2
                            master_twist.use_deform = False

                            master_twist.layers = Utility_Functions.get_bone_layers(self.twist_ctrl_layer-1)

                            master_twist.head += bone.vector/3
                            master_twist.tail += bone.vector/3

                            twist_bones_name = [twist_bone.name for twist_bone in twist_bones]
                            master_twist_name = master_twist.name

                            bone_set = {"twist_bones": twist_bones_name, "master_twist": master_twist_name, "bone": bone.name, "object": object, "child": child_target.name}
                            bone_sets.append(bone_set)

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                for bone_set in bone_sets:

                    twist_bones = bone_set["twist_bones"]
                    master_twist = object.pose.bones.get(bone_set["master_twist"])
                    bone = bone_set["bone"]
                    child_target = bone_set["child"]

                    object = bone_set["object"]

                    master_twist.lock_location[0] = True
                    master_twist.lock_location[1] = True
                    master_twist.lock_location[2] = True

                    master_twist.lock_rotation[0] = True
                    master_twist.lock_rotation[2] = True

                    constraint = master_twist.constraints.new("COPY_ROTATION")
                    constraint.target = object
                    constraint.subtarget = child_target
                    constraint.use_x = False
                    constraint.use_z = False
                    constraint.target_space = "LOCAL"
                    constraint.owner_space = "LOCAL"
                    constraint.mix_mode = "AFTER"
                    constraint.euler_order = "ZXY"

                    twist_bones.reverse()

                    for count, twist_bone in enumerate(twist_bones):

                        twist_bone = object.pose.bones.get(twist_bone)
                        constraint = twist_bone.constraints.new("COPY_ROTATION")
                        constraint.target = object
                        constraint.subtarget = master_twist.name
                        if self.influence_falloff == "RD":
                            influences = 1
                            for amt in range(count):
                                influences = influences / 2

                            constraint.influence = influences

                        if self.influence_falloff == "DBC":
                            constraint.influence = 1/(count+1)


                        if self.influence_falloff == "SUB":
                            constraint.influence = 1 - (count * (1/(len(twist_bones)-1)))

                        if self.ignore_last:
                            if count == len(twist_bones)-1:
                                constraint.influence = 0

        if mode == "POSE":
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)



        return {'FINISHED'}




classes = [BONERA_Generate_Twist_Bone]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
