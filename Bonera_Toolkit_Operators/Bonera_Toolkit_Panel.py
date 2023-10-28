import bpy
from .. import Utility_Functions

OPERATOR_POLL_CONTEXT = ["OBJECT","EDIT_MESH","EDIT_CURVE","EDIT_ARMATURE", "POSE"]


class BONERA_PT_Bonera_Toolkit_Panel(bpy.types.Panel):
    """Bonera Toolkit"""
    bl_label = "Bonera Toolkit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bonera"


    @classmethod
    def poll(cls, context):
        preferences = Utility_Functions.get_addon_preferences()

        if preferences.SECTION_Bonera_Toolkit:
            return True


    def draw(self, context):


        layout = self.layout





        layout.operator_context = "INVOKE_DEFAULT"








        if context.mode in OPERATOR_POLL_CONTEXT:


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


            layout.menu("POSE_MT_bonera_create_bone_menu", text="Bone Tools", icon="BONE_DATA")
            layout.menu("POSE_MT_bonera_generator_menu", text="Generator", icon="CONSTRAINT_BONE")
            layout.menu("POSE_MT_bonera_utility_menu", text="Utility", icon="TOOL_SETTINGS")
            layout.menu("POSE_MT_bonera_drivers_tools_menu", text="Drivers Tool", icon="DRIVER")
            layout.menu("POSE_MT_bonera_cleanup_menu", text="Clean Up", icon="BRUSH_DATA")



        if context.mode == "PAINT_WEIGHT":
            layout.operator("bonera.smooth_all_weights", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")

            # operator = layout.operator("object.vertex_group_smooth", text="Smooth All Weights", icon="MOD_VERTEX_WEIGHT")
            # operator.group_select_mode = "ALL"

        preferences = Utility_Functions.get_addon_preferences()

        if not preferences.DISABLE_Bonadd:
            layout.separator()
            layout.operator("bonera.bonadd", text="Bonadd", icon="EXPERIMENTAL")




        obj = context.object

        if obj:
            if obj.type == "ARMATURE":
                box = layout.box()
                if Utility_Functions.draw_subpanel(preferences, preferences.show_display_settings, "show_display_settings", "Display Settings", box):


                    box.label(text=obj.name, icon="ARMATURE_DATA")
                    box.label(text="Display As")
                    box.prop(obj.data, "display_type", text="")
                    box.prop(obj.data, "show_names", text="Show Names")
                    box.prop(obj.data, "show_bone_custom_shapes", text="Custom Shapes")
                    box.prop(obj.data, "show_group_colors", text="Group Colors")
                    box.prop(obj, "show_in_front", text="In Front")
                    row = box.row()
                    row.prop(obj.data, "show_axes", text="Axes")
                    row.prop(obj.data, "axes_position", text="Position")





classes = [BONERA_PT_Bonera_Toolkit_Panel]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
