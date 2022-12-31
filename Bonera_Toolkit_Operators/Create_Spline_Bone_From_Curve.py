import bpy
from Bonera_Toolkit import Utility_Functions


# FUTURE
# Add Control Bones
# Add Bezier Handle Bones

def find_end_bone(self, count, bone):

    if len(bone.children) > 0:

        for child in bone.children:
            if len(child.children) == 0:
                self.end_bones.append((child, count))
            else:
                find_end_bone(self, count + 1, child)
    

def separate_loose_curve(context, object):

    curves = []

    if object:
        if object.type == "CURVE":
            context.view_layer.objects.active = object
            splines = object.data.splines


            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.curve.select_all(action='DESELECT')

            while len(splines) > 1:
                spline = splines[0]
                if spline.bezier_points:
                    spline.bezier_points[0].select_control_point = True
                elif spline.points:
                    spline.points[0].select = True
                bpy.ops.curve.select_linked()
                bpy.ops.curve.separate()
                
                context.view_layer.update() 

                separated_object = context.view_layer.objects[-1]
                curves.append(separated_object)
            
            curves.append(object)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    return curves



ENUM_Controller_Type = [("BONE","Bone","Bone"),("EMPTY","Empty","Empty")]

class BONERA_Create_Spline_Bones_From_Curve(bpy.types.Operator):
    """Create Spline Bones From Curve
    Object Mode Only"""
    bl_idname = "bonera.create_spline_bones_from_curve"
    bl_label = "Create Spline Bones From Curve (Experimental)"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(default="Bone")
    set_resolution: bpy.props.BoolProperty(default=False)
    resolution: bpy.props.IntProperty(default=3, min=0, soft_max=15)
    separate_loose_curves: bpy.props.BoolProperty(default=True)

    # controller_type: bpy.props.EnumProperty(items=ENUM_Controller_Type)
    # create_controller_handle: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "separate_loose_curves", text="Separate Loose Curves")
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

        curves = []

        if self.separate_loose_curves:
            for object in selected_objects:

                separated_curves = separate_loose_curve(context, object)

                for curve in separated_curves:
                    curves.append(curve)
        else:
            curves = selected_objects

        for object in curves:

            self.end_bones = []

            bpy.ops.object.select_all(action='DESELECT')

            resolution = None

            if self.set_resolution:
                resolution = self.resolution
            else:
                resolution = None


            # if object.data.splines[0].use_cyclic:

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
            context.view_layer.update() 

            root_bones = [bone for bone in armature.pose.bones if not bone.parent]         

            for rb in root_bones:
                find_end_bone(self, 2, rb)

            for bone_pair in self.end_bones:
                
                

                constraint = bone_pair[0].constraints.new("SPLINE_IK")
                constraint.chain_count = bone_pair[1]
                constraint.target = object

        return {'FINISHED'}






classes = [BONERA_Create_Spline_Bones_From_Curve]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
