import bpy
from Bonera_Toolkit import Utility_Functions
#Editing bone

ENUM_Name_Mode = [("PREFIX","Prefix","Prefix"),("SUFFIX","Suffix","Suffix"),("REPLACE","Replace","Replace")]

class BONERA_Duplicate_And_Constraint(bpy.types.Operator):
    """Duplicate and Constraint Bones
    Object | Pose | Edit Armature"""
    bl_idname = "bonera.duplicate_and_constraint"
    bl_label = "Duplicate and Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    Name_Mode: bpy.props.EnumProperty(items=ENUM_Name_Mode)
    Name_01: bpy.props.StringProperty(default="DUPLICATE_")
    Name_02: bpy.props.StringProperty()

    Bone_Layer: bpy.props.IntProperty(min=1, max=32, default=2)

    Deform: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Name_Mode", text="Mode")

        if self.Name_Mode == "PREFIX":
            layout.prop(self, "Name_01", text="Prefix")
        if self.Name_Mode == "SUFFIX":
            layout.prop(self, "Name_01", text="Suffix")
        if self.Name_Mode == "REPLACE":
            layout.prop(self, "Name_01", text="Find")
            layout.prop(self, "Name_02", text="Replace")

        layout.prop(self, "Bone_Layer", text="Bone Layer")
        layout.prop(self, "Deform", text="Deform")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    @classmethod
    def poll(cls, context):
        return context.mode in ["EDIT_ARMATURE", "OBJECT", "POSE"]

    def execute(self, context):

        objects = []
        layers = [False for layer in range(32)]
        layers[self.Bone_Layer-1] = True

        mode = context.mode
        active_object = None

        if context.active_object:
            active_object = context.active_object


        if context.mode in ["OBJECT"]:
            objects = [object for object in context.selected_objects if object.type == "ARMATURE"]
            objects_name = [object.name for object in objects]
        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            objects = [object for object in context.objects_in_mode if object.type == "ARMATURE"]
            objects_name = [object.name for object in objects]

        if len(objects) > 0:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # for obj in context.view_layer.objects:
            #     obj.select_set(False)
            bpy.ops.object.select_all(action='DESELECT')


            for object in objects:
                object.data.layers[self.Bone_Layer-1] = True
                DUP_Object = object.copy()
                DUP_Armature = object.data.copy()
                DUP_Object.data = DUP_Armature
                context.collection.objects.link(DUP_Object)


                bpy.ops.object.select_all(action='DESELECT')
                DUP_Object.select_set(True)
                context.view_layer.objects.active = DUP_Object


                for bone in DUP_Object.pose.bones:

                    bone_name = bone.name

                    for a in bone.constraints:
                        for constraint in bone.constraints:
                            bone.constraints.remove(constraint)
                            break

                    if self.Name_Mode == "PREFIX":
                        bone.name = self.Name_01 + bone.name
                    if self.Name_Mode == "SUFFIX":
                        bone.name = bone.name + self.Name_01
                    if self.Name_Mode == "REPLACE":
                        bone.name = bone.name.replace(self.Name_01, self.Name_02)

                    constraint = bone.constraints.new("COPY_TRANSFORMS")
                    constraint.target = object
                    constraint.subtarget = bone_name

                    bone.bone.layers = layers
                    bone.bone.use_deform = self.Deform

                bpy.ops.object.mode_set(mode = 'EDIT')

                if mode in ["POSE", "EDIT_ARMATURE"]:
                    for edit_bone in DUP_Object.data.edit_bones:
                        if not edit_bone.select:
                            DUP_Object.data.edit_bones.remove(edit_bone)


                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                object.select_set(True)
                DUP_Object.select_set(True)
                context.view_layer.objects.active = object



                bpy.ops.object.join()
                bpy.ops.object.select_all(action='DESELECT')


            for object_name in objects_name:

                obj = context.view_layer.objects.get(object_name)


                if obj:
                    obj.select_set(True)
                    if active_object:
                        if obj.name == active_object:
                            context.view_layer.objects.active = obj

            if mode == "POSE":
                bpy.ops.object.mode_set(mode = 'POSE')
            if mode == "EDIT_ARMATURE":
                bpy.ops.object.mode_set(mode = 'EDIT')
            if mode == "OBJECT":
                bpy.ops.object.mode_set(mode = 'OBJECT')

        return {'FINISHED'}




classes = [BONERA_Duplicate_And_Constraint]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
