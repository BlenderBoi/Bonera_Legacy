import bpy
from . import Utility_Functions


OPERATOR_POLL_CONTEXT = ["OBJECT","EDIT_MESH","EDIT_CURVE","EDIT_ARMATURE", "POSE", "EDIT_LATTICE"]

class BONERA_MT_Bonera_Toolkit_Menu(bpy.types.Menu):
    bl_label = "Bonera Toolkit"
    bl_idname = "POSE_MT_bonera_toolkit_menu"

    @classmethod
    def poll(cls, context):
        if context.mode in OPERATOR_POLL_CONTEXT or context.mode == "PAINT_WEIGHT":
            return True

    def draw(self, context):

        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"

        if context.mode in OPERATOR_POLL_CONTEXT:

            # layout.operator("bonera.add_selected_objects_to_bone_shape_library")
            layout.operator("bonera.create_bones_from_selected", icon="BONE_DATA")
            layout.operator("bonera.create_empties_from_selected", icon="EMPTY_DATA")

            layout.separator()

            layout.operator("bonera.create_bone_chain_from_select_order", text="Bone Chain From Select Order (Experimental)", icon="BONE_DATA")



            Add_Bone_Shape_Label = "Add Bone Shape"

            if context.mode == "POSE":
                Add_Bone_Shape_Label = "Apply Bone Shape"

            layout.operator("bonera.add_bone_shape", text=Add_Bone_Shape_Label, icon="CUBE")

            if context.mode == "POSE":
                layout.operator("bonera.mirror_bone_shape", text="Mirror Bone Shape", icon="MOD_MIRROR")


            layout.separator()
            layout.menu("POSE_MT_bonera_create_bone_menu", text="Bone Tools", icon="BONE_DATA")
            layout.menu("POSE_MT_bonera_generator_menu", text="Generator", icon="CONSTRAINT_BONE")
            layout.menu("POSE_MT_bonera_utility_menu", text="Utility", icon="TOOL_SETTINGS")
            layout.menu("POSE_MT_bonera_drivers_tools_menu", text="Drivers Tool", icon="DRIVER")
            layout.menu("POSE_MT_bonera_cleanup_menu", text="Clean Up", icon="BRUSH_DATA")

        if context.mode == "PAINT_WEIGHT":
            # layout.operator("bonera.smooth_all_weights", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")
            operator = layout.operator("object.vertex_group_smooth", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")
            operator.group_select_mode = "ALL"


        preferences = Utility_Functions.get_addon_preferences()

        if not preferences.DISABLE_Bonadd:
            layout.separator()
            layout.operator("bonera.bonadd", text="Bonadd", icon="EXPERIMENTAL")

            # if context.mode == "POSE":
            #     layout.separator()
            #     layout.label(text="Utility")
            #     layout.operator("bonad.cleanup_constraint_selected_bone_to_armature_name", text="Constraint Selected to Armature", icon="CONSTRAINT_BONE")
            #

            # if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            #     layout.separator()
            #     layout.label(text="Generator")
            #     layout.operator("bonad.generate_ik", icon="CON_KINEMATIC")
            #     layout.operator("bonad.generate_hydraulic_rig", text="Generate Hydraulic", icon="CONSTRAINT_BONE")
            #
            # if context.mode == "OBJECT":
            #     layout.separator()
            #     layout.label(text="Generator")
            #     layout.operator("bonad.generate_driver_bone", text="Generate Driver Bone", icon="DRIVER")


class BONERA_MT_Bonera_Create_Bone_Menu(bpy.types.Menu):
    bl_label = "Bonera Create Bone Menu"
    bl_idname = "POSE_MT_bonera_create_bone_menu"

    def draw(self, context):

        if context.mode in OPERATOR_POLL_CONTEXT:

            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            layout.operator("bonera.create_bone_chain_from_object_hierarchy", text="Bone Chain From Object Hierarchy", icon="OUTLINER")
            layout.operator("bonera.create_bone_chain_from_curve", text="Bone Chain From Curve", icon="CURVE_DATA")


            layout.separator()
            layout.operator("bonera.create_bone_from_vertex_group", text="Bone From Vertex Group", icon="GROUP_VERTEX")

class BONERA_MT_Bonera_Generator_Menu(bpy.types.Menu):
    bl_label = "Bonera Generator Menu"
    bl_idname = "POSE_MT_bonera_generator_menu"

    def draw(self, context):

        if context.mode in OPERATOR_POLL_CONTEXT:

            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            layout.separator()
            layout.operator("bonera.generate_ik", icon="CON_KINEMATIC")
            layout.operator("bonera.generate_stretch_chain", text="Generate Stretch Chain", icon="CONSTRAINT_BONE")

            layout.separator()
            layout.operator("bonera.generate_eyelid", text="Generate Eyelid", icon="CONSTRAINT_BONE")
            layout.operator("bonera.generate_twist_bone", text="Generate Twist Bone", icon="CONSTRAINT_BONE")

            layout.separator()
            layout.operator("bonera.generate_hydraulic_rig", text="Generate Hydraulic", icon="CONSTRAINT_BONE")
            layout.operator("bonera.generate_basic_joint", text="Generate Basic Mechanical Joint", icon="CONSTRAINT_BONE")




class BONERA_MT_Bonera_Utility_Menu(bpy.types.Menu):
    bl_label = "Bonera Utility Menu"
    bl_idname = "POSE_MT_bonera_utility_menu"

    def draw(self, context):

        if context.mode in OPERATOR_POLL_CONTEXT:

            addon_preferences = Utility_Functions.get_addon_preferences()

            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"



            layout.separator()

            layout.row(align=True)
            operator = layout.operator("bonera.toogle_constraint", text="Mute Constraints", icon="CONSTRAINT_BONE")
            operator.mute = True
            operator.use_selected = True

            operator = layout.operator("bonera.toogle_constraint", text="Unmute Constraints", icon="CONSTRAINT_BONE")
            operator.mute = False
            operator.use_selected = True

            layout.prop(addon_preferences, "constraint_toogle_use_selected", text="Mute / Unmute Selected Only", icon="RESTRICT_SELECT_OFF")


            layout.separator()
            layout.operator("bonera.align_parent_to_child", text="Align Parent To Child", icon="BONE_DATA")
            layout.operator("bonera.orphan_parent", text="Orphan Parent", icon="CON_CHILDOF")
            layout.operator("bonera.parent_object_to_bone_by_name", text="Parent Object to Bone by Name", icon="CON_CHILDOF")
            layout.separator()
            layout.operator("bonera.convert_object_bone_parent_to_weight", text="Convert Object Bone Parent to Weight", icon="MOD_ARMATURE")
            # operator = layout.operator("object.vertex_group_smooth", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")
            # operator.group_select_mode = "ALL"
            # layout.operator("bonera.smooth_all_weights", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")

            operator = layout.operator("object.vertex_group_smooth", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")
            operator.group_select_mode = "ALL"

            layout.operator("bonera.weight_object", text="Weight Object", icon="MOD_ARMATURE")
            # layout.operator("bonera.add_object_vertex_group", text="Create Vertex Group from Object", icon="GROUP_VERTEX")

            layout.separator()
            layout.operator("bonera.create_empties_from_selected_bones_and_follow_path", text="Create Empties From Selected Bones and Follow Path (Experimental)", icon="OUTLINER_DATA_CURVE")
            layout.operator("bonera.convert_curve_to_bone", text="Convert Curve To Bone (Experimental)", icon="OUTLINER_DATA_CURVE")
            layout.operator("bonera.create_spline_bones_from_curve", text="Create Spline Bone From Curve (Experimental)", icon="CON_SPLINEIK")
            layout.operator("bonera.convert_bendy_bones_to_bones", text="Convert Bendy Bones to Bones (Experimental)", icon="BONE_DATA")
            layout.separator()


            layout.operator("bonera.constraint_bones_to_object_by_name", text="Constraint Bones To Object By Name", icon="CONSTRAINT_BONE")


            layout.separator()
            layout.operator("bonera.fix_ik_angle", text="Fix IK Angle", icon="DRIVER_ROTATIONAL_DIFFERENCE")




            if context.mode == "POSE":

                layout.operator("bonera.create_empty_and_copy_transform_at_bone", text="Create Empty and Copy Transform Bone", icon="CONSTRAINT_BONE")




            layout.separator()
            layout.operator("bonera.duplicate_and_constraint", text="Duplicate And Constraint", icon="DUPLICATE")

            if context.mode == "POSE":


                layout.operator("bonera.cleanup_constraint_selected_bone_to_armature_name", text="Constraint Selected Bone to Armature", icon="CONSTRAINT_BONE")

            if context.mode == "OBJECT":


                layout.operator("bonera.cleanup_constraint_to_armature_name", text="Constraint to Armature", icon="CONSTRAINT_BONE")

                layout.operator("bonera.move_object_to_bone_by_name", text="Move Object To Bone By Name", icon="ORIENTATION_LOCAL")
                layout.operator("bonera.join_and_parent_selected_bone_by_armature_name", text="Join And Parent Selected Bone By Armature Name", icon="CON_CHILDOF")


            if context.mode in ["OBJECT", "POSE", "EDIT_ARMATURE"]:
                layout.operator("bonera.proximity_parent", text="Parent By Distance", icon="CON_CHILDOF")



class BONERA_MT_Bonera_Cleanup_Menu(bpy.types.Menu):
    bl_label = "Bonera Cleanup Menu"
    bl_idname = "POSE_MT_bonera_cleanup_menu"

    def draw(self, context):

        if context.mode in OPERATOR_POLL_CONTEXT:

            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            layout.separator()
            layout.operator("bonera.cleanup_remove_custom_property", text="Remove Custom property", icon="BRUSH_DATA")
            layout.operator("bonera.cleanup_remove_animation_data", text="Remove Animation Data", icon="BRUSH_DATA")
            layout.operator("bonera.cleanup_remove_non_deform_bone", text="Remove Non Deform Bone", icon="BRUSH_DATA")
            layout.operator("bonera.cleanup_remove_bone_shape", text="Remove Bone Shape", icon="BRUSH_DATA")



class BONERA_MT_Bonera_Driver_Tools_Menu(bpy.types.Menu):
    bl_label = "Bonera Drivers Tools Menu"
    bl_idname = "POSE_MT_bonera_drivers_tools_menu"

    def draw(self, context):

        if context.mode in OPERATOR_POLL_CONTEXT:

            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            layout.operator("bonera.create_single_driver_bone", text="Add Single Driver Bone", icon="DRIVER")
            layout.operator("bonera.generate_driver_bone", text="Generate Driver Bones", icon="DRIVER")













classes = [BONERA_MT_Bonera_Driver_Tools_Menu, BONERA_MT_Bonera_Toolkit_Menu, BONERA_MT_Bonera_Generator_Menu, BONERA_MT_Bonera_Utility_Menu, BONERA_MT_Bonera_Create_Bone_Menu, BONERA_MT_Bonera_Cleanup_Menu]
addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name = "3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu", type="A", value="PRESS", shift=True, ctrl=True)
        kmi.properties.name = "POSE_MT_bonera_toolkit_menu"
        addon_keymaps.append([km, kmi])


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    addon_keymaps.clear()


if __name__ == "__main__":
    register()
