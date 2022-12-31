import bpy


ENUM_Scope = [("SELECTED","Selected","Selected"), ("ALL","All","All")]

class BONERA_Convert_Bendy_Bones_To_Bones(bpy.types.Operator):
    """Convert Bendy Bones to Regular Bones"""
    bl_idname = "bonera.convert_bendy_bones_to_bones"
    bl_label = "Convert Bendy Bones To Bones (Experimental)"
    bl_options = {'REGISTER', 'UNDO'}

    Scope: bpy.props.EnumProperty(items=ENUM_Scope)
    track_bone: bpy.props.BoolProperty(default=True)
    enable_stretch: bpy.props.BoolProperty(default=False)

    to_layer: bpy.props.IntProperty(default=31, max=31, min=0)
    move_to_layer: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout
        if context.mode in ["POSE", "EDIT_ARMATURE"]:
            layout.prop(self, "Scope", text="Scope")

        layout.prop(self, "track_bone", text="Use Track Bone")
        layout.prop(self, "enable_stretch", text="Enable Stretch")

        layout.prop(self, "move_to_layer", text="Move To Layer")

        if self.move_to_layer:
            layout.prop(self, "to_layer", text="Layer")

    @classmethod
    def poll(cls, context):
        if context.mode in ["OBJECT", "POSE"]:
            return True


    def invoke(self, context, event):
        if context.mode == "OBJECT":

            return context.window_manager.invoke_props_dialog(self)

        if context.mode in ["EDIT_ARMATURE" , "POSE"]:

            return context.window_manager.invoke_props_dialog(self)



    def execute(self, context):

        mode = context.mode

        selected_objects = []

        if mode == "OBJECT":
            selected_objects = [object for object in context.selected_objects if object.type == "ARMATURE"]
        if mode == "POSE":
            selected_objects = [object for object in context.view_layer.objects if object.mode == "POSE"]

        armature_check = False

        for object in context.selected_objects:
            if object.type == "ARMATURE":
                armature_check = True
                bpy.context.view_layer.objects.active = object

                if mode == "EDIT_ARMATURE":
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                if mode == "POSE":
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                break

        if armature_check:


            for object in selected_objects:

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

                if mode == "OBJECT":
                    Bones = object.data.edit_bones
                    Edit_Bones = object.data.edit_bones

                if mode in ["EDIT_ARMATURE", "POSE"]:

                    Edit_Bones = object.data.edit_bones

                    if mode == "EDIT_ARMATURE":
                        if self.Scope == "ALL":
                            Bones = [bone for bone in object.data.edit_bones]

                        if self.Scope == "SELECTED":
                            Bones = [bone for bone in object.data.edit_bones if bone.select]

                    if mode == "POSE":
                        if self.Scope == "ALL":
                            Bones = [object.data.edit_bones.get(bone.name) for bone in object.data.bones if object.data.edit_bones.get(bone.name)]

                        if self.Scope == "SELECTED":
                            Bones = [object.data.edit_bones.get(bone.name) for bone in object.data.bones if bone.select and object.data.edit_bones.get(bone.name)]

                Bone_Pairs = []

                for Bone in Bones:

                    if Bone.bbone_segments > 1:

                        PBone = object.pose.bones.get(Bone.name)

                        bbone_segment = Bone.bbone_segments
                        Bone_Matrix = Bone.matrix
                        BBone_Segment_Name = []
                        bbone_mats = []

                        for i in range(Bone.bbone_segments):

                            bbone_mats.append(Bone.matrix @ PBone.bbone_segment_matrix(i,rest=True))

                        for index, seg_mat in enumerate(bbone_mats):
                            Bone_Name = Bone.name + "_bbone_segment_" + str(index).zfill(2)
                            Segment_Bone = Edit_Bones.new(Bone_Name)
                            Segment_Bone.matrix = seg_mat
                            Segment_Bone.length = PBone.length / Bone.bbone_segments

                            if self.move_to_layer:

                                layers = [False for x in range(32)]
                                layers[self.to_layer] = True
                                Segment_Bone.layers = layers

                                object.data.layers[self.to_layer] = True

                            Segment_Bone.bbone_x = Bone.bbone_x * 2
                            Segment_Bone.bbone_z = Bone.bbone_z * 2

                            BBone_Segment_Name.append(Segment_Bone.name)

                        Bone_Pair = {"BendyBone": Bone.name, "Bones":BBone_Segment_Name}
                        Bone_Pairs.append(Bone_Pair)

                bpy.ops.object.mode_set(mode='POSE', toggle=False)

                for Bone_Pair in Bone_Pairs:
                    Convert_Bones = Bone_Pair["Bones"]
                    Bendy_Bone = object.pose.bones.get(Bone_Pair["BendyBone"])
                    Converted_Pose_Bones = [object.pose.bones.get(bone_name) for bone_name in Convert_Bones if object.pose.bones.get(bone_name)]

                    if Bendy_Bone and len(Converted_Pose_Bones) > 0:

                        for index, Converted_Pose_Bone in enumerate(Converted_Pose_Bones):


                            Constraint = Converted_Pose_Bone.constraints.new("ARMATURE")
                            Target = Constraint.targets.new()
                            Target.target = object
                            Target.subtarget = Bendy_Bone.name
                            if self.track_bone:
                                if len(Converted_Pose_Bones) > index+1:

                                    NextBone = Converted_Pose_Bones[index+1]

                                    Constraint = Converted_Pose_Bone.constraints.new("DAMPED_TRACK")
                                    Constraint.target = object
                                    Constraint.subtarget = NextBone.name
                                    # Constraint.track_axis = "TRACK_Y"
                                    # Constraint.up_axis = "UP_X"
                                else:
                                    use_first_child = True

                                    for c in Bendy_Bone.constraints:
                                        if c.type == "STRETCH_TO":
                                            if c.subtarget:
                                                Constraint = Converted_Pose_Bone.constraints.new("DAMPED_TRACK")
                                                Constraint.target = object
                                                Constraint.subtarget = c.subtarget
                                                # Constraint.track_axis = "TRACK_Y"
                                                # Constraint.up_axis = "UP_X"
                                                use_first_child = False
                                                break

                                    use_bendy_tail = True

                                    if use_first_child:

                                        for child in Bendy_Bone.children:
                                            if child.head == Bendy_Bone.tail:
                                                Constraint = Converted_Pose_Bone.constraints.new("DAMPED_TRACK")
                                                Constraint.target = object
                                                Constraint.subtarget = child.name
                                                use_bendy_tail = False
                                                # Constraint.track_axis = "TRACK_Y"
                                                # Constraint.up_axis = "UP_X"
                                                break

                                    if use_bendy_tail:
                                        Constraint = Converted_Pose_Bone.constraints.new("DAMPED_TRACK")
                                        Constraint.target = object
                                        Constraint.subtarget = Bendy_Bone.name
                                        Constraint.head_tail = 1

                            if not self.enable_stretch:
                                Constraint = Converted_Pose_Bone.constraints.new("LIMIT_SCALE")

                                Constraint.use_min_x = True
                                Constraint.use_min_y = True
                                Constraint.use_min_z = True
                                Constraint.use_max_x = True
                                Constraint.use_max_y = True
                                Constraint.use_max_z = True
                                Constraint.min_x = 1.0
                                Constraint.min_y = 1.0
                                Constraint.min_z = 1.0
                                Constraint.max_x = 1.0
                                Constraint.max_y = 1.0
                                Constraint.max_z = 1.0



            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)





            # if mode in ["EDIT_ARMATURE", "POSE"]:
            #
            #     if mode == "POSE":
            #         bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            #
            #     for object in context.selected_objects:
            #
            #         if object.type == "ARMATURE":
            #
            #             Bones = object.data.edit_bones
            #
            #             for Bone in Bones:
            #                 if self.Scope == "ALL":
            #                     Bone.parent = None
            #                 if self.Scope == "SELECTED":
            #                     if Bone.select:
            #                         Bone.parent = None
            if mode == "POSE":
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
            if mode == "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            if mode == "EDIT_ARMATURE":
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        context.view_layer.update()

        return {'FINISHED'}






classes = [BONERA_Convert_Bendy_Bones_To_Bones]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
